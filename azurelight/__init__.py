import asyncio
import aiohttp

import shutil
print(shutil.which("az"))

from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential

from azure.mgmt.resource import SubscriptionClient, ResourceManagementClient
from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
# from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.aio import CognitiveServicesManagementClient
from azure.mgmt.search import SearchManagementClient

from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
# from azure.search.documents.indexes.models import SemanticConfiguration, SemanticSettings


from _desc import (
    RESOURCE_GROUP_NAME,
    STORAGE_ACCOUNT_NAME,
    LOCATION,
    SEARCH_SERVICE_NAME,
    OPENAI_ACCOUNT_NAME
)
from .AzureLightClient import AzureLightClient

credential = DefaultAzureCredential()
token = credential.get_token("https://management.azure.com/.default").token
azureLightClient = AzureLightClient("https://portal.azure.com", token=token)

subscription_client = SubscriptionClient(credential)

async def subscription(azureLightClient=azureLightClient):
    async with azureLightClient as alc:
        response = await alc.get(endpoint="/subscriptions?api-version=2020-01-01")
        subscriptions = response.get("value", [])
        assert len(subscriptions) > 0, "No subscriptions are available"
        subscription = subscriptions[0]
        # subscription['subscriptionId']
        return subscription
    

from .create_resource_group import create_resource_group
from .create_storage_account import create_storage_account
from .create_search_service import create_search_service
from .create_cognitive_services_account_async import create_cognitive_services_account_async
from .read_model_list import read_model_list
from .create_model_deployment import create_model_deployment
from .update_network_access_public import update_network_access_public
from .read_cognitive_services_account_keys import read_cognitive_services_account_keys
from .createAIClient import createAIClient
from .create_all import create_all
from .delete_all import delete_all
from .read_subscription import read_subscription


# def add_semantic_configuration(index_name):
#     """
#     Add semantic configuration to an index in Azure Cognitive Search.
#     """
#     print("Adding semantic configuration...")
#     SEARCH_SERVICE_ENDPOINT = f"https://{SEARCH_SERVICE_NAME}.search.windows.net"

#     # Define Semantic Configuration
#     semantic_config_name = "default"
#     semantic_config = SemanticConfiguration(
#         name=semantic_config_name,
#         prioritized_fields={
#             "titleField": {"fieldName": "title"},
#             "contentFields": [{"fieldName": "content"}],
#             "keywordsField": {"fieldName": "tags"},
#         }
#     )
#     # Add the Semantic Configuration to an Existing Index
#     try:
#         # Fetch the existing index
#         index = index_client.get_index(index_name)

#         # Add semantic settings
#         index.semantic_settings = SemanticSettings(configurations=[semantic_config])

#         # Update the index
#         index_client.create_or_update_index(index)

#         print(f"Semantic configuration '{semantic_config_name}' successfully added to index '{index_name}'.")
#     except Exception as e:
#         print(f"Error configuring semantic search: {e}")

# def create_search_client():
#     SEARCH_SERVICE_ENDPOINT = f"https://{SEARCH_SERVICE_NAME}.search.windows.net"
#     # Initialize the SearchClient
#     search_client = SearchClient(endpoint=SEARCH_SERVICE_ENDPOINT, index_name=SEARCH_SERVICE_NAME, credential=credential)

#     # Example operation: Search for a term
#     results = search_client.search(query="example query")
#     for result in results:
#         print(result)    


