import asyncio
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
from _desc import AzureLightClient

credential = DefaultAzureCredential()
token = credential.get_token("https://management.azure.com/.default").token
azureLightClient = AzureLightClient("https://portal.azure.com", token=token)

subscription_client = SubscriptionClient(credential)

def first_subscription(subscription_client=subscription_client):
    """
    List all Azure subscriptions in your account.
    """
    # Authenticate using Default Azure credentials

    # print("Listing Azure Subscriptions:\n")
    for subscription in subscription_client.subscriptions.list():
        print(f"{subscription.as_dict()}")
        return subscription
        # print(f"Subscription Name: {subscription.display_name}")
        # print(f"Subscription ID: {subscription.subscription_id}")
        # print(f"State: {subscription.state}")
        # print("-" * 40)

async def subscription(azureLightClient=azureLightClient):
    async with azureLightClient as alc:
        response = await alc.get(endpoint="/subscriptions?api-version=2020-01-01")
        subscriptions = response.get("value", [])
        assert len(subscriptions) > 0, "No subscriptions are available"
        subscription = subscriptions[0]
        # subscription['subscriptionId']
        return subscription
    

# subscription = first_subscription()

# Initialize Azure clients
# SUBSCRIPTION_ID = subscription["subscription_id"]
# resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
# storage_client = StorageManagementClient(credential, SUBSCRIPTION_ID)
# cognitive_services_client = CognitiveServicesManagementClient(credential, SUBSCRIPTION_ID)

# # this is only sync
# search_client = SearchManagementClient(credential, SUBSCRIPTION_ID)


# Create Resource Group (if not exists)
# def create_resource_group(resource_client=resource_client, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, LOCATION=LOCATION):
#     print("Creating resource group...")
#     try:
#         resource_client.resource_groups.create_or_update(
#             RESOURCE_GROUP_NAME,
#             {"location": LOCATION}
#         )
#     except Exception as e:
#         print(f"exception happened {e}")

async def create_resource_group(azureLightClient: AzureLightClient, subscription_id: str, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, LOCATION=LOCATION):
    """
    Asynchronously create or update a resource group in Azure.

    This function uses the Azure REST API to create or update a resource group 
    with the specified name and location under the given subscription.

    :param azureLightClient: An instance of AzureLightClient for making API calls.
    :param subscription_id: The Azure subscription ID where the resource group will be created.
    :param RESOURCE_GROUP_NAME: The name of the resource group to create or update. Defaults to a global constant.
    :param LOCATION: The Azure region for the resource group (e.g., "Sweden Central"). Defaults to a global constant.

    :returns: The raw response from the Azure REST API.
    :rtype: dict or str (depending on the API response)
    """
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}?api-version=2021-04-01"
    payload = {
        "location": LOCATION
    }

    response = await azureLightClient.put(endpoint, payload)
    return response

        

# Create Storage Account
# def create_storage_account(storage_client=storage_client, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, LOCATION=LOCATION, STORAGE_ACCOUNT_NAME=STORAGE_ACCOUNT_NAME):
#     print("Creating storage account...")
#     try:
#         storage_client.storage_accounts.begin_create(
#             RESOURCE_GROUP_NAME,
#             STORAGE_ACCOUNT_NAME,
#             {
#                 "location": LOCATION,
#                 "sku": {"name": "Standard_LRS"},
#                 "kind": "StorageV2",
#                 "properties": {
#                     "accessTier": "Hot",
#                     "enableHttpsTrafficOnly": True
#                 }
#             }
#         ).result()
#     except Exception as e:
#         print(f"exception happened {e}")


# Create Cognitive Services Account
# def create_cognitive_services_account(cognitive_services_client=cognitive_services_client, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, LOCATION=LOCATION, OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME):
#     print("Creating Cognitive Services account...")
#     try:
#         cognitive_services_client.accounts.begin_create(
#             RESOURCE_GROUP_NAME,
#             OPENAI_ACCOUNT_NAME,
#             {
#                 "location": LOCATION,
#                 "sku": {"name": "S0"},
#                 "kind": "OpenAI",
#                 "properties": {
#                     "networkAcls": {"defaultAction": "Allow"},
#                     "publicNetworkAccess": "Enabled",
#                 },
#                 "tags": {"Vlastník": "Stefek"}
#             }
#         ).result()
#     except Exception as e:
#         print(f"exception happened {e}")

