from .AzureLightClient import AzureLightClient

from ._desc import (
    RESOURCE_GROUP_NAME,
    LOCATION,
    STORAGE_ACCOUNT_NAME
)

async def create_storage_account(azureLightClient: AzureLightClient, subscription_id: str, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, LOCATION=LOCATION, STORAGE_ACCOUNT_NAME=STORAGE_ACCOUNT_NAME):
    """
    Asynchronously create a storage account in Azure.

    This function uses the Azure REST API to create a storage account 
    with the specified name, location, and configuration in a resource group.

    :param azureLightClient: An instance of AzureLightClient for making API calls.
    :param subscription_id: The Azure subscription ID where the storage account will be created.
    :param RESOURCE_GROUP_NAME: The name of the resource group where the storage account will be created.
    :param LOCATION: The Azure region for the storage account (e.g., "Sweden Central").
    :param STORAGE_ACCOUNT_NAME: The name of the storage account to create.

    :returns: The raw response from the Azure REST API.
    :rtype: dict or str (depending on the API response)
    """
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.Storage/storageAccounts/{STORAGE_ACCOUNT_NAME}?api-version=2022-09-01"
    payload = {
        "location": LOCATION,
        "sku": {"name": "Standard_LRS"},
        "kind": "StorageV2",
        "properties": {
            "accessTier": "Hot",
            "enableHttpsTrafficOnly": True
        }
    }

    response = await azureLightClient.put(endpoint, payload)
    return response
