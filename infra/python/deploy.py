import os
import datetime

import zipfile
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.search import SearchManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.web.models import Site, SiteConfig
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.models import VirtualNetwork, Subnet
from azure.mgmt.web.models import AppServicePlan
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

def create_resource_group(resource_client, rg_name, location):
    resource_client.resource_groups.create_or_update(rg_name, {"location": location})


def create_app_service_plan(web_client, rg_name, plan_name, location):
    print(f"Creating App Service Plan '{plan_name}'...")
    existing = None
    try:
        existing = web_client.app_service_plans.get(rg_name, plan_name)
    except:
        pass  # pokud neexistuje, vytvoříme ho

    if not existing:
        web_client.app_service_plans.begin_create_or_update(
            rg_name,
            plan_name,
            AppServicePlan(
                location=location,
                kind="linux",
                reserved=True,
                sku={"name": "Y1", "tier": "Dynamic", "size": "Y1", "family": "Y", "capacity": 0}
            )
        ).result()
        print(f"✅ App Service Plan '{plan_name}' created.")
    else:
        print(f"ℹ️ App Service Plan '{plan_name}' already exists.")

def zip_function_code(source_dir: str, zip_path: str):
    from pathlib import Path

    source_dir = Path(source_dir).resolve()
    zip_path = Path(zip_path).resolve()

    print(f"Zipping function code from '{source_dir}'...")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(source_dir)
                zipf.write(file_path, arcname)

    print(f"✅ Zipped to '{zip_path}'.")

def create_storage_account(storage_client, rg_name, storage_account_name, location):
    storage_client.storage_accounts.begin_create(rg_name, storage_account_name, {
        "location": location,
        "sku": {"name": "Standard_LRS"},
        "kind": "StorageV2"
    }).result()

    storage_client.storage_accounts.update(
        resource_group_name=rg_name,
        account_name=storage_account_name,
        parameters={
            "network_rule_set": {
                # "default_action": "Deny",
                "default_action": "Allow",
                "bypass": "AzureServices",
                "virtual_network_rules": []  # Můžeš přidat subnet ID
            }
        }
    )

def create_ai_search_service(search_client, rg_name, search_service_name, location, sku):
    search_client.services.begin_create_or_update(rg_name, search_service_name, {
        "location": location,
        "sku": {"name": sku},
        "replica_count": 1,
        "partition_count": 1,
        "hosting_mode": "default",
        "semantic_search": "standard"
    }).result()

def create_static_web_app(web_client, rg_name, static_app_name, location, github_handle, github_repo):
    web_client.static_sites.begin_create_or_update_static_site(rg_name, static_app_name, {
        "location": location,
        "repository_url": f"https://github.com/{github_handle}/{github_repo}",
        "branch": "main",
        "sku": {"name": "Free"}
    }).result()

# def get_storage_connection_string(storage_client, rg_name, account_name):
#     keys = storage_client.storage_accounts.list_keys(rg_name, account_name)
#     key = keys.keys[0].value  # vezmeme první klíč
#     return f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={key};EndpointSuffix=core.windows.net"

def get_storage_account_key(storage_client, rg_name, storage_account_name):
    keys = storage_client.storage_accounts.list_keys(rg_name, storage_account_name)
    return keys.keys[0].value  # První klíč

# def create_function_app(web_client, subscription_id, rg_name, function_app_name, location, plan_name, storage_account_name, storage_account_key):
#     print(f"Creating Function App '{function_app_name}'...")

#     server_farm_id = (
#         f"/subscriptions/{subscription_id}/resourceGroups/{rg_name}/"
#         f"providers/Microsoft.Web/serverfarms/{plan_name}"
#     )

#     web_client.web_apps.begin_create_or_update(rg_name, function_app_name, Site(
#         location=location,
#         kind="functionapp,linux",
#         reserved=True,  # Musí být true pro Linux!
#         server_farm_id=server_farm_id,
#         site_config={
#             "linux_fx_version": "PYTHON|3.11",
#             "app_settings": [
#                 {
#                     "name": "AzureWebJobsStorage",
#                     "value": f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={storage_account_key};EndpointSuffix=core.windows.net"
#                 },
#                 {"name": "FUNCTIONS_WORKER_RUNTIME", "value": "python"},
#                 {"name": "FUNCTIONS_EXTENSION_VERSION", "value": "~4"},
#             ]
#         }
#     )).result()

