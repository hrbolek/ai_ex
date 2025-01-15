from .AzureLightClient import AzureLightClient

from ._desc import (
    RESOURCE_GROUP_NAME,
    LOCATION
)

# async def read_cognitive_services_account_keys(
#     azureLightClient: AzureLightClient, 
#     subscription_id, 
#     RESOURCE_GROUP_NAME, 
#     OPENAI_ACCOUNT_NAME
# ):
#     """
#     Retrieve the endpoint and API keys for the Cognitive Services account.

#     :param azureLightClient: Instance of AzureLightClient.
#     :param subscription_id: Azure Subscription ID.
#     :param RESOURCE_GROUP_NAME: Name of the resource group.
#     :param OPENAI_ACCOUNT_NAME: Name of the Cognitive Services account.
#     :return: Endpoint and keys for the Cognitive Services account.
#     """
#     # Fetch account details to get the endpoint
#     account_endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}?api-version=2024-10-01"
#     # account_endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}?api-version=2024-10-01"

#     account_response = await azureLightClient.get(account_endpoint)
#     if not isinstance(account_response, dict):
#         return account_response
#     print(f"read_cognitive_services_account_keys\n{account_response}")
#     endpoint = account_response.get("properties", {}).get("endpoint", "Unknown")

#     # Fetch API keys
#     keys_endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}/listKeys?api-version=2024-10-01"
#     keys_response = await azureLightClient.post(keys_endpoint, {})
#     print(f"read_cognitive_services_account_keys\n{account_response}")
#     keys = keys_response.get("key1"), keys_response.get("key2")

#     return endpoint, keys

async def read_cognitive_services_account_keys(
    azureLightClient: AzureLightClient, 
    subscription_id: str, 
    RESOURCE_GROUP_NAME: str, 
    OPENAI_ACCOUNT_NAME: str
):
    """
    Retrieve the endpoint and keys for an Azure Cognitive Services account.
    """
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}?api-version=2024-10-01"

    print(f"Fetching Cognitive Services account details: {OPENAI_ACCOUNT_NAME}...")
    response = await azureLightClient.get(endpoint)

    if isinstance(response, dict) and "properties" in response:
        properties = response["properties"]
        endpoint_url = properties.get("endpoint")
        print(f"Retrieved endpoint: {endpoint_url}")
        
        keys_endpoint = f"{endpoint}/listKeys?api-version=2024-10-01"
        keys_endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}/listKeys?api-version=2024-10-01"
        print(f"Fetching keys for Cognitive Services account: {OPENAI_ACCOUNT_NAME}...")
        keys_response = await azureLightClient.post(keys_endpoint, {})

        if isinstance(keys_response, dict) and "key1" in keys_response:
            keys = [keys_response["key1"], keys_response.get("key2")]
            return endpoint_url, keys
        else:
            raise Exception(f"Failed to fetch keys: {keys_response}")
    else:
        raise Exception(f"Failed to fetch account properties: {response}")