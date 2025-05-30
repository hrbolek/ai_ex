import os
import azure.functions as func
import openai

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Inicializace OpenAI klíče z prostředí
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_query_vector(query: str):
    """
    Generuje embedding vektor pro dotaz pomocí OpenAI modelu.
    """
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=query
    )
    embedding = response['data'][0]['embedding']
    return embedding

from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential

# Upravte podle názvu vašeho Cognitive OpenAI účtu:
COGNITIVE_ACCOUNT_NAME = "axsemanticcogaccount0602"
# Stejný název deploymentu, který jste vytvořili skriptem
EMBEDDING_DEPLOYMENT_NAME = "embedding-deployment"

def generate_embedding(apikey: str, text: str) -> list[float]:
    """
    Vygeneruje embedding pro zadaný text použitím Azure AI Inference (preview SDK),
    bez závislosti na balíčku openai-python.
    
    - apikey: primární klíč (key1) vašeho Cognitive OpenAI účtu.
    - text:   vstupní řetězec, pro který chcete embedding.
    
    Vrací: list plovoucích čísel reprezentující embedding.
    """
    endpoint = f"https://{COGNITIVE_ACCOUNT_NAME}.openai.azure.com"
    # Vytvoříme klienta pro embedding
    client = EmbeddingsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(apikey),
        model=EMBEDDING_DEPLOYMENT_NAME
    )
    # Pošleme jeden řetězec
    result = client.embed(input=[text])
    # Výsledek je objekt s .data, kde každá položka má .embedding
    return result.data[0].embedding

def search_documents(query: str, search_service_name, index_name, search_api_key):
    """
    Vyhledává dokumenty v Azure Cognitive Search pomocí vektorového dotazu.
    """
    endpoint = f"https://{search_service_name}.search.windows.net"
    client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(search_api_key))

    query_vector = generate_embedding(key, query)

    results = client.search(
        search_text="*",  # nutné pro Azure Search, i když používáme vektor
        vector={
            "value": query_vector,
            "fields": "contentVector",  # název pole s embeddingem v indexu
            "k": 10
        }
    )

    documents = []
    for result in results:
        documents.append({
            "id": result.get("id"),
            "document_name": result.get("fileName") or result.get("document_name"),
            "document_folder": result.get("folderName") or result.get("document_folder"),
            "url": result.get("url"),
            "score": result.get("@search.score")
        })

    return documents


def search_documents_for_LLM(query_vector, search_service_name, index_name, search_api_key, top=5):
    endpoint = f"https://{search_service_name}.search.windows.net"
    client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(search_api_key))
    results = client.search(
        search_text="*",
        vector={
            "value": query_vector,
            "fields": "contentVector",
            "k": top
        }
    )
    # Převod výsledků na seznam dokumentů
    docs = []
    for r in results:
        docs.append({
            "content": r.get("content", ""),
            "url": r.get("url", "")
        })
    return docs

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

def summarize_documents_with_sources(documents, query):
    # Sestav prompt se zdroji, každý dokument označíme číslem
    context_parts = []
    for i, doc in enumerate(documents, start=1):
        context_parts.append(f"[{i}] {doc['content']}\nSource: {doc['url']}")
    context = "\n\n".join(context_parts)

    prompt = (
        f"Na základě následujících textů odpověz na dotaz:\n{query}\n\n"
        f"Texty:\n{context}\n\n"
        "Prosím, ve své odpovědi odkaž na zdroje pomocí číselných odkazů [1], [2], ... "
        "a na konci odpovědi uváděj seznam těchto zdrojů s URL."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Jsi asistent poskytující odpovědi s odkazy na zdroje."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.3
    )
    return response.choices[0].message.content

def main(req: func.HttpRequest) -> func.HttpResponse:
    query = req.params.get('q')
    if not query:
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse("Please provide a search query parameter 'q'.", status_code=400)
        else:
            query = req_body.get('q')

    if not query:
        return func.HttpResponse("Missing search query parameter 'q'.", status_code=400)

    # Načtení konfiguračních hodnot z prostředí
    search_service_name = os.getenv("AZURE_SEARCH_SERVICE_NAME")
    search_index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
    search_api_key = os.getenv("AZURE_SEARCH_API_KEY")

    if not all([search_service_name, search_index_name, search_api_key]):
        return func.HttpResponse("Search service configuration is missing.", status_code=500)

    try:
        query_vector = generate_query_vector(query)
        docs = search_documents_for_LLM(query_vector, search_service_name, search_index_name, search_api_key)

        user_token = None  # Zde by měl být získán token uživatele, např. z hlavičky Authorization
        missing_docs = 0
        for doc in docs:
            has_access = check_user_access_to_document(user_token, doc.get("url"))
            if not has_access:
                doc["content"] = "Access denied to this document."
                doc["enabled"] = False
                missing_docs += 1

        if missing_docs > 0:
            additional_docs = find_additional_accessible_documents(user_token)
            # Zpracuj další logiku...
            docs.extend(additional_docs)


        summary = summarize_documents_with_sources(docs, query)
        result = {
            "query": query,
            "summary": summary,
            # "sources": [doc["url"] for doc in docs],
            "documents": docs
        }
        import json
        return func.HttpResponse(json.dumps(result, ensure_ascii=False), mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(f"Search failed: {str(e)}", status_code=500)