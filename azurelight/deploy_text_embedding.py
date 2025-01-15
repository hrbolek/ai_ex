from .AzureLightClient import AzureLightClient

from ._desc import (
    RESOURCE_GROUP_NAME,
    OPENAI_ACCOUNT_NAME
)

async def deploy_text_embedding(azureLightClient: AzureLightClient, subscription_id: str, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME):
    """
    Asynchronously deploy the Text Embedding model in an Azure Cognitive Services account.

    This function uses the Azure REST API to deploy the Text Embedding model.

    :param azureLightClient: An instance of AzureLightClient for making API calls.
    :param subscription_id: The Azure subscription ID where the deployment will occur.
    :param RESOURCE_GROUP_NAME: The name of the resource group containing the Cognitive Services account.
    :param OPENAI_ACCOUNT_NAME: The name of the Cognitive Services account where the model will be deployed.

    :returns: The raw response from the Azure REST API.
    :rtype: dict or str (depending on the API response)
    """
    deployment_name = "text-embedding-ada-002"
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}/deployments/{deployment_name}?api-version=2022-12-01"
    payload = {
        "sku": {"name": "Standard", "capacity": 120},
        "properties": {
            "model": {"format": "OpenAI", "name": "text-embedding-ada-002", "version": "2"},
            "versionUpgradeOption": "OnceNewDefaultVersionAvailable",
            "currentCapacity": 120,
            "raiPolicyName": "Microsoft.DefaultV2"
        }
    }

    response = await azureLightClient.put(endpoint, payload)
    return response
