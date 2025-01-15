import asyncio

from azure.identity.aio import DefaultAzureCredential

from azurelight import deploy, create_all, AzureLightClient, read_subscription
from azurelight import (
    RESOURCE_GROUP_NAME,
    STORAGE_ACCOUNT_NAME,
    LOCATION,
    SEARCH_SERVICE_NAME,
    OPENAI_ACCOUNT_NAME
)

async def deploy():
    credential = DefaultAzureCredential()
    # Acquire a token for Azure Management API
    resource = await credential.get_token("https://management.azure.com/.default")
    token = resource.token

    # Base URL for Azure Management API
    base_url = "https://management.azure.com"
    async with AzureLightClient(base_url, token) as azure_client:

        print("Step 0: Retrieving subscription information...")
        subscriptionDict = await read_subscription(azureLightClient=azure_client)
        subscription_id = subscriptionDict["subscriptionId"]
        print(f"Using Subscription ID: {subscription_id}")

        await create_all(
            azureLightClient=azure_client,
            subscription_id=subscription_id,
            RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
            LOCATION=LOCATION,
            STORAGE_ACCOUNT_NAME=STORAGE_ACCOUNT_NAME,
            SEARCH_SERVICE_NAME=SEARCH_SERVICE_NAME,
            OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME
        )

if __name__ == "__main__":
    asyncio.run(deploy())