async def create_storage_account(azureLightClient: AzureLightClient, subscription_id: str, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, LOCATION=LOCATION, STORAGE_ACCOUNT_NAME=STORAGE_ACCOUNT_NAME):
    """
    Asynchronously create a storage account in Azure.

    This function uses the Azure REST API to create a storage account 
    with the specified name, location, and configuration in a resource group.

    :param azureLightClient: An instance of AzureLightClient for making API calls.
    :param subscription_id: The Azure subscription ID where the storage account will be created.
    :param RESOURCE_GROUP_NAME: The name of the resource group where the storage account will be created.
    :param LOCATION: The Azure region for the storage account (e.g., "Sweden Central").
    :param STORAGE_ACCOUNT_NAME: The name of the storage account to create.

    :returns: The raw response from the Azure REST API.
    :rtype: dict or str (depending on the API response)
    """
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.Storage/storageAccounts/{STORAGE_ACCOUNT_NAME}?api-version=2022-09-01"
    payload = {
        "location": LOCATION,
        "sku": {"name": "Standard_LRS"},
        "kind": "StorageV2",
        "properties": {
            "accessTier": "Hot",
            "enableHttpsTrafficOnly": True
        }
    }

    response = await azureLightClient.put(endpoint, payload)
    return response

# Create Azure Search Service
# def create_search_service(search_client=search_client, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, LOCATION=LOCATION, SEARCH_SERVICE_NAME=SEARCH_SERVICE_NAME):
#     print("Creating search service...")
#     try:
#         # search_client.services.begin_create_or_update(#semantic_configs.create_or_update(
#         #     resource_group_name=RESOURCE_GROUP_NAME,
#         #     search_service_name=SEARCH_SERVICE_NAME,
#         #     semantic_config_name="default",
#         #     semantic_config={
#         #         "name": "default",
#         #         "prioritizedFields": {
#         #             "titleField": {"fieldName": "title"},
#         #             "contentFields": [{"fieldName": "content"}],
#         #             "keywordsField": {"fieldName": "tags"}
#         #         }
#         #     }
#         # ).result()  
#         search_client.services.begin_create_or_update(
#             RESOURCE_GROUP_NAME,
#             SEARCH_SERVICE_NAME,
#             {
#                 "location": LOCATION,
#                 "sku": {"name": "basic"},
#                 "replica_count": 1,
#                 "partition_count": 1,
#                 "publicNetworkAccess": "Enabled",
#                 "tags": {"ProjectType": "semantic-search"}
#             }
#         ).result()

#         # Semantic configuration (ensure service exists first)
#         # search_client.semantic_configs.create_or_update(
#         #     resource_group_name=RESOURCE_GROUP_NAME,
#         #     search_service_name=SEARCH_SERVICE_NAME,
#         #     semantic_config_name="default",
#         #     semantic_config={
#         #         "name": "default",
#         #         "prioritizedFields": {
#         #             "titleField": {"fieldName": "title"},
#         #             "contentFields": [{"fieldName": "content"}],
#         #             "keywordsField": {"fieldName": "tags"}
#         #         }
#         #     }
#         # )        
#     except Exception as e:
#         print(f"exception happened {e}")

async def create_search_service(azureLightClient: AzureLightClient, subscription_id: str, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, LOCATION=LOCATION, SEARCH_SERVICE_NAME=SEARCH_SERVICE_NAME):
    """
    Asynchronously create an Azure Search Service.

    This function uses the Azure REST API to create or update an Azure Search Service 
    with the specified configuration in a resource group.

    :param azureLightClient: An instance of AzureLightClient for making API calls.
    :param subscription_id: The Azure subscription ID where the search service will be created.
    :param RESOURCE_GROUP_NAME: The name of the resource group where the search service will be created.
    :param LOCATION: The Azure region for the search service (e.g., "Sweden Central").
    :param SEARCH_SERVICE_NAME: The name of the search service to create.

    :returns: The raw response from the Azure REST API.
    :rtype: dict or str (depending on the API response)
    """
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.Search/searchServices/{SEARCH_SERVICE_NAME}?api-version=2024-06-01-Preview"
    payload = {
        "location": LOCATION,
        "sku": {"name": "basic"},
        "properties": {
            "replicaCount": 1,
            "partitionCount": 1,
            "publicNetworkAccess": "Enabled"
        },
        "tags": {"ProjectType": "semantic-search"}
    }

    response = await azureLightClient.put(endpoint, payload)
    return response


