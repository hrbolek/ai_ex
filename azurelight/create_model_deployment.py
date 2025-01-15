from .AzureLightClient import AzureLightClient

from ._desc import (
    RESOURCE_GROUP_NAME,
    OPENAI_ACCOUNT_NAME
)

async def create_model_deployment(
    azureLightClient: AzureLightClient, 
    subscription_id: str, 
    RESOURCE_GROUP_NAME: str, 
    OPENAI_ACCOUNT_NAME: str, 
    deployment_name: str, 
    model_name: str, 
    sku_capacity: int, 
    model_version: str = "latest"
):
    """
    Deploy a model asynchronously in Cognitive Services using the Azure REST API.

    :param azureLightClient: An instance of AzureLightClient for making API calls.
    :param subscription_id: The Azure subscription ID where the deployment will be created.
    :param RESOURCE_GROUP_NAME: The name of the resource group containing the Cognitive Services account.
    :param OPENAI_ACCOUNT_NAME: The name of the Cognitive Services account where the model will be deployed.
    :param deployment_name: The name of the deployment to create or update.
    :param model_name: The name of the model to deploy (e.g., "gpt-4-32k").
    :param sku_capacity: The capacity (e.g., number of instances) to allocate for the deployment.
    :param model_version: The version of the model to deploy.
    :returns: The response from the Azure REST API.
    :rtype: dict or str (depending on the API response)
    """
    endpoint = (
        f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/"
        f"providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}/"
        f"deployments/{deployment_name}?api-version=2024-10-01"
    )
    payload = {
        "sku": {"name": "Standard", "capacity": sku_capacity},
        "properties": {
            "model": {"format": "OpenAI", "name": model_name, "version": model_version},
            "versionUpgradeOption": "OnceNewDefaultVersionAvailable",
            "currentCapacity": sku_capacity,
            "raiPolicyName": "Microsoft.DefaultV2"
        }
    }

    print(f"Deploying model '{model_name}' as '{deployment_name}' with payload:\n{payload}")
    
    try:
        response = await azureLightClient.put(endpoint, payload)
        print(f"Model '{model_name}' deployed as '{deployment_name}'. Response:\n{response}")
        return response
    except Exception as e:
        print(f"Failed to deploy model '{model_name}' as '{deployment_name}': {e}")
        raise
