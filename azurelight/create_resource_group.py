from .AzureLightClient import AzureLightClient

from ._desc import (
    RESOURCE_GROUP_NAME,
    LOCATION
)

async def create_resource_group(azureLightClient: AzureLightClient, subscription_id: str, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, LOCATION=LOCATION):
    """
    Asynchronously create or update a resource group in Azure.

    This function uses the Azure REST API to create or update a resource group 
    with the specified name and location under the given subscription.

    :param azureLightClient: An instance of AzureLightClient for making API calls.
    :param subscription_id: The Azure subscription ID where the resource group will be created.
    :param RESOURCE_GROUP_NAME: The name of the resource group to create or update. Defaults to a global constant.
    :param LOCATION: The Azure region for the resource group (e.g., "Sweden Central"). Defaults to a global constant.

    :returns: The raw response from the Azure REST API.
    :rtype: dict or str (depending on the API response)
    """
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}?api-version=2021-04-01"
    payload = {
        "location": LOCATION
    }

    response = await azureLightClient.put(endpoint, payload)
    return response

