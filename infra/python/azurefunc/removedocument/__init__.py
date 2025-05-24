import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import azure.functions as func

# Funkce pro odstranění dokumentu z indexu na základě jeho `document_folder` a `document_name`
def delete_document_from_search(service_name, index_name, api_key, document_folder, document_name):
    endpoint = f"https://{service_name}.search.windows.net"
    client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(api_key))

    # Vyhledání dokumentu podle kombinace document_folder a document_name
    query = f"document_folder:{document_folder} AND document_name:{document_name}"
    results = client.search(search_text=query, include_total_count=True)

    if results:
        # Získání ID dokumentu (dokument musí mít unikátní combination of document_folder and document_name)
        document_id = results[0]['id']  # Assuming 'id' is in the result
        print(f"✅ Dokument '{document_name}' ve složce '{document_folder}' nalezen. ID: {document_id}")

        # Odstranění dokumentu podle jeho ID
        result = client.delete_documents(documents=[{"id": document_id}])
        
        if result:
            print(f"✅ Dokument '{document_name}' byl úspěšně odstraněn z indexu.")
        else:
            print(f"❌ Chyba při odstraňování dokumentu '{document_name}' z indexu.")
    else:
        print(f"❌ Dokument s názvem '{document_name}' ve složce '{document_folder}' nebyl nalezen.")

# Hlavní Azure Function handler pro odstranění dokumentu z indexu
def main(req: func.HttpRequest) -> func.HttpResponse:
    # Získání připojení k Cognitive Search z environmentálních proměnných
    search_service_name = os.getenv("AZURE_SEARCH_SERVICE_NAME")
    search_index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
    search_api_key = os.getenv("AZURE_SEARCH_API_KEY")

    # Získání názvu složky a názvu souboru z požadavku (parametry v URL nebo v těle požadavku)
    document_folder = req.params.get('document_folder')
    document_name = req.params.get('document_name')
    
    if not document_folder or not document_name:
        return func.HttpResponse(
            "Parametry 'document_folder' a 'document_name' nejsou přítomny v požadavku.", status_code=400
        )
    
    # Odstranění dokumentu z indexu podle document_folder a document_name
    delete_document_from_search(search_service_name, search_index_name, search_api_key, document_folder, document_name)
    
    return func.HttpResponse(
        f"Dokument '{document_name}' ve složce '{document_folder}' byl úspěšně odstraněn z indexu.", status_code=200
    )
