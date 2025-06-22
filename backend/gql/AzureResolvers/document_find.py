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

# search_service = getenv("AZURE_AZURE_SEARCH_SERVICE_NAME_NAME", "")
#     search_index   = getenv("AZURE_SEARCH_INDEX_NAME", "")
#     search_api_key = getenv("AZURE_SEARCH_API_KEY","")
#     ai_api_key     = getenv("OPENAI_API_KEY","")
def search_documents(
    filter_str: str = None,
    skip: int = 0,
    limit: int = 10
) -> list[dict]:
    """
    Provede vektorové vyhledávání nad indexem.
    """
    endpoint = f"https://{AZURE_SEARCH_SERVICE_NAME}.search.windows.net"

    client = SearchClient(
        endpoint=endpoint,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
    )

    results = client.search(
        search_text="*",
        filter=filter_str,  # ← filtr se použije jen pokud není None
        top=limit,       # počet výsledků (např. 10)
        skip=skip        # přeskočit (např. 20)
    )

    docs = []
    for r in results:
        docs.append({
            "id":              r.get("id"),
            "content":         r.get("content", ""),
            "document_folder": r.get("document_folder"),
            # případně další metadata:
            # "document_name":  r.get("document_name"),
            # "document_folder":r.get("document_folder"),
        })
    return docs