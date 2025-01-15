from .AzureLightClient import AzureLightClient

async def read_search_service_keys(
    azureLightClient: AzureLightClient,
    subscription_id: str,
    RESOURCE_GROUP_NAME: str,
    SEARCH_SERVICE_NAME: str
):
    """
    Retrieve the admin keys for an Azure Cognitive Search service.

    :param azureLightClient: Instance of AzureLightClient.
    :param subscription_id: Azure Subscription ID.
    :param RESOURCE_GROUP_NAME: Resource group name.
    :param SEARCH_SERVICE_NAME: Search service name.
    :return: The primary and secondary API keys.
    """
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.Search/searchServices/{SEARCH_SERVICE_NAME}/listAdminKeys?api-version=2020-08-01"
    response = await azureLightClient.post(endpoint, {})
    if isinstance(response, dict):
        return response.get("primaryKey"), response.get("secondaryKey")
    else:
        raise Exception(f"Failed to fetch keys: {response}")