def add_semantic_configuration(index_name):
    """
    Add semantic configuration to an index in Azure Cognitive Search.
    """
    print("Adding semantic configuration...")
    SEARCH_SERVICE_ENDPOINT = f"https://{SEARCH_SERVICE_NAME}.search.windows.net"

    # Define Semantic Configuration
    semantic_config_name = "default"
    semantic_config = SemanticConfiguration(
        name=semantic_config_name,
        prioritized_fields={
            "titleField": {"fieldName": "title"},
            "contentFields": [{"fieldName": "content"}],
            "keywordsField": {"fieldName": "tags"},
        }
    )
    # Add the Semantic Configuration to an Existing Index
    try:
        # Fetch the existing index
        index = index_client.get_index(index_name)

        # Add semantic settings
        index.semantic_settings = SemanticSettings(configurations=[semantic_config])

        # Update the index
        index_client.create_or_update_index(index)

        print(f"Semantic configuration '{semantic_config_name}' successfully added to index '{index_name}'.")
    except Exception as e:
        print(f"Error configuring semantic search: {e}")

def create_search_client():
    SEARCH_SERVICE_ENDPOINT = f"https://{SEARCH_SERVICE_NAME}.search.windows.net"
    # Initialize the SearchClient
    search_client = SearchClient(endpoint=SEARCH_SERVICE_ENDPOINT, index_name=SEARCH_SERVICE_NAME, credential=credential)

    # Example operation: Search for a term
    results = search_client.search(query="example query")
    for result in results:
        print(result)    

# Deploy GPT-4 Deployment
# def deploy_gpt4(cognitive_services_client=cognitive_services_client, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME):
#     print("Deploying GPT-4...")
#     try:
#         cognitive_services_client.deployments.create_or_update(
#             RESOURCE_GROUP_NAME,
#             OPENAI_ACCOUNT_NAME,
#             "gpt-4-32k",
#             {
#                 "sku": {"name": "Standard", "capacity": 30},
#                 "properties": {
#                     "model": {"format": "OpenAI", "name": "gpt-4-32k", "version": "0613"},
#                     "versionUpgradeOption": "OnceNewDefaultVersionAvailable",
#                     "currentCapacity": 30,
#                     "raiPolicyName": "Microsoft.DefaultV2"
#                 }
#             }
#         )
#     except Exception as e:
#         print(f"exception happened {e}")

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

# Deploy Text Embedding Deployment
# def deploy_text_embedding(cognitive_services_client=cognitive_services_client, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME):
#     print("Deploying Text Embedding Model...")
#     try:
#         cognitive_services_client.deployments.create_or_update(
#             RESOURCE_GROUP_NAME,
#             OPENAI_ACCOUNT_NAME,
#             "text-embedding-ada-002",
#             {
#                 "sku": {"name": "Standard", "capacity": 120},
#                 "properties": {
#                     "model": {"format": "OpenAI", "name": "text-embedding-ada-002", "version": "2"},
#                     "versionUpgradeOption": "OnceNewDefaultVersionAvailable",
#                     "currentCapacity": 120,
#                     "raiPolicyName": "Microsoft.DefaultV2"
#                 }
#             }
#         )
#     except Exception as e:
#         print(f"exception happened {e}")

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

