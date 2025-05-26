import os
import docx
import fitz  # PyMuPDF pro PDF
from openai import OpenAI

import azure.functions as func

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import io
from azure.functions import HttpRequest

# Funkce pro extrakci textu z docx souboru
def extract_text_from_docx(blob_data):
    doc = docx.Document(io.BytesIO(blob_data))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Funkce pro extrakci textu z PDF souboru
def extract_text_from_pdf(blob_data):
    doc = fitz.open(io.BytesIO(blob_data))
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def generate_embedding(apikey: str, text: str):
    client = OpenAI(apikey)
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embedding_vector = response.data[0].embedding
    return embedding_vector

# Funkce pro indexování dokumentu do Azure Cognitive Search
def index_document_to_search(
        service_name, 
        index_name, 
        api_key, 
        document_id, 
        content,
        url=None,
        embedding=None
    ):
    endpoint = f"https://{service_name}.search.windows.net"
    client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(api_key))
    
    # Vytvoření dokumentu pro indexování
    document = {
        "id": document_id,
        "content": content
    }
    if url:
        document["url"] = url    
    
    if embedding:
        document["contentVector"] = embedding

    # Indexování dokumentu
    client.upload_documents(documents=[document])
    print(f"✅ Dokument '{document_id}' byl úspěšně zaindexován.")

# Hlavní Azure Function handler pro příjem souboru přes REST API
def main(req: HttpRequest) -> func.HttpResponse:
    # Získání připojení k Blob Storage a Cognitive Search z environmentálních proměnných
    blob_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    search_service_name = os.getenv("AZURE_SEARCH_SERVICE_NAME")
    search_index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
    search_api_key = os.getenv("AZURE_SEARCH_API_KEY")
    ai_api_key = os.getenv("OPENAI_API_KEY")

    # Inicializace Blob Storage clienta
    blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
    
    # Příjem souboru v těle požadavku
    file = req.files['file']  # Tento soubor je odesílán jako multipart/form-data
    
    # Získání obsahu souboru
    file_data = file.read()

    # Získání názvu souboru (bude použit jako ID dokumentu)
    document_id = file.filename

    document_url = req.form.get("documentUrl")  # pokud je součástí formuláře
    # nebo
    # document_url = req.params.get("documentUrl")  # pokud je v query parametrech
    if not document_url:
        return func.HttpResponse(
            "URL dokumentu není zadána.", status_code=400
        )
    
    # Extrakce textu z dokumentu na základě typu souboru
    if document_id.endswith(".docx"):
        content = extract_text_from_docx(file_data)
    elif document_id.endswith(".pdf"):
        content = extract_text_from_pdf(file_data)
    else:
        return func.HttpResponse(
            "Podporovány jsou pouze soubory PDF a DOCX.", status_code=400
        )
    
    # Generování embeddingu
    embedding = generate_embedding(ai_api_key, content)

    # Indexování dokumentu do Cognitive Search
    index_document_to_search(
        search_service_name, 
        search_index_name, 
        search_api_key, 
        document_id, 
        content,
        url=document_url,
        embedding=embedding
    )
    
    return func.HttpResponse(
        f"Dokument '{document_id}' byl úspěšně zaindexován.", status_code=200
    )
