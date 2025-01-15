from .AzureLightClient import AzureLightClient

async def read_model_list(
    azureLightClient: AzureLightClient, 
    subscription_id: str, 
    RESOURCE_GROUP_NAME: str, 
    OPENAI_ACCOUNT_NAME: str
):
    """
    List available models for a Cognitive Services account using AzureLightClient.

    :param azureLightClient: Instance of AzureLightClient.
    :param subscription_id: Azure Subscription ID.
    :param resource_group_name: Name of the resource group.
    :param account_name: Name of the Cognitive Services account.
    :return: List of available models or error response.
    """
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}/models?api-version=2024-10-01"

    print(f"Fetching models for account: {OPENAI_ACCOUNT_NAME} in resource group: {RESOURCE_GROUP_NAME}...")
    response = await azureLightClient.get(endpoint)

    if isinstance(response, dict) and "error" in response:
        print(f"Error fetching models: {response['error']}")
    else:
        print(f"Available models: {response}")

    return response
