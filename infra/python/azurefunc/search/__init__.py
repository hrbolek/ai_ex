import os
import json
import logging
import msal
import requests
import jwt

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
            "document_folder": r.get("document_folder"),
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


TENANT_ID = "xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
CLIENT_ID = "APP_ID"
CLIENT_SECRET = "APP_SECRET"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

SHAREPOINT_SCOPE = ["https://{tenant}.sharepoint.com/.default"]

bearerstr = "bearer "
bearerstrlen = len(bearerstr)

def get_user_email_from_req(req):
    # req je parametr dodany azure funkci
    # predpoklada se flow OBO (On Behalf Of), aby mohla byt vykonana impersonizace
    # je potreba overit, jake udaje v jwt skutecne jsou, zalezi to na konfiguraci
    # Očekává: Authorization: Bearer <token>

    auth_header = req.headers.get('authorization') or req.headers.get('Authorization')
    if not auth_header or not auth_header.lower().startswith("bearer "):
        return None  # nebo vyhoď výjimku

    token = auth_header[bearerstrlen:]

    try:
        # Pozor: verify_signature=False NIKDY nepoužívej na veřejné endpointy! Tady je to OK jen pro získání claimů, pokud Azure API proxy už validovala token.
        decoded = jwt.decode(token, options={"verify_signature": False, "verify_aud": False})
        # Nejčastější možnosti claimů s e-mailem:
        email = decoded.get("email") or decoded.get("upn") or decoded.get("preferred_username")
        return email
    except Exception as e:
        print("Token decode error:", e)
        return None
    
def get_sp_access_token(user_token):
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_on_behalf_of(
        user_assertion=user_token,
        scopes=SHAREPOINT_SCOPE,
    )
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Failed to acquire SharePoint token: {result.get('error_description')}")


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

    # toto prijde pryc, az bude pouzivana detekce autorizace pro pristup k dokumentum
    if user_token is None:
        return True

    sp_access_token = get_sp_access_token(user_token)
    headers = {"Authorization": f"Bearer {sp_access_token}"}
    
    # toto by bylo lepsi udelat jako asynchronni funkci
    resp = requests.get(document_url, headers=headers)
    return resp.status_code == 200  # nebo zpracuj další statusy

    # return True  # prozatím vždy povolit (dummy)

def find_additional_accessible_documents2(user_token, search_vector, desired_count=10, already_seen_ids=None):
    """
    Vrací seznam dokumentů z vektorového indexu, ke kterým má uživatel přístup,
    včetně dynamického načítání dalších pokud je jich po kontrole práv málo.
    """
    # IDs, které už jsme zkoušeli (abychom je nevraceli znova)
    already_seen_ids = set(already_seen_ids or [])

    found_docs = []
    offset = 0
    batch_size = 20  # Kolik najednou dotáhnout – můžeš si upravit

    while len(found_docs) < desired_count:
        # 1. Vyhledej další várku kandidátů podle vektoru
        results = search_by_vector(
            vector=search_vector,
            top=offset + batch_size
        )

        # Pokud už nejsou další kandidáti, skonči
        if not results or len(results) <= offset:
            break

        # 2. Vyfiltruj nově načtené dokumenty (přeskoč already_seen_ids)
        new_candidates = [doc for doc in results[offset:] if doc["id"] not in already_seen_ids]
        if not new_candidates:
            break

        # 3. Zkontroluj přístupová práva a přidej do výsledku jen ty, ke kterým má uživatel přístup
        for doc in new_candidates:
            if check_user_access_to_document(user_token, doc["document_url"]):
                found_docs.append(doc)
                if len(found_docs) == desired_count:
                    break
            already_seen_ids.add(doc["id"])

        # Posuň offset pro další kolo
        offset += batch_size

    return found_docs

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
import base64

def main(req: func.HttpRequest) -> func.HttpResponse:

    # # autentizacni udaje, pokud je nastavena autentizace pomoci entra id ...
    # principal_b64 = req.headers.get('x-ms-client-principal', None)
    # if not principal_b64:
    #     return func.HttpResponse("User not authenticated", status_code=401)
    # else:
    #     principal_json = base64.b64decode(principal_b64).decode('utf-8')
    #     principal = json.loads(principal_json)

    #     user_id = principal.get('userId')
    #     user_email = principal.get('userDetails')
    #     idp = principal.get('identityProvider')

    # asi se bude muset provest prevzeti user_jwt
    # bearerstr = "bearer "
    # user_access_token = req.headers.get('authorization')
    # if not user_access_token or not user_access_token.lower().startswith(bearerstr):
    #     return func.HttpResponse("Missing user access token", status_code=401)
    # user_access_token = user_access_token.replace(bearerstr, "")

    user_access_token = None

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

        # 2) vyhledání top dokumentů / fragmentů
        docs = search_by_vector(vec, search_service, search_index, search_api_key, top=5)

        # 3) filtrování podle přístupu uživatele (zatím dummy)
        # TODO: implementovat reálnou kontrolu Entra ID

        urls = {doc["document_url"] for doc in docs}
        available_urls = [check_user_access_to_document(user_token=user_access_token, document_url=url) for url in urls]
        accessible_docs = [doc for doc in docs if doc["document_url"] in available_urls]
        accessible_docs_len = len(accessible_docs)
        if accessible_docs_len < 10:
            other_docs = find_additional_accessible_documents(user_token=user_access_token, max_count=10-accessible_docs)
            urls = {doc["document_url"] for doc in other_docs}
            other_available_urls = [check_user_access_to_document(user_token=user_access_token, document_url=url) for url in urls]
            other_accessible_docs = [doc for doc in docs if doc["document_url"] in other_available_urls]
            accessible_docs.extend(other_accessible_docs)
            accessible_docs_len = len(accessible_docs)



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
