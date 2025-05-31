import os
import json
import logging

import azure.functions as func

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference import EmbeddingsClient, ChatCompletionsClient

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

def generate_embedding(texts: list[str], api_key: str) -> list[list[float]]:
    """
    Vygeneruje embeddingy pomocí Azure AI Inference.
    texts: seznam řetězců
    """
    account = getenv("AZURE_COGNITIVE_ACCOUNT_NAME")
    deployment = getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
    endpoint = f"https://{account}.openai.azure.com"

    client = EmbeddingsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key),
        model=deployment
    )
    resp = client.embed(input=texts)
    return [item.embedding for item in resp.data]

def search_by_vector(
    query_vector: list[float],
    service_name: str,
    index_name: str,
    api_key: str,
    top: int = 5
) -> list[dict]:
    """
    Provede vektorové vyhledávání nad indexem.
    """
    endpoint = f"https://{service_name}.search.windows.net"
    client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(api_key)
    )
    results = client.search(
        search_text="*",
        vector={
            "value": query_vector,
            "fields": "contentVector",
            "k": top
        }
    )
    docs = []
    for r in results:
        docs.append({
            "id":              r.get("id"),
            "content":         r.get("content", ""),
            "url":             r.get("url"),
            "score":           r.get("@search.score"),
            # případně další metadata:
            # "document_name":  r.get("document_name"),
            # "document_folder":r.get("document_folder"),
        })
    return docs

def generate_summary(
    docs: list[dict],
    query: str,
    api_key: str
) -> str:
    """
    Vygeneruje souhrn s odkazy na zdroje pomocí Azure AI Inference Chat.
    """
    account = getenv("AZURE_COGNITIVE_ACCOUNT_NAME")
    deployment = getenv("AZURE_CHAT_DEPLOYMENT_NAME", required=False) or "summarization-deployment"
    endpoint = f"https://{account}.openai.azure.com"
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key),
        model=deployment
    )

    # Sestavíme prompt
    context = "\n\n".join(
        f"[{i+1}] {d['content']}\nSource: {d['url']}"
        for i, d in enumerate(docs)
    )
    prompt = (
        f"Na základě následujících textů odpověz na dotaz:\n{query}\n\n"
        f"Texty:\n{context}\n\n"
        "Ve své odpovědi odkáž na zdroje [1], [2], ... a na konci uveď jejich seznam s URL."
    )

    resp = client.complete(
        messages=[
            {"role": "system", "content": "Jsi nápomocný asistent, cituj zdroje."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    return resp.choices[0].message.content


def check_user_access_to_document(user_token: str, document_url: str) -> bool:
    """
    Ověří, zda má uživatel s daným tokenem přístup k dokumentu na dané URL.
    
    V budoucnu zde bude implementována autentizace a autorizace pomocí Azure Entra ID,
    kontrola oprávnění uživatele k přístupu k dokumentu.

    :param user_token: Access token uživatele (např. JWT token)
    :param document_url: URL dokumentu, ke kterému je potřeba ověřit přístup
    :return: True pokud má uživatel přístup, False jinak
    """
    # TODO: Implementovat volání Entra/Azure AD k ověření tokenu a přístupových práv
    # TODO: Ověřit, zda uživatel smí dokument číst
    return True  # prozatím vždy povolit (dummy)


def find_additional_accessible_documents(user_token: str, max_count: int = 10) -> list:
    """
    Vyhledá další dokumenty, ke kterým má uživatel přístup, pokud primární dokument není dostupný.
    
    V budoucnu zde bude implementováno volání relevantních API/úložišť,
    které vrátí seznam dostupných dokumentů pro daného uživatele,
    omezí výsledky na max_count.

    :param user_token: Access token uživatele
    :param max_count: Maximální počet dokumentů, které se mají vrátit
    :return: Seznam slovníků s informacemi o dokumentech (např. URL, název, metadata)
    """
    # TODO: Implementovat vyhledávání dostupných dokumentů v rámci oprávnění uživatele
    # TODO: Vrátit max_count dokumentů
    return []  # prozatím prázdný seznam (dummy)

# --- AZURE FUNCTION ------------------------------------------

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # načtení konfigurace
        search_service = getenv("AZURE_SEARCH_SERVICE_NAME")
        search_index   = getenv("AZURE_SEARCH_INDEX_NAME")
        search_api_key = getenv("AZURE_SEARCH_API_KEY")
        ai_api_key     = getenv("OPENAI_API_KEY")

        # query param
        query = req.params.get("q") or (req.get_json(silent=True) or {}).get("q")
        if not query:
            return func.HttpResponse(
                "Chybí parametr 'q' (search query).",
                status_code=400
            )

        # 1) embedding dotazu
        vec = generate_embedding([query], ai_api_key)[0]

        # 2) vyhledání top dokumentů
        docs = search_by_vector(vec, search_service, search_index, search_api_key, top=5)

        # 3) filtrování podle přístupu uživatele (zatím dummy)
        # TODO: implementovat reálnou kontrolu Entra ID
        for d in docs:
            d["access"] = True

        # 4) generování souhrnu s odkazy
        summary = generate_summary(docs, query, ai_api_key)

        # 5) výstup JSON
        payload = {
            "query":    query,
            "summary":  summary,
            "documents": docs
        }
        return func.HttpResponse(
            json.dumps(payload, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )

    except ValueError as ve:
        logging.warning(str(ve))
        return func.HttpResponse(str(ve), status_code=400)
    except Exception as e:
        logging.exception(e)
        return func.HttpResponse("Internal server error.", status_code=500)