# Main execution
async def deploy(
    RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
    LOCATION=LOCATION,
    STORAGE_ACCOUNT_NAME=STORAGE_ACCOUNT_NAME,
    SEARCH_SERVICE_NAME=SEARCH_SERVICE_NAME,
    OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME
):
    """
    Orchestrates the creation of Azure resources and model deployments in a sequence.
    """
    credential = DefaultAzureCredential()
    # Acquire a token for Azure Management API
    token = credential.get_token("https://management.azure.com/.default").token

    # Base URL for Azure Management API
    base_url = "https://management.azure.com"
    async with AzureLightClient(base_url, token) as azure_client:
        # Step 0: Pick up the subscription
        print("Step 0: Retrieving subscription information...")
        subscriptionDict = await subscription(azureLightClient=azure_client)
        subscription_id = subscriptionDict["subscriptionId"]
        print(f"Using Subscription ID: {subscription_id}")

        # Step 1: Create the resource group
        print("\nStep 1: Creating Resource Group...")
        resource_group_result = await create_resource_group(
            azureLightClient=azure_client,
            subscription_id=subscription_id,
            RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
            LOCATION=LOCATION
        )
        print(f"{type(resource_group_result)}", resource_group_result)
        assert isinstance(resource_group_result, dict), f"Resource Group creation failed: {resource_group_result}"
        print(f"Resource Group '{RESOURCE_GROUP_NAME}' in location '{LOCATION}' created successfully.")

        # Step 2: Create the storage account
        print("\nStep 2: Creating Storage Account...")
        storage_account_result = await create_storage_account(
            azureLightClient=azure_client,
            subscription_id=subscription_id,
            RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
            STORAGE_ACCOUNT_NAME=STORAGE_ACCOUNT_NAME,
            LOCATION=LOCATION
        )
        print(f"storage_account_result={storage_account_result}")
        assert isinstance(storage_account_result, dict), f"Storage Account creation failed: {storage_account_result}"
        print(f"Storage Account '{STORAGE_ACCOUNT_NAME}' in Resource Group '{RESOURCE_GROUP_NAME}' created successfully.")

        # Step 3.0: Create the Azure Cognitive Search service
        print("\nStep 3.0: Creating Azure Cognitive Search Service...")
        search_service_result = await create_search_service(
            azureLightClient=azure_client,
            subscription_id=subscription_id,
            RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
            SEARCH_SERVICE_NAME=SEARCH_SERVICE_NAME,
            LOCATION=LOCATION
        )
        print(f"storage_account_result={search_service_result}")
        assert isinstance(search_service_result, dict), f"Search Service creation failed: {search_service_result}"
        print(f"Search Service '{SEARCH_SERVICE_NAME}' in Resource Group '{RESOURCE_GROUP_NAME}' created successfully.")

        # Step 3.1: Create Cognitive Services Account
        print("\nStep 3.1: Creating Cognitive Services Account...")
        services_account_result = await create_cognitive_services_account_async(
            azureLightClient=azure_client,
            subscription_id=subscription_id,
            RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
            OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME,
            LOCATION=LOCATION
        )
        print(f"services_account_result={services_account_result}")
        assert isinstance(services_account_result, dict), f"Cognitive Services Account creation failed: {services_account_result}"
        print(f"Cognitive Services Account '{OPENAI_ACCOUNT_NAME}' in Resource Group '{RESOURCE_GROUP_NAME}' created successfully.")


        # Step 3.2: Enable Public Access
        print("\nStep 3.2: Enabling Public Access...")
        network_access_result = update_network_access_public(azureLightClient, subscription_id, RESOURCE_GROUP_NAME, OPENAI_ACCOUNT_NAME)
        print(f"network_access_result={network_access_result}")
        assert isinstance(network_access_result, dict), f"Enable Public Access failed: {network_access_result}"
        print(f"Enable Public Access for '{OPENAI_ACCOUNT_NAME}' in Resource Group '{RESOURCE_GROUP_NAME}' finished successfully.")


        # Step 3.3: Get API Keys
        print("\nStep 3.3: Getting API Keys...")
        account_keys = read_cognitive_services_account_keys(azureLightClient, subscription_id, RESOURCE_GROUP_NAME, OPENAI_ACCOUNT_NAME)
        assert isinstance(account_keys, tuple), f"Getting API Keys failed: {account_keys}"
        endpoint, keys = account_keys
        print(f"Getting API Keys for '{OPENAI_ACCOUNT_NAME}' in Resource Group '{RESOURCE_GROUP_NAME}' finished successfully.")
        print(f"endpoint = {endpoint}")
        print(f"keys = {keys}")

        # Step 4.0: Deploy Cognitive Services models
        print("\nStep 4.0: Deploying Cognitive Services Models...")
        models_result = await read_model_list(
            azureLightClient=azure_client,
            subscription_id=subscription_id,
            RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
            OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME
        )
        print(f"models_result={models_result}")
        assert isinstance(models_result, dict), f"Cognitive Services Account creation failed: {models_result}"
        print(f"List models '{OPENAI_ACCOUNT_NAME}' in Resource Group '{RESOURCE_GROUP_NAME}' read successfully.")
        models = models_result["value"]
        for model in models:
            print(f"{model['name']}")

        # Step 4.1: Deploy Cognitive Services models
        print("\nStep 4.1: Deploying Cognitive Services Models...")
        try:
            deployment_results = await asyncio.gather(
                create_model_deployment(
                    azureLightClient=azure_client,
                    subscription_id=subscription_id,
                    RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
                    OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME,
                    deployment_name="gpt-4-32k",
                    model_name="gpt-4-32k",
                    sku_capacity=30,
                    model_version="0613"  # matches the working CLI call
                ),
                create_model_deployment(
                    azureLightClient=azure_client,
                    subscription_id=subscription_id,
                    RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
                    OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME,
                    deployment_name="text-embedding-ada-002",
                    model_name="text-embedding-ada-002",
                    sku_capacity=120,
                    model_version="2"  # matches the working CLI call
                )
            )
            print(f"Model deployments completed successfully: {deployment_results}")
        except Exception as e:
            print(f"Model deployment failed: {e}")
            raise

        print("\nAll resources and models have been deployed successfully!")


        
if __name__ == "__main__":
    asyncio.run(deploy())