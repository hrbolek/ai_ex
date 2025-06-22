from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

from .environment import (
    AZURE_SEARCH_SERVICE_NAME,
    AZURE_SEARCH_INDEX_NAME,
    AZURE_SEARCH_API_KEY,
)

def delete_document_fragment(document_id: str) -> bool:
    """
    Smaže dokument s daným ID z Azure Cognitive Search indexu.
    Vrací True při úspěchu, jinak False.
    """
    endpoint = f"https://{AZURE_SEARCH_SERVICE_NAME}.search.windows.net"
    client = SearchClient(
        endpoint=endpoint,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
    )

    # Azure Search podporuje dávkové operace, i pro jeden dokument musíš použít batch
    try:
        result = client.delete_documents(documents=[{"id": document_id}])
        # Můžeš zkontrolovat stav výsledku:
        # print(result)
        return True
    except Exception as ex:
        # Můžeš zalogovat: print(f"Chyba při mazání dokumentu: {ex}")
        return False
