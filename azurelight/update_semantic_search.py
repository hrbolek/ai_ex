from .AzureLightClient import AzureLightClient

async def update_semantic_search(
    azureLightClient: AzureLightClient,
    SEARCH_SERVICE_NAME: str,
    API_KEY: str
):
    """
    Configure semantic search for Azure Cognitive Search.

    :param azureLightClient: Instance of AzureLightClient.
    :param SEARCH_SERVICE_NAME: Search service name.
    :param API_KEY: Admin API key for the search service.
    """
    endpoint = f"https://{SEARCH_SERVICE_NAME}.search.windows.net/semanticConfig?api-version=2021-04-30-Preview"
    headers = {"Content-Type": "application/json", "api-key": API_KEY}
    payload = {
        "name": "default",
        "prioritizedFields": {
            "titleField": {"fieldName": "title"},
            "contentFields": [{"fieldName": "content"}],
            "keywordsField": {"fieldName": "tags"}
        }
    }
    response = await azureLightClient.post(endpoint, payload)
    print(f"Semantic Configuration Response: {response}")
