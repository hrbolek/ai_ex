import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import azure.functions as func

def delete_document_from_search(service_name, index_name, api_key, document_folder, document_name):
    endpoint = f"https://{service_name}.search.windows.net"
    client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(api_key))

    query = f"document_folder eq '{document_folder}' and document_name eq '{document_name}'"
    results = client.search(search_text="*", filter=query, include_total_count=True)

    try:
        first_result = next(results)
    except StopIteration:
        print(f"❌ Dokument s názvem '{document_name}' ve složce '{document_folder}' nebyl nalezen.")
        return False

    document_id = first_result['id']
    print(f"✅ Dokument '{document_name}' ve složce '{document_folder}' nalezen. ID: {document_id}")

    try:
        client.delete_documents(documents=[{"id": document_id}])
        print(f"✅ Dokument '{document_name}' byl úspěšně odstraněn z indexu.")
        return True
    except Exception as e:
        print(f"❌ Chyba při odstraňování dokumentu '{document_name}': {e}")
        return False

def main(req: func.HttpRequest) -> func.HttpResponse:
    search_service_name = os.getenv("AZURE_SEARCH_SERVICE_NAME")
    search_index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
    search_api_key = os.getenv("AZURE_SEARCH_API_KEY")

    document_folder = req.params.get('document_folder')
    document_name = req.params.get('document_name')
    
    if not document_folder or not document_name:
        return func.HttpResponse(
            "Parametry 'document_folder' a 'document_name' nejsou přítomny v požadavku.", status_code=400
        )
    
    success = delete_document_from_search(search_service_name, search_index_name, search_api_key, document_folder, document_name)
    
    if success:
        return func.HttpResponse(
            f"Dokument '{document_name}' ve složce '{document_folder}' byl úspěšně odstraněn z indexu.", status_code=200
        )
    else:
        return func.HttpResponse(
            f"Dokument '{document_name}' ve složce '{document_folder}' nebyl nalezen nebo se nepodařilo odstranit.", status_code=404
        )
