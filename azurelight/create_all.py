import asyncio

from .create_resource_group import create_resource_group
from .create_storage_account import create_storage_account
from .create_search_service import create_search_service
from .create_cognitive_services_account_async import create_cognitive_services_account_async
from .read_model_list import read_model_list
from .create_model_deployment import create_model_deployment
from .update_network_access_public import update_network_access_public
from .read_cognitive_services_account_keys import read_cognitive_services_account_keys
from .AzureLightClient import AzureLightClient
from .createAIClient import createAIClient

from ._desc import (
    RESOURCE_GROUP_NAME,
    LOCATION,
    STORAGE_ACCOUNT_NAME,
    SEARCH_SERVICE_NAME,
    OPENAI_ACCOUNT_NAME
)

async def create_all(
    azureLightClient: AzureLightClient,
    subscription_id: str,
    RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
    LOCATION=LOCATION,
    STORAGE_ACCOUNT_NAME=STORAGE_ACCOUNT_NAME,
    SEARCH_SERVICE_NAME=SEARCH_SERVICE_NAME,
    OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME
):
    """
    Orchestrates the creation of Azure resources and model deployments in a sequence.
    """

    # Step 1: Create the resource group
    print("\nStep 1: Creating Resource Group...")
    resource_group_result = await create_resource_group(
        azureLightClient=azureLightClient,
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
        azureLightClient=azureLightClient,
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
        azureLightClient=azureLightClient,
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
        azureLightClient=azureLightClient,
        subscription_id=subscription_id,
        RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
        OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME,
        LOCATION=LOCATION
    )
    print(f"services_account_result={services_account_result}")
    assert isinstance(services_account_result, dict), f"Cognitive Services Account creation failed: {services_account_result}"
    print(f"Cognitive Services Account '{OPENAI_ACCOUNT_NAME}' in Resource Group '{RESOURCE_GROUP_NAME}' created successfully.")

    # Step 3.2: Create Search Index
    # create_search_index()  

    # Step 3.2.1 Get API Key
    # read_search_service_keys()

    # Step 3.3 Upload / create documents
    # create_documents()

    # Step 3.4 Updare / configure search service
    # update_semantic_search()

    # Step 3.5 Read / query index
    # read_semantic_search()

    # # Step 3.2: Enable Public Access
    # print("\nStep 3.2: Enabling Public Access...")
    # network_access_result = await update_network_access_public(
    #     azureLightClient=azureLightClient, 
    #     subscription_id=subscription_id, 
    #     RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME, 
    #     OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME,
    #     LOCATION=LOCATION
    # )
    # print(f"network_access_result={network_access_result}")
    # assert isinstance(network_access_result, dict), f"Enable Public Access failed: {network_access_result}"
    # print(f"Enable Public Access for '{OPENAI_ACCOUNT_NAME}' in Resource Group '{RESOURCE_GROUP_NAME}' finished successfully.")


    # Step 3.3: Get API Keys
    print("\nStep 3.3: Getting API Keys...")
    account_keys = await read_cognitive_services_account_keys(azureLightClient, subscription_id, RESOURCE_GROUP_NAME, OPENAI_ACCOUNT_NAME)
    assert isinstance(account_keys, tuple), f"Getting API Keys failed: {account_keys}"
    endpoint, keys = account_keys
    print(f"Getting API Keys for '{OPENAI_ACCOUNT_NAME}' in Resource Group '{RESOURCE_GROUP_NAME}' finished successfully.")
    print(f"endpoint = {endpoint}")
    print(f"keys = {keys}")

    # Step 4.0: Deploy Cognitive Services models
    print("\nStep 4.0: Deploying Cognitive Services Models...")
    models_result = await read_model_list(
        azureLightClient=azureLightClient,
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
                azureLightClient=azureLightClient,
                subscription_id=subscription_id,
                RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
                OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME,
                deployment_name="gpt-4-32k",
                model_name="gpt-4-32k",
                sku_capacity=30,
                model_version="0613"  # matches the working CLI call
            ),
            create_model_deployment(
                azureLightClient=azureLightClient,
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

    result_tuple = await read_cognitive_services_account_keys(
        azureLightClient=azureLightClient,
        subscription_id=subscription_id,
        RESOURCE_GROUP_NAME=RESOURCE_GROUP_NAME,
        OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME
    )

    assert isinstance(result_tuple, tuple), f"error while creating key"
    ENDPOINT, keys = result_tuple
    print(f"ENDPOINT={ENDPOINT}")
    print(f"keys={keys}")
    # ENDPOINT = "https://swedencentral.api.cognitive.microsoft.com/openai/deployments/gpt-4-32k/chat/completions?api-version=2024-08-01-preview"
    aiClient = createAIClient(
        ENDPOINT=ENDPOINT,
        DEPLOYMENT_NAME="gpt-4-32k",
        API_KEY=keys[0]
    )

    prompt_result = await aiClient("tell me a joke")
    print(prompt_result)
    prompt_result = await aiClient("repeat that joke")
    print(prompt_result)
    print("\nAll resources and models have been deployed successfully!")
