from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

from .environment import (
    AZURE_COGNITIVE_ACCOUNT_NAME,
    AZURE_SEARCH_SERVICE_NAME,
    AZURE_SEARCH_INDEX_NAME,
    AZURE_SEARCH_API_KEY,
    OPENAI_API_KEY,
    AZURE_EMBEDDING_DEPLOYMENT_NAME,
    AZURE_CHAT_DEPLOYMENT_NAME,
)

def delete_documents_by_filter(filter_str):
    endpoint = f"https://{AZURE_SEARCH_SERVICE_NAME}.search.windows.net"
    client = SearchClient(
        endpoint=endpoint,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
    )

    # 1. Najdi všechny dokumenty podle filtru
    results = client.search(
        search_text="*",
        filter=filter_str,
        top=1000  # nebo stránkuj
    )

    ids_to_delete = [{"id": doc["id"]} for doc in results]

    if not ids_to_delete:
        return 0

    # 2. Smaž všechny nalezené dokumenty podle ID
    client.delete_documents(documents=ids_to_delete)
    return len(ids_to_delete)
