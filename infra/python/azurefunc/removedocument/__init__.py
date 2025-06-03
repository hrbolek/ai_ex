import os
import json
import logging

import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# --- HELPERS -------------------------------------------------

ENV_KEY_NAMES = {
    "AZURE_COGNITIVE_ACCOUNT_NAME": "AZURE_COGNITIVE_ACCOUNT_NAME",
    "AZURE_EMBEDDING_DEPLOYMENT_NAME": "AZURE_EMBEDDING_DEPLOYMENT_NAME",
    "AZURE_SEARCH_SERVICE_NAME": "AZURE_SEARCH_SERVICE_NAME",
    "AZURE_SEARCH_INDEX_NAME": "AZURE_SEARCH_INDEX_NAME",
    "AZURE_SEARCH_API_KEY": "AZURE_SEARCH_API_KEY",
    "OPENAI_API_KEY": "OPENAI_API_KEY",
    "AZURE_CHAT_DEPLOYMENT_NAME": "AZURE_CHAT_DEPLOYMENT_NAME"
}

def getenv(key_name, default_value):
    proxied_key_name = ENV_KEY_NAMES.get(key_name, None)
    assert proxied_key_name is not None, f"missing {key_name} in proxied list of key_names"
    result = os.getenv(proxied_key_name, default_value)
    return result

def find_fragments_id(
    client: SearchClient,
    document_folder: str,
) -> str | None:
    """
    Najde vsechny dokumentu v indexu podle folder a vrátí jejich idcka
    """
    # OData filter pro přesnou shodu
    filter_expr = (
        f"document_folder eq '{document_folder}'"
    )
    results = client.search(
        search_text="*",
        filter=filter_expr,
        top=1,
        include_total_count=False
    )
    ids = [result["id"] for result in results]
    return ids

def delete_by_ids(
    client: SearchClient,
    document_ids: list[str]
) -> bool:
    """
    Smaže více dokumentů podle jejich id. Vrátí True, pokud volání proběhne bez výjimky.
    """
    try:
        # S Azure Search lze mazat až 1000 záznamů v jednom volání
        batch = [{"id": did} for did in document_ids]
        client.delete_documents(documents=batch)
        logging.info(f"Deleted {len(batch)} documents: {batch}")
        return True
    except Exception as e:
        logging.error(f"Chyba při mazání dokumentů: {e}")
        return False

# --- AZURE FUNCTION ------------------------------------------

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # 1) načtení konfigurace
        service_name = getenv("AZURE_SEARCH_SERVICE_NAME", "")
        index_name   = getenv("AZURE_SEARCH_INDEX_NAME", "")
        api_key      = getenv("AZURE_SEARCH_API_KEY", "")

        # 2) načtení parametrů
        params = req.params or {}
        folder = params.get("document_folder")
        # name   = params.get("document_name")   or body.get("document_name")

        if not folder:
            return func.HttpResponse(
                "Chybí parametr 'document_folder'",
                status_code=400
            )

        # 3) připravíme klienta
        endpoint = f"https://{service_name}.search.windows.net"
        client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key)
        )

        # 4) najdeme id a smažeme
        doc_ids = find_fragments_id(client, folder)
        if len(doc_ids) == 0:
            return func.HttpResponse(
                json.dumps({
                    "error": "not_found",
                    "message": f"Dokument ve složce '{folder}' nebyl nalezen."
                }),
                status_code=404,
                mimetype="application/json"
            )

        success = delete_by_ids(client, doc_ids)
        if not success:
            return func.HttpResponse(
                json.dumps({
                    "error": "delete_failed",
                    "message": f"Dokumenty (id={doc_ids}) se nepodařilo odstranit."
                }),
                status_code=500,
                mimetype="application/json"
            )

        # 5) odpověď
        return func.HttpResponse(
            json.dumps({
                "message": f"Dokument ve složce '{folder}' byl úspěšně odstraněn.",
                "id": doc_ids
            }),
            status_code=200,
            mimetype="application/json"
        )

    except ValueError as ve:
        logging.warning(str(ve))
        return func.HttpResponse(str(ve), status_code=400)
    except Exception as ex:
        logging.exception(ex)
        return func.HttpResponse(
            "Internal server error.",
            status_code=500
        )
