from .AzureLightClient import AzureLightClient

from ._desc import (
    RESOURCE_GROUP_NAME,
    LOCATION,
    OPENAI_ACCOUNT_NAME
)

async def create_cognitive_services_account_async(
    azureLightClient: AzureLightClient, subscription_id: str, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME, LOCATION=LOCATION
):
    """
    Asynchronously create a Cognitive Services account in Azure.

    This function uses the Azure REST API to create or update a Cognitive Services account.

    :param azureLightClient: An instance of AzureLightClient for making API calls.
    :param subscription_id: The Azure subscription ID where the account will be created.
    :param RESOURCE_GROUP_NAME: The name of the resource group to contain the Cognitive Services account.
    :param OPENAI_ACCOUNT_NAME: The name of the Cognitive Services account to be created.
    :param LOCATION: The Azure region where the account will be created (e.g., "Sweden Central").

    :returns: The raw response from the Azure REST API.
    :rtype: dict or str (depending on the API response)
    """
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}?api-version=2022-12-01"
    payload = {
        "location": LOCATION,
        "sku": {"name": "S0"},
        "kind": "OpenAI",
        "properties": {
            "networkAcls": {"defaultAction": "Allow"},
            "publicNetworkAccess": "Enabled"
        },
        # "tags": {"Owner": "Stefek"}
    }

    # print(f"Creating Cognitive Services account: {OPENAI_ACCOUNT_NAME}...")
    response = await azureLightClient.put(endpoint, payload)
    # print(f"Cognitive Services account '{OPENAI_ACCOUNT_NAME}' created.")
    return response
