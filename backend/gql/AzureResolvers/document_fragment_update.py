from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

from .environment import (
    AZURE_SEARCH_SERVICE_NAME,
    AZURE_SEARCH_INDEX_NAME,
    AZURE_SEARCH_API_KEY,
)

def update_document_folder_by_id_prefix(id_prefix: str, new_folder: str):
    endpoint = f"https://{AZURE_SEARCH_SERVICE_NAME}.search.windows.net"
    client = SearchClient(
        endpoint=endpoint,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
    )

    # 1. Najdi všechny dokumenty, jejichž ID začíná na id_prefix
    # Azure Cognitive Search podporuje OData funkci 'startswith'
    # filter_str = f"startswith(id, '{id_prefix}')"
    # results = client.search(
    #     search_text="*",
    #     filter=filter_str,
    #     top=1000  # stránkuj pokud potřebuješ víc
    # )

    results = client.search(
        search_text="*",
        top=1000  # případně stránkuj
    )

    docs_to_update = []
    for doc in results:
        # Filtrovat prefix v Pythonu!
        if doc["id"].startswith(id_prefix):
            updated_doc = dict(doc)
            print(f"updating {doc['id']} to {new_folder}")
            updated_doc["document_folder"] = new_folder
            docs_to_update.append(updated_doc)
        else:
            print(f"skipping {doc['id']} ({id_prefix})")

    if not docs_to_update:
        print("Nic k aktualizaci.")
        return 0

    print(f"updates ready {len(docs_to_update)}")
    # 2. Hromadný zápis aktualizovaných dokumentů
    client.merge_or_upload_documents(documents=docs_to_update)
    print(f"Aktualizováno: {len(docs_to_update)} dokumentů.")
    return len(docs_to_update)
