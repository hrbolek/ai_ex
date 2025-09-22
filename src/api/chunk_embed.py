import asyncio
import os
import typing
import io
from abc import ABC, abstractmethod

from transformers import PreTrainedTokenizerBase

from fastapi import UploadFile
import numpy as np
import fitz  # PyMuPDF
import docx

def extract_text_from_docx(blob_data: bytes) -> str:
    doc = docx.Document(io.BytesIO(blob_data))
    return "\n".join(para.text for para in doc.paragraphs)

def extract_text_from_pdf(blob_data: bytes) -> str:
    pdf = fitz.open(stream=blob_data, filetype="pdf")
    return "".join(page.get_text() for page in pdf)

FILE_TRANSFORMERS = {
    "docx": extract_text_from_docx,
    "pdf": extract_text_from_pdf
}

def extract_text(file: UploadFile) -> str:
    name = (file.filename or "").lower()
    data = file.file.read()
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    appendix = name.split(".")[-1]
    procesor = FILE_TRANSFORMERS.get(appendix, None)
    if procesor is not None:
        return procesor(data)
    
    # fallback – prostý text
    try:
        return data.decode("utf-8")
    except Exception:
        return data.decode("latin-1", errors="ignore")
    
def split_text_to_chunks_with_overlap(
    text: str,
    max_chunk_size: int = 1000,
    overlap: int = 100
) -> typing.Iterable[str]:
    words = text.split()
    
    start = 0
    while start < len(words):
        end = min(start + max_chunk_size, len(words))
        chunk = words[start:end]
        yield chunk
        
        start += max_chunk_size - overlap
    
def split_text_by_tokens(
    text: str,
    tokenizer: PreTrainedTokenizerBase,
    max_tokens: int = 100,          # pro E5: 256–384 je safe
    overlap_tokens: int = 50,       # 32–64
) -> typing.Iterable[str]:
    # normalizace whitespace
    text = " ".join(text.split())

    enc = tokenizer(
        text,
        add_special_tokens=False,
        return_offsets_mapping=True,
    )
    ids = enc["input_ids"]
    offsets = enc["offset_mapping"]  # list[(start_char, end_char)]

    if not ids:
        return []

    step = max_tokens - overlap_tokens
    i = 0
    n = len(ids)
    while i < n:
        j = min(i + max_tokens, n)
        start_char = offsets[i][0]
        end_char = offsets[j - 1][1]
        chunk_text = text[start_char:end_char].strip()
        if chunk_text:
            yield chunk_text
        i += step    

async def process_file(file: UploadFile) -> typing.Iterable[str]:
    text = extract_text(file)
    # return split_text_to_chunks_with_overlap(text)
    return split_text_by_tokens(text)

from sentence_transformers import SentenceTransformer  # pip install sentence-transformers
model_name = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME", "sentence-transformers/all-MiniLM-L6-v2")
model_name = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME", "intfloat/multilingual-e5-large")


TARGET_DIM = 1536


embed_model = SentenceTransformer("intfloat/multilingual-e5-large")


def l2_normalize(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    if x.ndim == 1:
        n = np.linalg.norm(x) + eps
        return (x / n).astype(np.float32)
    n = np.linalg.norm(x, axis=1, keepdims=True) + eps
    return (x / n).astype(np.float32)


def ensure_dim(vecs: np.ndarray, d: int = TARGET_DIM) -> np.ndarray:
    """
    Přizpůsobí tvar na [N, d] (pad 0, nebo truncate), pak L2 normalizuje (float32).
    Vstup může být [dim] nebo [N, dim].
    """
    if vecs.ndim == 1:
        vecs = vecs[None, :]
    n, dim = vecs.shape
    if dim == d:
        return l2_normalize(vecs)
    if dim < d:
        out = np.zeros((n, d), dtype=vecs.dtype)
        out[:, :dim] = vecs
    else:
        out = vecs[:, :d]
    return l2_normalize(out)


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: typing.List[str], *, is_query: bool = False) -> np.ndarray:
        """Vrátí array tvaru [N, TARGET_DIM], float32, L2-normalized."""
        ...