# async def create_cognitive_services_account_async(
#     cognitive_services_client=cognitive_services_client, RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME, LOCATION=LOCATION
# ):
#     """
#     Create a Cognitive Services account asynchronously.
#     """
#     print(f"Creating Cognitive Services account: {OPENAI_ACCOUNT_NAME}...")
#     poller = await cognitive_services_client.accounts.begin_create(
#         RESOURCE_GROUP_NAME,
#         OPENAI_ACCOUNT_NAME,
#         {
#             "location": LOCATION,
#             "sku": {"name": "S0"},
#             "kind": "OpenAI",
#             "properties": {
#                 "networkAcls": {"defaultAction": "Allow"},
#                 "publicNetworkAccess": "Enabled",
#             },
#             "tags": {"Owner": "Stefek"},
#         },
#     )
#     account = await poller.result()
#     print(f"Cognitive Services account '{OPENAI_ACCOUNT_NAME}' created.")
#     return account

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
        "tags": {"Owner": "Stefek"}
    }

    # print(f"Creating Cognitive Services account: {OPENAI_ACCOUNT_NAME}...")
    response = await azureLightClient.put(endpoint, payload)
    # print(f"Cognitive Services account '{OPENAI_ACCOUNT_NAME}' created.")
    return response

# async def deploy_model_async(
#     cognitive_services_client=cognitive_services_client, 
#     RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, 
#     OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME, 
#     deployment_name=None, 
#     model_name=None, 
#     sku_capacity=None
# ):
#     """
#     Deploy a model asynchronously in Cognitive Services.
#     """
#     print(f"Deploying model '{model_name}' as '{deployment_name}'...")
#     poller = await cognitive_services_client.deployments.begin_create_or_update(
#         RESOURCE_GROUP_NAME,
#         OPENAI_ACCOUNT_NAME,
#         deployment_name,
#         {
#             "sku": {"name": "Standard", "capacity": sku_capacity},
#             "properties": {
#                 "model": {"format": "OpenAI", "name": model_name, "version": "latest"},
#                 "versionUpgradeOption": "OnceNewDefaultVersionAvailable",
#                 "currentCapacity": sku_capacity,
#                 "raiPolicyName": "Microsoft.DefaultV2",
#             },
#         },
#     )
#     deployment = await poller.result()
#     print(f"Model '{model_name}' deployed as '{deployment_name}'.")
#     return deployment

async def deploy_model_async(
    azureLightClient: AzureLightClient, 
    subscription_id: str, 
    RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, 
    OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME, 
    deployment_name=None, 
    model_name=None, 
    sku_capacity=None
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

    :returns: The response from the Azure REST API.
    :rtype: dict or str (depending on the API response)
    """
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}/deployments/{deployment_name}?api-version=2022-12-01"
    payload = {
        "sku": {"name": "Standard", "capacity": sku_capacity},
        "properties": {
            "model": {"format": "OpenAI", "name": model_name, "version": "latest"},
            "versionUpgradeOption": "OnceNewDefaultVersionAvailable",
            "currentCapacity": sku_capacity,
            "raiPolicyName": "Microsoft.DefaultV2"
        }
    }

    # print(f"Deploying model '{model_name}' as '{deployment_name}'...")
    response = await azureLightClient.put(endpoint, payload)
    # print(f"Model '{model_name}' deployed as '{deployment_name}'.")
    return response

# Main execution
async def main():
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

        # Step 3: Create the Azure Cognitive Search service
        print("\nStep 3: Creating Azure Cognitive Search Service...")
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

        # # Step 4: Deploy Cognitive Services models
        # print("\nStep 4: Deploying Cognitive Services Models...")
        # try:
        #     deployment_results = await asyncio.gather(
        #         deploy_model_async(
        #             azureLightClient=azure_client,
        #             subscription_id=subscription_id,
        #             RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
        #             OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME,
        #             deployment_name="gpt-4-32k",
        #             model_name="gpt-4-32k",
        #             sku_capacity=30
        #         ),
        #         deploy_model_async(
        #             azureLightClient=azure_client,
        #             subscription_id=subscription_id,
        #             RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
        #             OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME,
        #             deployment_name="text-embedding-ada-002",
        #             model_name="text-embedding-ada-002",
        #             sku_capacity=120
        #         )
        #     )
        #     print(f"Model deployments completed successfully: {deployment_results}")
        # except Exception as e:
        #     print(f"Model deployment failed: {e}")
        #     raise

        print("\nAll resources and models have been deployed successfully!")


if __name__ == "__main__":
    asyncio.run(main())