#     print(f"✅ Function App '{function_app_name}' created.")

def create_private_network(network_client, rg_name, vnet_name, subnet_name, location):
    # Vytvoření virtuální sítě
    vnet_params = {
        "location": location,
        "address_space": {"address_prefixes": ["10.0.0.0/16"]},
        "subnets": [{
            "name": subnet_name,
            "address_prefix": "10.0.0.0/24"
        }]
    }
    return network_client.virtual_networks.begin_create_or_update(
        resource_group_name=rg_name,
        virtual_network_name=vnet_name,
        parameters=vnet_params
    ).result()

def create_or_update_function_app(web_client, subscription_id, rg_name, function_app_name, location, plan_name, storage_account_name, connection_string):
    print(f"Creating or updating Function App '{function_app_name}'...")
    existing = None
    try:
        existing = web_client.web_apps.get(rg_name, function_app_name)
    except:
        pass

    if not existing:
        site_config = SiteConfig(**{
                "linux_fx_version": "PYTHON|3.11",
                "app_settings": [
                    {
                        "name": "AzureWebJobsStorage", 
                        "value": connection_string
                    },
                    {"name": "FUNCTIONS_WORKER_RUNTIME", "value": "python"},
                    {"name": "FUNCTIONS_EXTENSION_VERSION", "value": "~4"},
                    {"name": "WEBSITE_RUN_FROM_PACKAGE", "value": "1"}
                ]
            })
        web_client.web_apps.begin_create_or_update(rg_name, function_app_name, Site(
            location=location,
            kind="functionapp,linux",
            reserved=True,  # Musí být true pro Linux!
            server_farm_id=f"/subscriptions/{subscription_id}/resourceGroups/{rg_name}/providers/Microsoft.Web/serverfarms/{plan_name}",
            site_config=site_config
        )).result()
        print(f"✅ Function App '{function_app_name}' created.")
    else:
        print(f"ℹ️ Function App '{function_app_name}' already exists.")

def upload_zip_to_blob(storage_connection_string, container_name, zip_file_path, storage_account_key, account_name):
    """
    Nahraje ZIP soubor do zadaného kontejneru a vygeneruje SAS token pro přístup.
    Vrací kompletní URL s SAS tokenem.
    """
    print("Nahrávám ZIP balíček do blob storage...")
    blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    
    try:
        container_client.create_container()
        print(f"✅ Kontejner '{container_name}' vytvořen.")
    except Exception:
        print(f"ℹ️ Kontejner '{container_name}' již existuje nebo nelze vytvořit.")

    blob_name = os.path.basename(zip_file_path)
    blob_client = container_client.get_blob_client(blob_name)

    with open(zip_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print(f"✅ Soubor '{blob_name}' nahrán.")

    # Vygenerujeme SAS token platný 1 hodinu
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=storage_account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.datetime.utcnow() + datetime.tim(hours=1)
    )
    blob_url_with_sas = f"{blob_client.url}?{sas_token}"
    print(f"✅ SAS URL vygenerováno: {blob_url_with_sas}")
    return blob_url_with_sas

def deploy_function_code(credentials, subscription_id, rg_name, function_app_name: str, zip_path: str):
    import xml.etree.ElementTree as ET
    import time
    import requests

    print(f"🚀 Deploying ZIP to Function App '{function_app_name}'...")

    web_client = WebSiteManagementClient(credentials, subscription_id)

    # Reset publikovacího profilu - přeskočeno (volitelné)
    print("⚠️ Publish profile not reset — be cautious if credentials were rotated.")

    # Získání publikovacího profilu
    pub_profile = web_client.web_apps.list_publishing_profile_xml_with_secrets(
        rg_name,
        function_app_name,
        {'format': 'WebDeploy'}
    )

    xml_content = b"".join(pub_profile)
    root = ET.fromstring(xml_content)

    user = root.find(".//publishProfile[@publishMethod='MSDeploy']").attrib['userName']
    pwd = root.find(".//publishProfile[@publishMethod='MSDeploy']").attrib['userPWD']
    scm_uri = root.find(".//publishProfile[@publishMethod='MSDeploy']").attrib['publishUrl'].replace(":443", "")
    zip_url = f"https://{scm_uri}/api/zipdeploy"

    print(f"📦 ZIP URL: {zip_url}")
    # Čekání na připravenost SCM endpointu
    def wait_for_scm_ready():
        print("⌛ Waiting for Kudu/SCM endpoint to be ready...")
        for _ in range(20):  # až 60 sekund
            try:
                r = requests.get(zip_url.replace("/api/zipdeploy", "/api/settings"), auth=(user, pwd))
                if r.status_code == 200:
                    print("✅ SCM endpoint is ready.")
                    return True
            except Exception:
                pass
            time.sleep(3)
        print("❌ SCM endpoint not ready after timeout.")
        return False

    if not wait_for_scm_ready():
        print("⛔ Deployment aborted — SCM endpoint not ready.")
        return

    # Upload ZIP
    with open(zip_path, "rb") as zip_file:
        response = requests.post(
            zip_url,
            data=zip_file,
            headers={"Content-Type": "application/zip"},
            auth=(user, pwd)
        )

    if response.status_code in [200, 202]:
        print("✅ Function code deployed successfully!")
    else:
        print(f"❌ Deployment failed: {response.status_code}")
        print(response.text)


