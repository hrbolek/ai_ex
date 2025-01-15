import urllib
from .AzureLightClient import AzureLightClient

async def purge_deleted_account(
    azureLightClient: AzureLightClient, 
    subscription_id: str, 
    LOCATION: str, 
    OPENAI_ACCOUNT_NAME: str
):
    """
    Purge a soft-deleted Cognitive Services account using AzureLightClient.

    :param azureLightClient: Instance of AzureLightClient.
    :param subscription_id: Azure Subscription ID.
    :param location: The Azure location where the account was created.
    :param account_name: The name of the Cognitive Services account to purge.
    :return: Response from the Azure REST API for the purge operation.
    """
    # LOCATIONwospaces = LOCATION.replace(" ", "%20")
    LOCATIONwospaces = LOCATION.replace(" ", "")
    # URL-encode the LOCATION value
    encoded_location = urllib.parse.quote(LOCATION)
    endpoint = f"/subscriptions/{subscription_id}/providers/Microsoft.CognitiveServices/locations/{encoded_location}/deletedAccounts/{OPENAI_ACCOUNT_NAME}/purge?api-version=2024-10-01"

    print(f"Purging soft-deleted account: {OPENAI_ACCOUNT_NAME} in location: {LOCATION}...")
    response = await azureLightClient.post(endpoint, {})

    if isinstance(response, dict) and "error" in response:
        print(f"Error purging account: {response['error']}")
    else:
        print(f"response = '{response}'")
        print(f"Account '{OPENAI_ACCOUNT_NAME}' purged successfully.")

    return response