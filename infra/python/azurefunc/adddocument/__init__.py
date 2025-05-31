import os
import io
import logging

import azure.functions as func
import docx
import fitz  # PyMuPDF

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference import EmbeddingsClient


ENV_KEY_NAMES = {
    "AZURE_COGNITIVE_ACCOUNT_NAME": "AZURE_COGNITIVE_ACCOUNT_NAME",
    "AZURE_EMBEDDING_DEPLOYMENT_NAME": "AZURE_EMBEDDING_DEPLOYMENT_NAME",
    "AZURE_SEARCH_SERVICE_NAME": "AZURE_SEARCH_SERVICE_NAME",
    "AZURE_SEARCH_INDEX_NAME": "AZURE_SEARCH_INDEX_NAME",
    "AZURE_SEARCH_API_KEY": "AZURE_SEARCH_API_KEY",
    "OPENAI_API_KEY": "OPENAI_API_KEY"
}

def getenv(key_name, default_value):
    proxied_key_name = ENV_KEY_NAMES.get(key_name, None)
    assert proxied_key_name is not None, f"missing {key_name} in proxied list of key_names"
    result = os.getenv(proxied_key_name, default_value)
    return result


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

def generate_embedding(api_key: str, texts: list[str]) -> list[list[float]]:
    """
    Volá Azure AI Inference EmbeddingsClient pro batch textů.
    Vrací seznam embeddingů (pořadí odpovídá vstupu).
    """
    cog_account = getenv("AZURE_COGNITIVE_ACCOUNT_NAME", None)
    if not cog_account:
        raise ValueError("Chybí proměnná AZURE_COGNITIVE_ACCOUNT_NAME")
    endpoint = f"https://{cog_account}.openai.azure.com"
    model_name = getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME", "embedding-deployment")

    client = EmbeddingsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key),
        model=model_name
    )
    response = client.embed(input=texts)
    # response.data je seznam, každý prvek má .embedding
    return [item.embedding for item in response.data]

def index_documents_batch(
        service_name: str,
        index_name: str,
        api_key: str,
        documents: list[dict]
    ):
    endpoint = f"https://{service_name}.search.windows.net"
    client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(api_key)
    )
    result = client.upload_documents(documents)
    logging.info(f"Upload result: {result}")

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # načtení konfigurace z env vars
        search_service  = getenv("AZURE_SEARCH_SERVICE_NAME", None)
        search_index    = getenv("AZURE_SEARCH_INDEX_NAME", None)
        search_api_key  = getenv("AZURE_SEARCH_API_KEY", None)
        ai_api_key      = getenv("OPENAI_API_KEY", None)

        if not all([search_service, search_index, search_api_key, ai_api_key]):
            raise ValueError("Chybí některá z proměnných: "
                             "AZURE_SEARCH_SERVICE_NAME, AZURE_SEARCH_INDEX_NAME, "
                             "AZURE_SEARCH_API_KEY nebo OPENAI_API_KEY.")

        # zpracování multipart/form-data
        if not req.files or "file" not in req.files:
            return func.HttpResponse(
                "Očekávám soubor v poli 'file' (multipart/form-data).",
                status_code=400
            )
        uploaded = req.files["file"]
        blob_data = uploaded.stream.read()
        filename = uploaded.filename

        # parametr URL dokumentu
        document_url = req.form.get("documentUrl") or req.params.get("documentUrl")
        if not document_url:
            return func.HttpResponse(
                "Chybí parametr documentUrl (v těle form nebo query).",
                status_code=400
            )

        # extrakce textu podle přípony
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext not in FILE_TRANSFORMERS:
            return func.HttpResponse(
                f"Podporované přípony: {', '.join(FILE_TRANSFORMERS)}",
                status_code=400
            )
        content = FILE_TRANSFORMERS[ext](blob_data)

        # rozdělíme na překrývající se chunk-y
        chunks = split_text_to_chunks_with_overlap(content)
        if not chunks:
            raise ValueError("Extrahovaný text je prázdný.")

        # batch generování embeddingů
        embeddings = generate_embedding(ai_api_key, chunks)

        # příprava dokumentů pro index
        docs = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings), start=1):
            docs.append({
                "id":        f"{filename}_chunk{i}",
                "content":   chunk,
                "url":       document_url,
                "contentVector": emb
            })

        # nahrát všechny v jednom batch
        index_documents_batch(
            service_name=search_service,
            index_name=search_index,
            api_key=search_api_key,
            documents=docs
        )

        return func.HttpResponse(
            f"Dokument '{filename}' rozdělen na {len(chunks)} částí a úspěšně zaindexován.",
            status_code=200
        )
    except ValueError as ve:
        logging.warning(str(ve))
        return func.HttpResponse(str(ve), status_code=400)
    except Exception as ex:
        logging.exception(ex)
        return func.HttpResponse(
            "Internal server error.", status_code=500
        )