# This script creates a resource group, a storage account, an AI search service, a static web app, and a function app in Azure using the Azure SDK for Python.
# It uses the DefaultAzureCredential to authenticate, which works with Azure CLI, Managed Identity, and other Azure authentication methods.
# Make sure to set the environment variable AZURE_SUBSCRIPTION_ID with your Azure subscription ID before running the script.
def main():
    # subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

    # získání přihlašovacích údajů
    credentials = DefaultAzureCredential()

    # vytvoření klienta pro přístup k informacím o předplatném
    subscription_client = SubscriptionClient(credentials)

    # načtení seznamu předplatných
    subscription = next(subscription_client.subscriptions.list())

    # získání subscription ID
    subscription_id = subscription.subscription_id

    location = "westeurope"
    resource_group_name = "AXSemantiSearchResourceGroup"
    storage_account_name = "axsemanticstorageacc"


    search_service_sku = "standard"
    search_service_name = "semanticsearchinfra2"
    github_handle_name = "vojtan"
    github_repo_name = "semanticindexreact"

    static_web_app_name = "semanticstaticwebapp"
    function_app_name = "semanticsearchfunction"
    private_network_name = "semanticprivatevnet"

    resource_client = ResourceManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)
    storage_client = StorageManagementClient(credentials, subscription_id)
    search_client = SearchManagementClient(credentials, subscription_id)
    web_client = WebSiteManagementClient(credentials, subscription_id)
    
    print("Zipping function code...")
    zip_function_code("./infra/python/azurefunc", "function_package.zip")
    print("Function code zipped.")

    print("Creating resources...")
    create_resource_group(resource_client, resource_group_name, location)
    print(f"Resource group '{resource_group_name}' created in location '{location}'.")
    # print("Creating private network...")
    # create_private_network(network_client, resource_group_name, private_network_name, "mySubnet", location)
    # print(f"Private network '{private_network_name}' created in resource group '{resource_group_name}'.")
    print("Creating storage account...")
    create_storage_account(storage_client, resource_group_name, storage_account_name, location)
    print(f"Storage account '{storage_account_name}' created in resource group '{resource_group_name}'.")
    # print("Creating AI search service...")
    create_ai_search_service(search_client, resource_group_name, search_service_name, location, search_service_sku)
    # create_static_web_app(web_client, resource_group_name, static_web_app_name, location, github_handle_name, github_repo_name)
    # create_function_app(web_client, resource_group_name, function_app_name, location, storage_account_name)


    service_plan_name = function_app_name + "-plan"

    create_app_service_plan(web_client, resource_group_name, service_plan_name, location)
    # conn_string = get_storage_connection_string(storage_client, resource_group_name, storage_account_name)
    key = get_storage_account_key(storage_client, resource_group_name, storage_account_name)
    conn_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={key};EndpointSuffix=core.windows.net"
    create_or_update_function_app(
        web_client, 
        subscription_id, 
        resource_group_name, 
        function_app_name, 
        location, 
        service_plan_name, 
        storage_account_name,
        connection_string=conn_string
    )   

    # Nahrajeme ZIP do Blob Storage a získáme URL s SAS tokenem
    package_url = upload_zip_to_blob(connection_string, container_name, zip_file, storage_account_key, storage_account_name)


    deploy_function_code(
        credentials, 
        subscription_id, 
        resource_group_name, 
        function_app_name, 
        zip_path="function_package.zip"
    )

if __name__ == "__main__":
    main()
