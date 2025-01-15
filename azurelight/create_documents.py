from .AzureLightClient import AzureLightClient

async def create_documents(
    azureLightClient: AzureLightClient,
    SEARCH_SERVICE_NAME: str,
    API_KEY: str,
    index_name: str
):
    """
    Upload documents to the Azure Cognitive Search index.

    :param azureLightClient: Instance of AzureLightClient.
    :param SEARCH_SERVICE_NAME: Search service name.
    :param API_KEY: Admin API key for the search service.
    :param index_name: Name of the search index.
    """
    endpoint = f"https://{SEARCH_SERVICE_NAME}.search.windows.net/indexes/{index_name}/docs/index?api-version=2021-04-30-Preview"
    headers = {"Content-Type": "application/json", "api-key": API_KEY}
    payload = {
        "value": [
            {
                "@search.action": "upload",
                "id": "1",
                "title": "Azure Cognitive Search",
                "content": "Azure Cognitive Search is a cloud search service.",
                "tags": ["azure", "search", "ai"]
            },
            {
                "@search.action": "upload",
                "id": "2",
                "title": "Semantic Search",
                "content": "Semantic search uses AI to improve search relevance.",
                "tags": ["semantic", "ai"]
            }
        ]
    }
    response = await azureLightClient.post(endpoint, payload)
    print(f"Document Upload Response: {response}")
