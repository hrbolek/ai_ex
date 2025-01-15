from .AzureLightClient import AzureLightClient

from ._desc import (
    RESOURCE_GROUP_NAME,
    LOCATION,
    SEARCH_SERVICE_NAME
)

async def create_search_service(azureLightClient: AzureLightClient, subscription_id: str, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, LOCATION=LOCATION, SEARCH_SERVICE_NAME=SEARCH_SERVICE_NAME):
    """
    Asynchronously create an Azure Search Service.

    This function uses the Azure REST API to create or update an Azure Search Service 
    with the specified configuration in a resource group.

    :param azureLightClient: An instance of AzureLightClient for making API calls.
    :param subscription_id: The Azure subscription ID where the search service will be created.
    :param RESOURCE_GROUP_NAME: The name of the resource group where the search service will be created.
    :param LOCATION: The Azure region for the search service (e.g., "Sweden Central").
    :param SEARCH_SERVICE_NAME: The name of the search service to create.

    :returns: The raw response from the Azure REST API.
    :rtype: dict or str (depending on the API response)
    """
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.Search/searchServices/{SEARCH_SERVICE_NAME}?api-version=2024-06-01-Preview"
    payload = {
        "location": LOCATION,
        "sku": {"name": "basic"},
        "properties": {
            "replicaCount": 1,
            "partitionCount": 1,
            "publicNetworkAccess": "Enabled"
        },
        "tags": {"ProjectType": "semantic-search"}
    }

    response = await azureLightClient.put(endpoint, payload)
    return response
