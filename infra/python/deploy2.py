import os
import time
import zipfile
import datetime
import requests
from pathlib import Path

from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.web.models import Site, SiteConfig, AppServicePlan
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.mgmt.search import SearchManagementClient
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import Account as CognitiveServicesAccount, Sku
from azure.ai.openai import OpenAIClient

from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField
)
from azure.search.documents.indexes import SearchIndexClient


# ---------------------------
# Pomocné funkce
# ---------------------------
def create_resource_group(resource_client, rg_name, location):
    resource_client.resource_groups.create_or_update(rg_name, {"location": location})
    print(f"✅ Resource Group '{rg_name}' vytvořena.")


def create_app_service_plan(web_client, rg_name, plan_name, location):
    print(f"Vytvářím App Service Plan '{plan_name}'...")
    try:
        existing = web_client.app_service_plans.get(rg_name, plan_name)
    except Exception:
        existing = None

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
        print(f"✅ App Service Plan '{plan_name}' vytvořen.")
    else:
        print(f"ℹ️ App Service Plan '{plan_name}' již existuje.")


def create_storage_account(storage_client, rg_name, storage_account_name, location):
    print(f"Vytvářím Storage Account '{storage_account_name}'...")
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
                "default_action": "Allow",
                "bypass": "AzureServices",
                "virtual_network_rules": []
            }
        }
    )
    print(f"✅ Storage Account '{storage_account_name}' vytvořen.")


def get_storage_account_key(storage_client, rg_name, storage_account_name):
    keys = storage_client.storage_accounts.list_keys(rg_name, storage_account_name)
    return keys.keys[0].value


def zip_function_code(source_dir: str, zip_path: str):
    source_dir = Path(source_dir).resolve()
    zip_path = Path(zip_path).resolve()
    print(f"Zabalím kód funkcí z '{source_dir}' do '{zip_path}'...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(source_dir)
                zipf.write(file_path, arcname)
    print(f"✅ Kód funkcí byl zabalen do '{zip_path}'.")


def create_or_update_function_app(web_client, subscription_id, rg_name, function_app_name, location, plan_name, storage_account_name, connection_string):
    print(f"Vytvářím nebo aktualizuji Function App '{function_app_name}'...")
    try:
        existing = web_client.web_apps.get(rg_name, function_app_name)
    except Exception:
        existing = None

    if not existing:
        site_config = SiteConfig(
            linux_fx_version="PYTHON|3.11",
            app_settings=[
                {"name": "AzureWebJobsStorage", "value": connection_string},
                {"name": "FUNCTIONS_WORKER_RUNTIME", "value": "python"},
                {"name": "FUNCTIONS_EXTENSION_VERSION", "value": "~4"}
            ]
        )
        server_farm_id = f"/subscriptions/{subscription_id}/resourceGroups/{rg_name}/providers/Microsoft.Web/serverfarms/{plan_name}"
        web_client.web_apps.begin_create_or_update(
            rg_name, function_app_name,
            Site(
                location=location,
                kind="functionapp,linux",
                reserved=True,
                server_farm_id=server_farm_id,
                site_config=site_config
            )
        ).result()
        print(f"✅ Function App '{function_app_name}' vytvořen.")
    else:
        print(f"ℹ️ Function App '{function_app_name}' již existuje.")


def upload_zip_to_blob(storage_connection_string, container_name, zip_file_path, storage_account_key, account_name):
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

    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=storage_account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    )
    blob_url_with_sas = f"{blob_client.url}?{sas_token}"
    print(f"✅ SAS URL vygenerováno: {blob_url_with_sas}")
    return blob_url_with_sas


def update_function_app_package_setting(web_client, rg_name, function_app_name, package_url):
    print("Aktualizuji aplikacní nastavení Function App...")
    settings = web_client.web_apps.list_application_settings(rg_name, function_app_name)
    settings.properties["WEBSITE_RUN_FROM_PACKAGE"] = package_url
    web_client.web_apps.update_application_settings(rg_name, function_app_name, settings)
    print("✅ Nastavení WEBSITE_RUN_FROM_PACKAGE aktualizováno.")


