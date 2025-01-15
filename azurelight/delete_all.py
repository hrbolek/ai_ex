from .AzureLightClient import AzureLightClient
from .purge_deleted_account import purge_deleted_account

async def delete_all(
    azure_client: AzureLightClient,
    subscription_id: str,
    RESOURCE_GROUP_NAME: str,
    STORAGE_ACCOUNT_NAME: str,
    SEARCH_SERVICE_NAME: str,
    OPENAI_ACCOUNT_NAME: str,
    LOCATION: str
):
    """
    Deletes all resources created during deployment in reverse order.

    :param subscription_id: Azure Subscription ID.
    :param RESOURCE_GROUP_NAME: The resource group name.
    :param STORAGE_ACCOUNT_NAME: The name of the storage account.
    :param SEARCH_SERVICE_NAME: The name of the search service.
    :param OPENAI_ACCOUNT_NAME: The name of the OpenAI account.
    """
    # Step 1: Delete Cognitive Services Deployments
    print("\nStep 1: Deleting Cognitive Services Deployments...")
    deployments = ["gpt-4-32k", "text-embedding-ada-002"]
    for deployment_name in deployments:
        try:
            endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}/deployments/{deployment_name}?api-version=2024-10-01"
            response = await azure_client.delete(endpoint)
            print(f"Deleted deployment '{deployment_name}': {response}")
        except Exception as e:
            print(f"Failed to delete deployment '{deployment_name}': {e}")

    # Step 2: Delete Cognitive Services Account
    print("\nStep 2: Deleting Cognitive Services Account...")
    try:
        endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.CognitiveServices/accounts/{OPENAI_ACCOUNT_NAME}?api-version=2022-12-01"
        response = await azure_client.delete(endpoint)
        print(f"Deleted Cognitive Services Account '{OPENAI_ACCOUNT_NAME}': {response}")
    except Exception as e:
        print(f"Failed to delete Cognitive Services Account '{OPENAI_ACCOUNT_NAME}': {e}")

    # Step 3: Delete Search Service
    print("\nStep 3: Deleting Search Service...")
    try:
        endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.Search/searchServices/{SEARCH_SERVICE_NAME}?api-version=2024-06-01-Preview"
        response = await azure_client.delete(endpoint)
        print(f"Deleted Search Service '{SEARCH_SERVICE_NAME}': {response}")
    except Exception as e:
        print(f"Failed to delete Search Service '{SEARCH_SERVICE_NAME}': {e}")

    # Step 4: Delete Storage Account
    print("\nStep 4: Deleting Storage Account...")
    try:
        endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.Storage/storageAccounts/{STORAGE_ACCOUNT_NAME}?api-version=2022-09-01"
        response = await azure_client.delete(endpoint)
        print(f"Deleted Storage Account '{STORAGE_ACCOUNT_NAME}': {response}")
    except Exception as e:
        print(f"Failed to delete Storage Account '{STORAGE_ACCOUNT_NAME}': {e}")

    # Step 5: Delete Resource Group
    print("\nStep 5: Deleting Resource Group...")
    try:
        endpoint = f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}?api-version=2021-04-01"
        response = await azure_client.delete(endpoint)
        print(f"Deleted Resource Group '{RESOURCE_GROUP_NAME}': {response}")
    except Exception as e:
        print(f"Failed to delete Resource Group '{RESOURCE_GROUP_NAME}': {e}")

    print("\nAll resources have been deleted successfully!")

    response = await purge_deleted_account(
        azureLightClient=azure_client,
        subscription_id=subscription_id,
        LOCATION=LOCATION,
        OPENAI_ACCOUNT_NAME=OPENAI_ACCOUNT_NAME
    )
    print(f"response = {response}")