import requests
import json

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Nastav své údaje
AZURE_SEARCH_SERVICE_NAME = 'tvuj-nazev-search-service'  # např. 'my-cognitive-search'
AZURE_SEARCH_INDEX_NAME = 'tvuj-index'                     # např. 'documents'
AZURE_SEARCH_API_KEY = 'tvuj-admin-key'                  # API klíč s právem write (najdeš v Azure Portalu)



def get_local_settings():
    with open("./local.settings.json", encoding="utf-8") as f:
        result = json.load(f)
    return result


def search_by_prefix(
    prefix: str,
    service_name: str,
    index_name: str,
    api_key: str,
    top: int = 5
) -> list[dict]:
    """
    Provede vektorové vyhledávání nad indexem.
    """
    endpoint = f"https://{service_name}.search.windows.net"

    client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(api_key)
    )


    results = client.search(
        search_text=f"*",  # hvězdička znamená prefix
        # search_fields="id"
    )

    docs = []
    for r in results:
        docs.append({
            "id":              r.get("id"),
            "content":         r.get("content", ""),
            "document_folder": r.get("document_folder"),
            "score":           r.get("@search.score"),
            # případně další metadata:
            # "document_name":  r.get("document_name"),
            # "document_folder":r.get("document_folder"),
        })
    return docs


def find_with_prefix(PREFIX):
    headers = {
        'Content-Type': 'application/json',
        'api-key': AZURE_SEARCH_API_KEY
    }

    # V Azure Cognitive Search musíš použít $filter s funkcí startswith
    params = {
        '$filter': f"startswith(id, '{PREFIX}')",
        '$top': 1000   # max počet výsledků na stránku (paging lze řešit přes @odata.nextLink)
    }

    response = requests.get(url, headers=headers, params=params)

    print("Status:", response.status_code)
    print("Response:", response.text)
    return response.text

def update_with_id(service_name, index_name, api_key, DOCUMENT_ID, NEW_FOLDER):
    # Tělo požadavku dle Azure Search API: akce 'mergeOrUpload'
    endpoint = f"https://{service_name}.search.windows.net"
    client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(api_key)
    )

    doc = {
        "id": DOCUMENT_ID,
        "document_folder": NEW_FOLDER
        # ostatní pole posílat nemusíš – zůstanou nedotčena (mergeOrUpload)
    }
    result = client.merge_or_upload_documents([doc])
    print("Update response:", result)



env = get_local_settings()
print(env)
values = env.get("Values")
AZURE_SEARCH_SERVICE_NAME = values["AZURE_SEARCH_SERVICE_NAME"]
AZURE_SEARCH_INDEX_NAME = values["AZURE_SEARCH_INDEX_NAME"]
AZURE_SEARCH_API_KEY = values["AZURE_SEARCH_API_KEY"]

# url = f"https://{AZURE_SEARCH_SERVICE_NAME}.search.windows.net/indexes/{AZURE_SEARCH_INDEX_NAME}/docs/index?api-version=2023-11-01"

# docs = find_with_prefix("17_")
docs = search_by_prefix(
    prefix="17_",
    service_name=AZURE_SEARCH_SERVICE_NAME,
    index_name=AZURE_SEARCH_INDEX_NAME,
    api_key=AZURE_SEARCH_API_KEY,
    top=1000
)

prefix="17_",
for doc in docs:
    print(doc["id"], doc["document_folder"])
    id: str = doc["id"]
    if id.startswith(prefix):
        print("updating")
        update_with_id(
            service_name=AZURE_SEARCH_SERVICE_NAME,
            index_name=AZURE_SEARCH_INDEX_NAME,
            api_key=AZURE_SEARCH_API_KEY,
            DOCUMENT_ID=id,
            NEW_FOLDER="https://lib.unob.cz/UNOB_CZ/UNOB/DOKUMENTY/VNITRNI-PREDPISY/Studijn%C3%AD%20a%20zku%C5%A1ebn%C3%AD%20%C5%99%C3%A1d%20Univerzity%20obrany%20v%20Brn%C4%9B.pdf"
        )
# print(docs)
