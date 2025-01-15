from .AzureLightClient import AzureLightClient

from ._desc import (
    RESOURCE_GROUP_NAME,
    OPENAI_ACCOUNT_NAME
)

async def update_network_access_public(
    azureLightClient, 
    subscription_id, 
    RESOURCE_GROUP_NAME, 
    OPENAI_ACCOUNT_NAME,
    LOCATION
):
    """
    Enable public network access for the Cognitive Services account.

    :param azureLightClient: Instance of AzureLightClient.
    :param subscription_id: Azure Subscription ID.
    :param RESOURCE_GROUP_NAME: Name of the resource group.
    :param OPENAI_ACCOUNT_NAME: Name of the Cognitive Services account.
    :return: Response from the Azure REST API.
    """
    # Endpoint to get the current account details
    get_endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}?api-version=2024-10-01"
    # Fetch existing account details
    current_account = await azureLightClient.get(get_endpoint)
    if "error" in current_account:
        raise Exception(f"Error fetching account details: {current_account['error']}")

    # Ensure the required `kind` field and existing properties are included
    payload = {
        "location": LOCATION,
        "kind": current_account.get("kind"),  # Include existing 'kind'
        "properties": {
            "publicNetworkAccess": "Enabled"
        },
        "sku": current_account.get("sku"),  # Include existing 'sku'
        "tags": current_account.get("tags", {})  # Include existing 'tags'
    }

    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}?api-version=2024-10-01"
    response = await azureLightClient.put(endpoint, payload)
    return response
