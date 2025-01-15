from .AzureLightClient import AzureLightClient

async def read_semantic_search(
    azureLightClient: AzureLightClient,
    SEARCH_SERVICE_NAME: str,
    API_KEY: str,
    index_name: str,
    query: str
):
    """
    Query the Azure Cognitive Search index using semantic search.

    :param azureLightClient: Instance of AzureLightClient.
    :param SEARCH_SERVICE_NAME: Search service name.
    :param API_KEY: Admin API key for the search service.
    :param index_name: Name of the search index.
    :param query: Search query string.
    """
    endpoint = f"https://{SEARCH_SERVICE_NAME}.search.windows.net/indexes/{index_name}/docs/search?api-version=2021-04-30-Preview"
    headers = {"Content-Type": "application/json", "api-key": API_KEY}
    payload = {
        "queryType": "semantic",
        "semanticConfiguration": "default",
        "search": query
    }
    response = await azureLightClient.post(endpoint, payload)
    print(f"Semantic Search Response: {response}")
