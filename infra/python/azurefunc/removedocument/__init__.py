import os
import json
import logging

import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import SearchQuery   # for type hints, optional

# --- HELPERS -------------------------------------------------

def get_env(var_name: str, required: bool = True) -> str:
    """Načte proměnnou z prostředí; pokud chybí a je required, vyhodí ValueError."""
    val = os.getenv(var_name)
    if required and not val:
        raise ValueError(f"Chybí proměnná prostředí: {var_name}")
    return val

def find_document_id(
    client: SearchClient,
    document_folder: str,
    document_name: str
) -> str | None:
    """
    Najde první dokument v indexu podle folder a name a vrátí jeho id,
    nebo None, pokud dokument neexistuje.
    """
    # OData filter pro přesnou shodu
    filter_expr = (
        f"document_folder eq '{document_folder}' and "
        f"document_name eq '{document_name}'"
    )
    results = client.search(
        search_text="*",
        filter=filter_expr,
        top=1,
        include_total_count=False
    )
    try:
        first = next(results)
        return first["id"]
    except StopIteration:
        return None

def delete_by_id(
    client: SearchClient,
    document_id: str
) -> bool:
    """
    Smaže dokument podle jeho id. Vrátí True, pokud volání proběhlo bez výjimky.
    """
    try:
        res = client.delete_documents(documents=[{"id": document_id}])
        logging.info(f"Azure Search delete result: {res}")
        return True
    except Exception as e:
        logging.error(f"Chyba při mazání dokumentu id={document_id}: {e}")
        return False

# --- AZURE FUNCTION ------------------------------------------

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # 1) načtení konfigurace
        service_name = get_env("AZURE_SEARCH_SERVICE_NAME")
        index_name   = get_env("AZURE_SEARCH_INDEX_NAME")
        api_key      = get_env("AZURE_SEARCH_API_KEY")

        # 2) načtení parametrů
        params = req.params or {}
        body = req.get_json(silent=True) or {}
        folder = params.get("document_folder") or body.get("document_folder")
        name   = params.get("document_name")   or body.get("document_name")

        if not folder or not name:
            return func.HttpResponse(
                "Chybí parametry 'document_folder' a 'document_name'.",
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
        doc_id = find_document_id(client, folder, name)
        if not doc_id:
            return func.HttpResponse(
                json.dumps({
                    "error": "not_found",
                    "message": f"Dokument '{name}' ve složce '{folder}' nebyl nalezen."
                }),
                status_code=404,
                mimetype="application/json"
            )

        success = delete_by_id(client, doc_id)
        if not success:
            return func.HttpResponse(
                json.dumps({
                    "error": "delete_failed",
                    "message": f"Dokument '{name}' (id={doc_id}) se nepodařilo odstranit."
                }),
                status_code=500,
                mimetype="application/json"
            )

        # 5) odpověď
        return func.HttpResponse(
            json.dumps({
                "message": f"Dokument '{name}' ve složce '{folder}' byl úspěšně odstraněn.",
                "id": doc_id
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