class EmbeddingService:
    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    async def embed_one(self, text: str, *, is_query: bool = False) -> np.ndarray:
        out = await self.provider.embed([text], is_query=is_query)
        return out[0]

    async def embed_many(self, texts: typing.List[str], *, is_query: bool = False) -> np.ndarray:
        return await self.provider.embed(texts, is_query=is_query)


class E5Provider(EmbeddingProvider):
    def __init__(self, model_name: str = "intfloat/multilingual-e5-large"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def _encode_sync(self, texts: typing.List[str]) -> np.ndarray:
        # ST.encode je sync → přes threadpool
        vecs = self.model.encode(texts, normalize_embeddings=True)
        return np.asarray(vecs, dtype=np.float32)

    async def embed(self, texts: typing.List[str], *, is_query: bool = False) -> np.ndarray:
        prefix = "query: " if is_query else "passage: "
        prefixed = [prefix + t for t in texts]
        vecs = await asyncio.to_thread(self._encode_sync, prefixed)  # [N, dim(=1024 u e5-large)]
        return ensure_dim(vecs, TARGET_DIM)  # sjednocení na 1536
    

class AzureOpenAIEmbeddingProvider(EmbeddingProvider):
    """
    Vyžaduje:
      - AZURE_OPENAI_ENDPOINT = https://<resource>.openai.azure.com
      - AZURE_OPENAI_API_KEY
      - AZURE_EMBEDDING_DEPLOYMENT (název deploymentu embedding modelu)
    Pozn.: `dimensions=1536` funguje jen u modelů, které to podporují.
    """
    def __init__(self, deployment: typing.Optional[str] = None, api_version: str = "2024-02-01"):
        from openai import AzureOpenAI
        # endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
        cog_account = os.getenv("AZURE_COGNITIVE_ACCOUNT_NAME", None)
        endpoint = f"https://{cog_account}.openai.azure.com"
        key = os.getenv("OPENAI_API_KEY", None)
        self.client = AzureOpenAI(
            azure_endpoint=endpoint, 
            api_key=key, 
            api_version=api_version
        )
        self.deployment = deployment or os.environ.get("AZURE_EMBEDDING_DEPLOYMENT", "embedding-deployment")

    async def embed(self, texts: typing.List[str], *, is_query: bool = False) -> np.ndarray:
        # Azure klient je sync → přehodíme do threadpoolu
        def _call():
            # Některé modely benefitují z prefixů; pokud víš, že jde o e5-derivát, klidně přidej:
            payload = texts  # případně: [("query: " if is_query else "passage: ") + t for t in texts]
            resp = self.client.embeddings.create(
                model=self.deployment,
                input=payload,
                dimensions=TARGET_DIM,  # použije se, jen když to model umí
            )
            return [d.embedding for d in resp.data]

        embs = await asyncio.to_thread(_call)  # List[List[float]]
        vecs = np.asarray(embs, dtype=np.float32)
        # kdyby model neuměl `dimensions`, vrátí původní dimenzi → sjednotíme
        return ensure_dim(vecs, TARGET_DIM)    


async def compute_embedding_azure(api_key: str, text) -> list[list[float]]:
    """
    Volá Azure AI Inference EmbeddingsClient pro batch textů.
    Vrací seznam embeddingů (pořadí odpovídá vstupu).
    """
    from openai import AzureOpenAI
    cog_account = os.getenv("AZURE_COGNITIVE_ACCOUNT_NAME", None)
    if not cog_account:
        raise ValueError("Chybí proměnná AZURE_COGNITIVE_ACCOUNT_NAME")
    endpoint = f"https://{cog_account}.openai.azure.com"
    model_name = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME", "embedding-deployment")
    vector_dimensions = 1536

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-02-01"
    )
    response = client.embeddings.create(model=model_name, input=text.lower(), dimensions=int(vector_dimensions))
    # response.data je seznam, každý prvek má .embedding
    embedding = response.data[0].embedding
    return embedding

