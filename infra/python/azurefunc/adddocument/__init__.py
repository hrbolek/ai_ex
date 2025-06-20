import os
import io
import logging
import json
import azure.functions as func
import docx
import fitz  # PyMuPDF

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI


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

def generate_embedding(api_key: str, text) -> list[list[float]]:
    """
    Volá Azure AI Inference EmbeddingsClient pro batch textů.
    Vrací seznam embeddingů (pořadí odpovídá vstupu).
    """
    cog_account = getenv("AZURE_COGNITIVE_ACCOUNT_NAME", None)
    if not cog_account:
        raise ValueError("Chybí proměnná AZURE_COGNITIVE_ACCOUNT_NAME")
    endpoint = f"https://{cog_account}.openai.azure.com"
    model_name = getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME", "embedding-deployment")
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


def make_json_response(payload, status_code=200):
    return func.HttpResponse(
        json.dumps(payload, ensure_ascii=False),
        mimetype="application/json",
        status_code=status_code
    )

def adddocumenthandler(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # načtení konfigurace z env vars
        search_service  = getenv("AZURE_SEARCH_SERVICE_NAME", None)
        search_index    = getenv("AZURE_SEARCH_INDEX_NAME", None)
        search_api_key  = getenv("AZURE_SEARCH_API_KEY", None)
        ai_api_key      = getenv("OPENAI_API_KEY", None)

        if not all([search_service, search_index, search_api_key, ai_api_key]):
            msg = ("Chybí některá z proměnných: "
                   "AZURE_SEARCH_SERVICE_NAME, AZURE_SEARCH_INDEX_NAME, "
                   "AZURE_SEARCH_API_KEY nebo OPENAI_API_KEY.")
            logging.warning(msg)
            return make_json_response({"success": False, "message": msg}, status_code=400)
        

        # zpracování multipart/form-data
        if not req.files or "file" not in req.files:
            msg = "Očekávám soubor v poli 'file' (multipart/form-data)."
            logging.warning(msg)
            return make_json_response({"success": False, "message": msg}, status_code=400)
        
        uploaded = req.files["file"]
        blob_data = uploaded.stream.read()
        filename = uploaded.filename

        # parametr URL dokumentu
        document_folder = req.form.get("document_folder") or req.params.get("document_folder")
        if not document_folder:
            msg = "Chybí parametr documentUrl (v těle form nebo query)."
            logging.warning(msg)
            return make_json_response({"success": False, "message": msg}, status_code=400)

        # extrakce textu podle přípony
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext not in FILE_TRANSFORMERS:
            msg = f"Podporované přípony: {', '.join(FILE_TRANSFORMERS)}"
            logging.warning(msg)
            return make_json_response({"success": False, "message": msg}, status_code=400)
        
        content = FILE_TRANSFORMERS[ext](blob_data)

        # rozdělíme na překrývající se chunk-y
        chunks = split_text_to_chunks_with_overlap(content)
        if not chunks:
            msg = "Extrahovaný text je prázdný."
            logging.warning(msg)
            return make_json_response({"success": False, "message": msg}, status_code=400)

        # batch generování embeddingů
        try:
            embeddings = [generate_embedding(ai_api_key, chunk) for chunk in chunks]
        except Exception as e:
            msg = f"Chyba při generování embeddingů: {e}"
            logging.exception(msg)
            return make_json_response({"success": False, "message": msg}, status_code=500)

        # příprava dokumentů pro index
        docs = []
        filename = filename.split(".")[0].encode("ascii", errors="ignore").decode().replace(" ", "")

        for i, (chunk, emb) in enumerate(zip(chunks, embeddings), start=1):
            docs.append({
                "id":        f"{filename}_chunk{i}",
                "content":   chunk,
                "document_folder": document_folder,
                "contentVector": emb
            })

        # nahrát všechny v jednom batch
        try:
            index_documents_batch(
                service_name=search_service,
                index_name=search_index,
                api_key=search_api_key,
                documents=docs
            )
            msg = f"Test message"
        except Exception as e:
            msg = f"Chyba při uploadu do Azure Search: {e}"
            logging.exception(msg)
            return make_json_response({"success": False, "message": msg}, status_code=500)

        return make_json_response({
            "success": True,
            "message": msg,
            "filename": filename,
            "chunks": len(chunks)
        }, status_code=200)
    
    except Exception as ex:
        msg = f"Internal server error: {ex}"
        logging.exception(msg)
        return make_json_response({"success": False, "message": msg}, status_code=500)


print("import adddocument OK")