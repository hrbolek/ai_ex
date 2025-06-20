import os

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizedQuery

# Config načítání
def getenv(key, default=""):
    return os.getenv(key, default)


endpoint = f"https://{getenv('AZURE_SEARCH_SERVICE_NAME')}.search.windows.net"
index = getenv("AZURE_SEARCH_INDEX_NAME")
api_key = getenv("AZURE_SEARCH_API_KEY")

from semantic_kernel.functions import kernel_function

@kernel_function(
    description="Najde fragmenty dokumentů v Azure Cognitive Search na základě vektoru.",
    # input_variables=[
    #     {"name": "vector", "description": "Embedding dotazu"}
    # ]
)
async def search_by_vector(vector) -> list:
    
    client = SearchClient(
        endpoint=endpoint,
        index_name=index,
        credential=AzureKeyCredential(api_key)
    )
    vq = VectorizedQuery(vector=vector, k_nearest_neighbors=10, fields="contentVector")
    # print(f"search_by_vector.pre search {vector}")
    print(f"search_by_vector.pre search {type(vector)}")
    results = client.search(search_text="*", vector_queries=[vq])
    print("search_by_vector.post search")
    docs = [{
        "id": r.get("id"),
        "content": r.get("content", ""),
        "document_folder": r.get("document_folder"),
        "score": r.get("@search.score"),
    } for r in results]
    # print(f"search_by_vector.result\n{docs}")
    return docs