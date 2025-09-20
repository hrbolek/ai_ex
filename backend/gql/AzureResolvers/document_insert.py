import io
import docx
import fitz  # PyMuPDF

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

from .environment import (
    AZURE_COGNITIVE_ACCOUNT_NAME,
    AZURE_SEARCH_SERVICE_NAME,
    AZURE_SEARCH_INDEX_NAME,
    AZURE_SEARCH_API_KEY,
    OPENAI_API_KEY,
    AZURE_EMBEDDING_DEPLOYMENT_NAME,
    AZURE_CHAT_DEPLOYMENT_NAME,
)

# search_service  = getenv("AZURE_SEARCH_SERVICE_NAME", None)
#         search_index    = getenv("AZURE_SEARCH_INDEX_NAME", None)
#         search_api_key  = getenv("AZURE_SEARCH_API_KEY", None)
#         ai_api_key      = getenv("OPENAI_API_KEY", None)


# Rozšiřitelné mapování přípon → extrakční funkce
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


def split_text_to_chunks_with_overlap(
        text: str,
        max_chunk_size: int = 1000,
        overlap: int = 100
    ) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += max_chunk_size - overlap
    return chunks

def generate_embedding(text: str) -> list[list[float]]:
    """
    Volá Azure AI Inference EmbeddingsClient pro batch textů.
    Vrací seznam embeddingů (pořadí odpovídá vstupu).
    """
    api_key = OPENAI_API_KEY
    cog_account = AZURE_COGNITIVE_ACCOUNT_NAME
    endpoint = f"https://{cog_account}.openai.azure.com"
    model_name = AZURE_EMBEDDING_DEPLOYMENT_NAME
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

def index_documents_batch(
    documents: list[dict]
):
    service_name = AZURE_SEARCH_SERVICE_NAME
    index_name = AZURE_SEARCH_INDEX_NAME
    api_key = AZURE_SEARCH_API_KEY
    endpoint = f"https://{service_name}.search.windows.net"
    client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(api_key)
    )
    result = client.upload_documents(documents)
    print(f"Upload result: {result}")
    return result

def document_insert(url, filename, stream):
    
    blob_data = stream.read()

    # parametr URL dokumentu
    document_folder = url

    # extrakce textu podle přípony
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in FILE_TRANSFORMERS:
        msg = f"Podporované přípony: {', '.join(FILE_TRANSFORMERS)}"
        raise Exception(f"unsuported file extension")
    
    content = FILE_TRANSFORMERS[ext](blob_data)

    # rozdělíme na překrývající se chunk-y
    chunks = split_text_to_chunks_with_overlap(content)

    # batch generování embeddingů
    embeddings = [generate_embedding(chunk) for chunk in chunks]
    
    #TODO udelat sumarizaci chunku a vlozit ji do indexu pro potreby popisu pri interakci s uzivatelem
    #TODO strom chunku, napr tri urovne pro presnejsi lokalizaci casti dokumentu, ktera je pro dotaz relevantni, tedy chunks from chunk

    # příprava dokumentů pro index
    docs = []
    #TODO osetrit, pokud je v nazvu pouzita tecka, napr. Statut ve zneni 1. zmeny.pdf
    filename = filename.split(".")[0].encode("ascii", errors="ignore").decode().replace(" ", "")

    for i, (chunk, emb) in enumerate(zip(chunks, embeddings), start=1):
        docs.append({
            "id":        f"{filename}_chunk{i}",
            "content":   chunk,
            "document_folder": document_folder,
            "contentVector": emb
        })

    # nahrát všechny v jednom batch
    result = index_documents_batch(
        documents=docs
    )
    return result
