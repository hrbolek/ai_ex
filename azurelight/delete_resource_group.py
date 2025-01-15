from .AzureLightClient import AzureLightClient

async def delete_resource_group(
    azureLightClient: AzureLightClient, 
    subscription_id: str, 
    RESOURCE_GROUP_NAME: str
):
    """
    Delete a resource group in Azure using AzureLightClient.

    :param azureLightClient: Instance of AzureLightClient.
    :param subscription_id: Azure Subscription ID.
    :param resource_group_name: The name of the resource group to delete.
    :return: Response from the Azure REST API for the delete operation.
    """
    endpoint = f"/subscriptions/{subscription_id}/resourcegroups/{RESOURCE_GROUP_NAME}?api-version=2021-04-01"

    print(f"Deleting resource group: {RESOURCE_GROUP_NAME}...")
    response = await azureLightClient.delete(endpoint)

    if isinstance(response, dict) and "error" in response:
        print(f"Error deleting resource group: {response['error']}")
    else:
        print(f"Resource group '{RESOURCE_GROUP_NAME}' deleted successfully.")

    return response