def create_ai_search_service(search_client, rg_name, search_service_name, location, sku):
    try:
        existing_service = search_client.services.get(rg_name, search_service_name)
        if existing_service:
            print(f"ℹ️ AI Search Service '{search_service_name}' již existuje.")
            return existing_service
    except HttpResponseError as e:
        if "ServiceNameUnavailable" in str(e):
            print(f"ℹ️ AI Search Service '{search_service_name}' již existuje nebo je název rezervován.")
            return None
        print(f"Chyba při ověřování existence služby: {e}")

    try:
        poller = search_client.services.begin_create_or_update(rg_name, search_service_name, {
            "location": location,
            "sku": {"name": sku},
            "replica_count": 1,
            "partition_count": 1,
            "hosting_mode": "default",
            "semantic_search": "standard"
        })
        poller.result()
        print(f"✅ AI Search Service '{search_service_name}' vytvořen.")
    except HttpResponseError as e:
        if "ServiceNameUnavailable" in str(e):
            print(f"ℹ️ AI Search Service '{search_service_name}' již existuje nebo je název rezervován (chyba: {e}).")
        else:
            raise


def get_search_admin_key(subscription_id, resource_group, search_service_name, credentials):
    search_client = SearchManagementClient(credentials, subscription_id)
    admin_keys = search_client.admin_keys.get(resource_group, search_service_name)
    return admin_keys.primary_key


def get_cognitive_services_key(subscription_id, resource_group, cognitive_account_name, credentials):
    cog_client = CognitiveServicesManagementClient(credentials, subscription_id)
    keys = cog_client.accounts.list_keys(resource_group, cognitive_account_name)
    print(f"🔑 Cognitive Services keys: {keys}")
    return keys.key1


def create_or_get_cognitive_account(subscription_id, resource_group, account_name, location, sku_name, kind, tags=None):
    credential = DefaultAzureCredential()
    cog_client = CognitiveServicesManagementClient(credential, subscription_id)
    try:
        account = cog_client.accounts.get(resource_group, account_name)
        print(f"ℹ️ Cognitive Services účet '{account_name}' již existuje.")
        return account
    except Exception as e:
        print(f"ℹ️ Cognitive Services účet '{account_name}' nebyl nalezen, bude vytvořen. Detaily chyby (ignorujeme): {e}")

    params = CognitiveServicesAccount(
        location=location,
        sku=Sku(name=sku_name),
        kind=kind,
        properties={},
        tags=tags
    )
    
    print(f"🚀 Vytvářím Cognitive Services účet '{account_name}'...")
    poller = cog_client.accounts.begin_create(resource_group, account_name, params)
    account = poller.result()
    print(f"✅ Cognitive Services účet '{account_name}' byl úspěšně vytvořen.")
    return account

def create_or_update_skillset(search_service_name, admin_key, skillset_name, cognitive_services_key):
    """
    Vytvoří nebo aktualizuje skillset v Azure Cognitive Search s použitím SplitSkill pro chunking textu
    a EmbeddingsSkill pro generování vektorů.
    """
    api_version = "2020-06-30"
    url = f"https://{search_service_name}.search.windows.net/skillsets/{skillset_name}?api-version={api_version}"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": admin_key
    }

    skillset_definition = {
        "name": skillset_name,
        "description": "Skillset s chunkingem pro rozdělení textu a embedding pro generování vektorů",
        "skills": [
            {
                "@odata.type": "#Microsoft.Skills.Text.SplitSkill",
                "name": "textChunker",
                "description": "Rozděluje text na chunky",
                "context": "/document/normalized_text",
                "inputs": [
                    {"name": "text", "source": "/document/normalized_text"}
                ],
                "outputs": [
                    {"name": "textItems", "targetName": "chunks"}
                ],
                "defaultLanguageCode": "en",
                "textSplitMode": "pages"  # Přidaný parametr pro dělení na stránky
            },
            # {
            #     "@odata.type": "#Microsoft.Skills.Text.EmbeddingsSkill",
            #     "name": "embeddingSkill",
            #     "description": "Generuje embeddingy pro každý chunk textu",
            #     "context": "/document/chunks",
            #     "inputs": [
            #         {"name": "text", "source": "/document/chunks"}
            #     ],
            #     "outputs": [
            #         {"name": "embedding", "targetName": "contentVector"}  # Ukládání vektoru do pole contentVector
            #     ],
            #     "cognitiveServices": {
            #         "@odata.type": "#Microsoft.Azure.Search.CognitiveServicesByKey",
            #         "description": "Klíč pro Cognitive Services spojených s vyhledáváním",
            #         "key": cognitive_services_key
            #     }
            # }
        ]
    }

    response = requests.put(url, headers=headers, json=skillset_definition)
    if response.status_code in [200, 201]:
        print("✅ Skillset s chunkingem a embeddingy pro vektorové vyhledávání byl úspěšně vytvořen/aktualizován.")
    else:
        print(f"❌ Chyba při vytváření/aktualizaci skillsetu: {response.status_code} - {response.text}")

