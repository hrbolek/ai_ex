import azure.functions as func
import openai

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

def search_documents(query: str, search_service_name, index_name, search_api_key):
    """
    Vyhledává semantické dokumenty podle dotazu, který je převeden na embedding.
    """
    # Inicializace klienta pro Azure Cognitive Search
    endpoint = f"https://{search_service_name}.search.windows.net"
    client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(search_api_key))

    # Předpokládáme, že máte metodu pro převod dotazu na vektor
    query_vector = generate_query_vector(query)  # Funkce pro generování vektoru pro dotaz

    # Vyhledávací dotaz s vektorem
    results = client.search(
        search_text="*",
        vector=query_vector,
        top=10  # Počet výsledků
    )
    
    documents = []
    for result in results:
        documents.append({
            "id": result['id'],
            "document_name": result['document_name'],
            "document_folder": result['document_folder'],
            "score": result['@search.score']
        })

    return documents



openai.api_key = "YOUR_OPENAI_API_KEY"

def generate_query_vector(query: str):
    """
    Tato funkce přijme textový dotaz, použije OpenAI model pro generování embeddingu.
    """
    response = openai.Embedding.create(
        model="text-embedding-3-large",  # Model pro generování embeddingů
        input=query  # Dotaz
    )
    
    # Extrahování embeddingu (vektoru) z odpovědi
    embedding = response['data'][0]['embedding']
    return embedding

def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello from Azure Function! Version 2", status_code=200)