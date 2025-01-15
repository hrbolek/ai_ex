from .AzureLightClient import AzureLightClient

from ._desc import (
    RESOURCE_GROUP_NAME,
    OPENAI_ACCOUNT_NAME
)

async def deploy_gpt4(azureLightClient: AzureLightClient, subscription_id: str, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME):
    """
    Asynchronously deploy the GPT-4 model in an Azure Cognitive Services account.

    This function uses the Azure REST API to deploy the GPT-4 model.

    :param azureLightClient: An instance of AzureLightClient for making API calls.
    :param subscription_id: The Azure subscription ID where the deployment will occur.
    :param RESOURCE_GROUP_NAME: The name of the resource group containing the Cognitive Services account.
    :param OPENAI_ACCOUNT_NAME: The name of the Cognitive Services account where GPT-4 will be deployed.

    :returns: The raw response from the Azure REST API.
    :rtype: dict or str (depending on the API response)
    """
    deployment_name = "gpt-4-32k"
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}/deployments/{deployment_name}?api-version=2022-12-01"
    payload = {
        "sku": {"name": "Standard", "capacity": 30},
        "properties": {
            "model": {"format": "OpenAI", "name": "gpt-4-32k", "version": "0613"},
            "versionUpgradeOption": "OnceNewDefaultVersionAvailable",
            "currentCapacity": 30,
            "raiPolicyName": "Microsoft.DefaultV2"
        }
    }

    response = await azureLightClient.put(endpoint, payload)
    return response