def get_skillset(search_service_name, admin_key, skillset_name):
    """
    Pokusí se získat detail skillsetu z Azure Cognitive Search.
    """
    api_version = "2020-06-30"
    url = f"https://{search_service_name}.search.windows.net/skillsets/{skillset_name}?api-version={api_version}"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": admin_key
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f"✅ Skillset '{skillset_name}' byl nalezen: {response.json()}")
    else:
        print(f"❌ Chyba při získávání skillsetu: {response.status_code} - {response.text}")

def create_or_update_vector_index(credentials, search_service_name, admin_key, index_name, vector_dimension=1536):
    """
    Vytvoří nebo aktualizuje index pro vector search.
    Index obsahuje klíčová pole, textové pole a vektorové pole 'contentVector' s dodatečnými vlastnostmi.
    
    Místo sestavování instance SearchIndex pomocí SDK konstruktorů sestavíme slovníkovou definici
    a převedeme ji na SearchIndex přes from_dict, čímž zajistíme, že budou ve výsledném JSONu obsaženy
    dodatečné vlastnosti 'dimensions' a 'vectorSearchConfiguration'.
    
    Parametry:
      - credentials: Credential instance (např. DefaultAzureCredential)
      - search_service_name: Název Search Service (bez domény, např. "semanticsearchinfra24654")
      - admin_key: Admin klíč z Search Service
      - index_name: Unikátní jméno indexu
      - vector_dimension: Dimenze vektorů (výchozí 1536, pro OpenAI embeddingy)
    """
    from azure.search.documents.indexes import SearchIndexClient
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.models import SearchIndex

    endpoint = f"https://{search_service_name}.search.windows.net/"
    # Použijeme AzureKeyCredential založený na admin klíči (nutný pro operace nad indexem)
    index_client = SearchIndexClient(
        endpoint=endpoint, 
        credential=AzureKeyCredential(admin_key)
        )
    
    # Sestavíme slovníkovou definici indexu
    index_definition = {
        "name": index_name,
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "searchable": False},
            {"name": "document_folder", "type": "Edm.String", "searchable": True},
            {"name": "document_name", "type": "Edm.String", "searchable": False},
            {"name": "content", "type": "Edm.String", "searchable": True},
            {
                "name": "contentVector",
                "type": "Collection(Edm.Single)",
                "searchable": True,
                "dimensions": vector_dimension,
                # "vectorSearchConfiguration": "vectorConfig1",
                "vectorSearchProfile": "vectorProfile1"  # Nová vlastnost požadovaná API
            }
        ],
        "vectorSearch": {
            "algorithms": [
                {
                "name": "hnsw-1",
                "kind": "hnsw",
                "hnswParameters": {
                    "m": 4,
                    "efConstruction": 400,
                    "efSearch": 500,
                    "metric": "cosine"
                }
                }
            ],
            "profiles": [
                {
                "name": "vectorProfile1",
                "algorithm": "hnsw-1"
                }
            ]
        }
    }
    
    # Převod slovníkové definice na objekt SearchIndex
    index = SearchIndex.from_dict(index_definition)
    
    # Vytvoření nebo aktualizace indexu
    result_index = index_client.create_or_update_index(index)
    print(f"✅ Vector index '{result_index.name}' byl úspěšně vytvořen/aktualizován.")


def create_or_update_openai_model_deployment(cognitive_account_endpoint, model_deployment_name, model_name):
    """
    Vytvoří nebo aktualizuje deployment OpenAI modelu v rámci Cognitive Services.
    (Pozn.: V praxi toto obvykle provedete přes Azure Portal, CLI nebo ARM template.
    Tady je návrh pro budoucí automatizaci, pokud Azure SDK tuto funkcionalitu podporuje.)
    """
    credential = DefaultAzureCredential()
    client = OpenAIClient(cognitive_account_endpoint, credential)

    # Zde je pouze návrh, protože SDK nemusí mít metodu pro deployment vytváření přímo.
    # V případě potřeby použij ARM template nebo Azure CLI k nasazení modelů.

    # Pokud by SDK umožňovala, mohl by to být nějaký kód:
    # client.model_deployments.create_or_update(
    #     deployment_name=model_deployment_name,
    #     model_name=model_name
    # )
    print(f"Nasazení modelu '{model_name}' jako deployment '{model_deployment_name}' - implementace podle SDK nebo ARM.")


