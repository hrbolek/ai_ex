from .AzureLightClient import AzureLightClient

async def create_search_index(
    azureLightClient: AzureLightClient,
    subscription_id: str,
    RESOURCE_GROUP_NAME: str,
    SEARCH_SERVICE_NAME: str
):
    """
    Create a semantic index in Azure Cognitive Search.

    :param azureLightClient: Instance of AzureLightClient.
    :param subscription_id: Azure Subscription ID.
    :param RESOURCE_GROUP_NAME: Resource group name.
    :param SEARCH_SERVICE_NAME: Search service name.
    """
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.Search/searchServices/{SEARCH_SERVICE_NAME}/indexes/semantic-index?api-version=2021-04-30-Preview"
    payload = {
        "name": "semantic-index",
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "searchable": False},
            {"name": "title", "type": "Edm.String", "searchable": True},
            {"name": "content", "type": "Edm.String", "searchable": True},
            {"name": "tags", "type": "Collection(Edm.String)", "searchable": True}
        ]
    }
    response = await azureLightClient.put(endpoint, payload)
    print(f"Search Index Response: {response}")
    return response