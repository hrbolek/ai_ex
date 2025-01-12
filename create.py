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
from _desc import AzureLightClient

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

async def list_models(
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

async def deploy_model_async(
    azureLightClient: AzureLightClient, 
    subscription_id: str, 
    RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, 
    OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME, 
    deployment_name=None, 
    model_name=None, 
    sku_capacity=None,
    model_version="latest"
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
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}/deployments/{deployment_name}?api-version=2024-10-01"
    payload = {
        "sku": {"name": "Standard", "capacity": sku_capacity},
        "properties": {
            "model": {"format": "OpenAI", "name": model_name, "version": model_version},
            "versionUpgradeOption": "OnceNewDefaultVersionAvailable",
            "currentCapacity": sku_capacity,
            "raiPolicyName": "Microsoft.DefaultV2"
        }
    }

# payload = {
#     "sku": {"name": "Standard", "capacity": sku_capacity},
#     "properties": {
#         "model": {"format": "OpenAI", "name": model_name, "version": "0613"},
#         "versionUpgradeOption": "None",  # Update based on supported options
#         "currentCapacity": sku_capacity,
#         "raiPolicyName": "Microsoft.DefaultV2",
#     }
# }

    # print(f"Deploying model '{model_name}' as '{deployment_name}'...")
    response = await azureLightClient.put(endpoint, payload)
    # print(f"Model '{model_name}' deployed as '{deployment_name}'.")
    return response


async def enable_public_network_access(azureLightClient, subscription_id, RESOURCE_GROUP_NAME, OPENAI_ACCOUNT_NAME):
    """
    Enable public network access for the Cognitive Services account.

    :param azureLightClient: Instance of AzureLightClient.
    :param subscription_id: Azure Subscription ID.
    :param RESOURCE_GROUP_NAME: Name of the resource group.
    :param OPENAI_ACCOUNT_NAME: Name of the Cognitive Services account.
    :return: Response from the Azure REST API.
    """
    endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}?api-version=2024-10-01"

    payload = {
        "properties": {
            "publicNetworkAccess": "Enabled"
        }
    }

    response = await azureLightClient.put(endpoint, payload)
    return response


async def get_cognitive_services_account_keys(azureLightClient, subscription_id, RESOURCE_GROUP_NAME, OPENAI_ACCOUNT_NAME):
    """
    Retrieve the endpoint and API keys for the Cognitive Services account.

    :param azureLightClient: Instance of AzureLightClient.
    :param subscription_id: Azure Subscription ID.
    :param RESOURCE_GROUP_NAME: Name of the resource group.
    :param OPENAI_ACCOUNT_NAME: Name of the Cognitive Services account.
    :return: Endpoint and keys for the Cognitive Services account.
    """
    # Fetch account details to get the endpoint
    account_endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}?api-version=2024-10-01"
    account_response = await azureLightClient.get(account_endpoint)
    if not isinstance(account_response, dict):
        return account_response
    endpoint = account_response.get("properties", {}).get("endpoint", "Unknown")

    # Fetch API keys
    keys_endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}/listKeys?api-version=2024-10-01"
    keys_response = await azureLightClient.post(keys_endpoint, {})
    keys = keys_response.get("key1"), keys_response.get("key2")

    return endpoint, keys

def createClient(ENDPOINT, DEPLOYMENT_NAME, API_KEY, max_chars=3000, max_tokens=100):
    """
    Creates a context-aware client for querying the Azure OpenAI model with context trimming by character count.

    :param ENDPOINT: The endpoint of the Azure OpenAI service.
    :param DEPLOYMENT_NAME: The deployment name for the Azure OpenAI model.
    :param API_KEY: The API key for authentication.
    :param max_chars: Maximum total character count for the conversation context.
    :return: An async function that takes a prompt and returns a response.
    """
    # Maintain conversation history
    messages = [
        {"role": "system", "content": "You are an AI assistant."}
    ]

    async def client(prompt):
        """
        Query the Azure OpenAI model for a response asynchronously while maintaining context.

        :param prompt: The input prompt to send to the model.
        :return: The response from the model.
        """
        nonlocal messages  # Allows modification of the messages list
        url = f"{ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version=2024-10-01"

        headers = {
            "Content-Type": "application/json",
            "api-key": API_KEY
        }

        # Add the user prompt to the conversation history
        messages.append({"role": "user", "content": prompt})

        # Calculate the total character count of the conversation
        total_chars = sum(len(message["content"]) for message in messages)

        # Ensure the messages list does not exceed the maximum character count
        while total_chars > max_chars:
            if len(messages) > 1:  # Always keep the system message
                removed_message = messages.pop(1)  # Remove the oldest user/assistant message
                print(f"Trimming message: {removed_message['content'][:30]}... (length: {len(removed_message['content'])})")
                total_chars = sum(len(message["content"]) for message in messages)
            else:
                break

        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"POST {url} -> Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    # Extract the assistant's reply and add it to the conversation history
                    assistant_reply = data["choices"][0]["message"]["content"]
                    messages.append({"role": "assistant", "content": assistant_reply})
                    return assistant_reply
                else:
                    error_message = await response.text()
                    return f"Error: {response.status} - {error_message}"

    return client

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
        network_access_result = enable_public_network_access(azureLightClient, subscription_id, RESOURCE_GROUP_NAME, OPENAI_ACCOUNT_NAME)
        print(f"network_access_result={network_access_result}")
        assert isinstance(network_access_result, dict), f"Enable Public Access failed: {network_access_result}"
        print(f"Enable Public Access for '{OPENAI_ACCOUNT_NAME}' in Resource Group '{RESOURCE_GROUP_NAME}' finished successfully.")


        # Step 3.3: Get API Keys
        print("\nStep 3.3: Getting API Keys...")
        account_keys = get_cognitive_services_account_keys(azureLightClient, subscription_id, RESOURCE_GROUP_NAME, OPENAI_ACCOUNT_NAME)
        assert isinstance(account_keys, tuple), f"Getting API Keys failed: {account_keys}"
        endpoint, keys = account_keys
        print(f"Getting API Keys for '{OPENAI_ACCOUNT_NAME}' in Resource Group '{RESOURCE_GROUP_NAME}' finished successfully.")
        print(f"endpoint = {endpoint}")
        print(f"keys = {keys}")

        # Step 4.0: Deploy Cognitive Services models
        print("\nStep 4.0: Deploying Cognitive Services Models...")
        models_result = await list_models(
            azureLightClient=azure_client,
                subscription_id=subscription_id,
                RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
                OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME)
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
                deploy_model_async(
                    azureLightClient=azure_client,
                    subscription_id=subscription_id,
                    RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
                    OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME,
                    deployment_name="gpt-4-32k",
                    model_name="gpt-4-32k",
                    sku_capacity=30,
                    model_version="0613"  # matches the working CLI call
                ),
                deploy_model_async(
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
    asyncio.run(main())