import shutil
print(shutil.which("az"))

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient, ResourceManagementClient
from azure.mgmt.consumption import ConsumptionManagementClient

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


def list_resource_groups(subscription):
    """
    List all resource groups in a given subscription.
    """
    subscription_id = subscription.subscription_id
    print(f"Resource Groups in Subscription ID: {subscription_id}\n")

    # Initialize Resource Management client
    resource_client = ResourceManagementClient(credential, subscription_id)

    # List resource groups
    for rg in resource_client.resource_groups.list():
        print(f"Resource Group Name: {rg.name}")
        print(f"Location: {rg.location}")
        print(f"Provisioning State: {rg.properties.provisioning_state}")
        print("-" * 20)
        print(f"{rg.as_dict()}")

def get_billing_info(subscription):
    """
    Retrieve billing information for a subscription.
    """
    subscription_id = subscription.subscription_id
    print(f"Fetching billing info for Subscription ID: {subscription_id}\n")
    consumption_client = ConsumptionManagementClient(credential, subscription_id)

    scope = f"/subscriptions/{subscription_id}"  # Scope for the subscription

    try:
        print(f"Fetching usage details for scope: {scope}\n")
        usage_details = consumption_client.usage_details.list(scope)

        for detail in usage_details:
            # Print all available attributes for debugging
            # print(f"Available Attributes: {dir(detail)}")
            # print(f"Detail as dict: {detail.as_dict()}")  # Print detail as dictionary
            
            # Replace the below fields with available ones from the API response
            print(f"Instance ID: {detail.product}")
            print(f"consumed_service: {detail.consumed_service}")
            print(f"resource_group: {detail.resource_group}")
            print(f"resource_name: {detail.resource_name}")
            print(f"Cost: {detail.cost}")
            print(f"billing_currency: {detail.billing_currency}")
            print(f"billing_period_start_date: {detail.billing_period_start_date}")
            print(f"billing_period_end_date: {detail.billing_period_end_date}")
            print("-" * 40)
        
        print(f"Available Attributes: {dir(detail)}")
        print(f"{detail.as_dict()}")

    except Exception as e:
        print(f"Error fetching usage details: {e}")

if __name__ == "__main__":
    fs = first_subscription()
    list_resource_groups(fs)
    get_billing_info(fs)