# ---------------------------
# Hlavní skript
# ---------------------------
def main():
    credentials = DefaultAzureCredential()
    subscription_client = SubscriptionClient(credentials)
    subscription = next(subscription_client.subscriptions.list())
    subscription_id = subscription.subscription_id

    # Konfigurace
    location = "westeurope"
    resource_group_name = "AXSemantiSearchResourceGroup"
    storage_account_name = "axsemanticstorageacc"
    function_app_name = "semanticsearchfunction"
    service_plan_name = function_app_name + "-plan"
    container_name = "function-code"
    zip_file = "function_package.zip"           # Váš ZIP soubor s funkcí
    function_code_dir = "./infra/python/azurefunc"  # Zdrojový adresář s kódem funkcí

    cognitive_account_name = "axsemanticcogaccount"
    search_service_sku = "standard"
    search_service_name = "semanticsearchinfra24654"
    vector_index_name = "my_vector_index"
    skillset_name = "my-skillset-with-chunking"

    # Inicializace klientů
    resource_client = ResourceManagementClient(credentials, subscription_id)
    storage_client = StorageManagementClient(credentials, subscription_id)
    web_client = WebSiteManagementClient(credentials, subscription_id)
    search_client = SearchManagementClient(credentials, subscription_id)

    # Vytvoření Resource Group
    create_resource_group(resource_client, resource_group_name, location)

    # Vytvoření Storage Account
    create_storage_account(storage_client, resource_group_name, storage_account_name, location)
    storage_account_key = get_storage_account_key(storage_client, resource_group_name, storage_account_name)
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={storage_account_key};EndpointSuffix=core.windows.net"

    sku_name = "S0"          
    kind = "CognitiveServices"  
    tags = {"env": "prod", "project": "SemanticSearch"}
    
    account = create_or_get_cognitive_account(subscription_id, resource_group_name, cognitive_account_name, location, sku_name, kind, tags)
    
    keys = CognitiveServicesManagementClient(DefaultAzureCredential(), subscription_id) \
            .accounts.list_keys(resource_group_name, cognitive_account_name)
    print(f"🔑 Cognitive Services primary key: {keys}")
    cognitive_key = keys.key1
    print(f"🔑 Cognitive Services primary key: {cognitive_key}")

    create_ai_search_service(search_client, resource_group_name, search_service_name, location, search_service_sku)

    search_admin_key = get_search_admin_key(subscription_id, resource_group_name, search_service_name, credentials)
    print(f"Search Admin Key: {search_admin_key}")

    cognitive_services_key = get_cognitive_services_key(subscription_id, resource_group_name, cognitive_account_name, credentials)
    print(f"Cognitive Services Key: YOUR_OPENAI_API_KEY='{cognitive_services_key}'")
    print("tento klic je pro funkce potrebujici pristup k AI Search Service a take pro embedding")

    # Vytvoření skillsetu s chunkingem
    create_or_update_skillset(search_service_name, search_admin_key, skillset_name, cognitive_services_key)

    # Získání skillsetu pro ověření
    get_skillset(search_service_name, search_admin_key, skillset_name)

    # Vytvoření nebo aktualizace vector indexu
    create_or_update_vector_index(credentials, search_service_name, search_admin_key, vector_index_name, vector_dimension=1536)

    # Zipování kódu funkcí
    zip_function_code(function_code_dir, zip_file)

    # Vytvoření App Service Planu
    create_app_service_plan(web_client, resource_group_name, service_plan_name, location)

    # Vytvoření nebo aktualizace Function App
    create_or_update_function_app(web_client, subscription_id, resource_group_name, function_app_name, location,
                                  service_plan_name, storage_account_name, connection_string)

    # Nahrání ZIP do Blob Storage a získání URL s SAS tokenem
    package_url = upload_zip_to_blob(connection_string, container_name, zip_file, storage_account_key, storage_account_name)

    # Aktualizace nastavení Function App: WEBSITE_RUN_FROM_PACKAGE
    update_function_app_package_setting(web_client, resource_group_name, function_app_name, package_url)

    print("✅ Nasazení kódu proběhlo úspěšně. Vaše Function App načte kód přímo z balíčku uloženého v Azure Blob Storage.")


    cognitive_account = create_or_get_cognitive_account(
        subscription_id, resource_group_name,
        cognitive_account_name, location,
        sku_name, kind, tags
    )

    cognitive_account_endpoint = cognitive_account.properties.endpoint

    # Přidat nasazení modelů (pouze jako logická ukázka, implementace může být přes CLI/Portal)
    create_or_update_openai_model_deployment(
        cognitive_account_endpoint,
        model_deployment_name="embedding-deployment",
        model_name="text-embedding-ada-002"
    )

    create_or_update_openai_model_deployment(
        cognitive_account_endpoint,
        model_deployment_name="summarization-deployment",
        model_name="gpt-4o-mini"
    )

if __name__ == "__main__":
    main()
