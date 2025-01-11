import asyncio
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient, ResourceManagementClient
from azure.mgmt.search import SearchManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

# Import constants
from _desc import (
    RESOURCE_GROUP_NAME,
    STORAGE_ACCOUNT_NAME,
    SEARCH_SERVICE_NAME,
    OPENAI_ACCOUNT_NAME
)

# Initialize credential and subscription information
credential = DefaultAzureCredential()
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


subscription = first_subscription()

# Initialize Azure clients
SUBSCRIPTION_ID = subscription.subscription_id

# Initialize Azure clients
resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
storage_client = StorageManagementClient(credential, SUBSCRIPTION_ID)
search_client = SearchManagementClient(credential, SUBSCRIPTION_ID)
cognitive_services_client = CognitiveServicesManagementClient(credential, SUBSCRIPTION_ID)

async def delete_cognitive_services_account():
    """
    Deletes the Cognitive Services account.
    """
    print(f"Deleting Cognitive Services account: {OPENAI_ACCOUNT_NAME}...")
    try:
        poller = cognitive_services_client.accounts.begin_delete(
            RESOURCE_GROUP_NAME, OPENAI_ACCOUNT_NAME
        )
        poller.result()
        print(f"Cognitive Services account '{OPENAI_ACCOUNT_NAME}' deleted successfully.")
    except Exception as e:
        print(f"Failed to delete Cognitive Services account: {e}")

def delete_search_service():
    """
    Deletes the Azure Search service.
    """
    print(f"Deleting Azure Search service: {SEARCH_SERVICE_NAME}...")
    try:
        search_client.services.delete(
            resource_group_name=RESOURCE_GROUP_NAME,
            search_service_name=SEARCH_SERVICE_NAME,
        )
        print(f"Azure Search service '{SEARCH_SERVICE_NAME}' deleted successfully.")
    except Exception as e:
        print(f"Failed to delete Azure Search service: {e}")

def delete_storage_account():
    """
    Deletes the Storage account.
    """
    print(f"Deleting Storage account: {STORAGE_ACCOUNT_NAME}...")
    try:
        storage_client.storage_accounts.delete(
            RESOURCE_GROUP_NAME, STORAGE_ACCOUNT_NAME
        )
        print(f"Storage account '{STORAGE_ACCOUNT_NAME}' deleted successfully.")
    except Exception as e:
        print(f"Failed to delete Storage account: {e}")

def delete_resource_group():
    """
    Deletes the entire resource group.
    """
    print(f"Deleting resource group: {RESOURCE_GROUP_NAME}...")
    try:
        poller = resource_client.resource_groups.begin_delete(RESOURCE_GROUP_NAME)
        poller.result()
        print(f"Resource group '{RESOURCE_GROUP_NAME}' deleted successfully.")
    except Exception as e:
        print(f"Failed to delete resource group: {e}")

# Main function
async def main(delete_group=False):
    if delete_group:
        delete_resource_group()
    else:
        delete_storage_account()
        delete_search_service()
        await delete_cognitive_services_account()

if __name__ == "__main__":
    delete_group = input(
        "Do you want to delete the entire resource group? (yes/no): "
    ).strip().lower().startswith("y")
    asyncio.run(main(delete_group))
