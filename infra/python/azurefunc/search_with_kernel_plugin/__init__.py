import asyncio
import os
import json

from openai import AzureOpenAI
from typing import Annotated, List, Dict, Any, Optional
from pydantic import BaseModel, Field

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments

from semantic_kernel.functions import kernel_function
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizedQuery


# Config načítání
def getenv(key, default=""):
    return os.getenv(key, default)

ENV_KEY_NAMES = {
    "AZURE_COGNITIVE_ACCOUNT_NAME": "AZURE_COGNITIVE_ACCOUNT_NAME",
    "AZURE_EMBEDDING_DEPLOYMENT_NAME": "AZURE_EMBEDDING_DEPLOYMENT_NAME",
    "AZURE_SEARCH_SERVICE_NAME": "AZURE_SEARCH_SERVICE_NAME",
    "AZURE_SEARCH_INDEX_NAME": "AZURE_SEARCH_INDEX_NAME",
    "AZURE_SEARCH_API_KEY": "AZURE_SEARCH_API_KEY",
    "OPENAI_API_KEY": "OPENAI_API_KEY",
    "AZURE_CHAT_DEPLOYMENT_NAME": "AZURE_CHAT_DEPLOYMENT_NAME"
}

def getenv(key_name, default_value=None):
    proxied_key_name = ENV_KEY_NAMES.get(key_name, None)
    assert proxied_key_name is not None, f"missing {key_name} in proxied list of key_names"
    result = os.getenv(proxied_key_name, default_value)
    return result

search_service = getenv("AZURE_SEARCH_SERVICE_NAME", "")
search_index   = getenv("AZURE_SEARCH_INDEX_NAME", "")
search_api_key = getenv("AZURE_SEARCH_API_KEY","")
ai_api_key     = getenv("OPENAI_API_KEY","")
index = getenv("AZURE_SEARCH_INDEX_NAME")
openai_key = getenv("OPENAI_API_KEY")
search_api_key = getenv("AZURE_SEARCH_API_KEY")

cog_account = getenv("AZURE_COGNITIVE_ACCOUNT_NAME", None)
if not cog_account:
    raise ValueError("Chybí proměnná AZURE_COGNITIVE_ACCOUNT_NAME")
ai_endpoint = f"https://{cog_account}.openai.azure.com"
search_endpoint = f"https://{getenv('AZURE_SEARCH_SERVICE_NAME')}.search.windows.net"
model_name = getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME", "embedding-deployment")
chat_model_name = getenv("AZURE_CHAT_DEPLOYMENT_NAME", "embedding-deployment")

vector_dimensions = 1536

class DocumentResult(BaseModel):
    id: str = Field(..., description="Unikátní ID dokumentu")
    content: str = Field("", description="Textový obsah dokumentu")
    document_folder: Optional[str] = Field(
        None, description="Cesta nebo název složky, ze které dokument pochází"
    )
    score: float = Field(..., description="Relevance skóre z Azure Search")

class SearchPlugin:
    @kernel_function(
        description="Vygeneruje embedding (vektorové zastoupení) pro daný text pomocí Azure OpenAI. Velikost vektoru je 1536.",
        # input_variables=[
        #     {"name": "text", "description": "Text k vektorování"}
        # ]
    )
    async def generate_embedding(self, text: Annotated[str, "Text k vektorování"]) -> List[float]:
        """
        Volá Azure AI Inference EmbeddingsClient pro batch textů.
        Vrací seznam embeddingů (pořadí odpovídá vstupu).
        """

        print(f"generate_embedding for {text}")
        # print("Raw query codepoints:", [hex(ord(c)) for c in text])
        client = AzureOpenAI(
            azure_endpoint=ai_endpoint,
            api_key=ai_api_key,
            api_version="2024-02-01"
        )
        response = client.embeddings.create(model=model_name, input=text, dimensions=int(vector_dimensions))
        # response.data je seznam, každý prvek má .embedding
        embedding = response.data[0].embedding

        # print(f"generate_embedding {embedding}")
        return embedding
    
    @kernel_function(
        description="Najde fragmenty dokumentů v Azure Cognitive Search na základě vektoru. Ocekavana velikost vektoru je 1536.",
        # input_variables=[
        #     {"name": "vector", "description": "Embedding dotazu"}
        # ]
    )
    async def search_by_vector(self, vector: Annotated[List[float], "Vektor dotazu"]) -> List[Dict[str, Any]]:
        
        client = SearchClient(
            endpoint=search_endpoint,
            index_name=index,
            credential=AzureKeyCredential(search_api_key)
        )
        vq = VectorizedQuery(vector=vector, k_nearest_neighbors=10, fields="contentVector")
        # print(f"search_by_vector.pre search {vector}")
        print(f"search_by_vector.pre search {type(vector)}")
        results = client.search(search_text="*", vector_queries=[vq])
        print("search_by_vector.post search")
        docs = [{
            "id": r.get("id"),
            "content": r.get("content", ""),
            "document_folder": r.get("document_folder"),
            "score": r.get("@search.score"),
        } for r in results]
        # print(f"search_by_vector.result\n{docs}")
        return docs    
    
    @kernel_function(
        description="Provede sumarizaci pro zadaný dotaz z daných dokumentů",
        # input_variables=[
        #     {
        #         "name": "documents",
        #         "description": "Seznam dokumentů (id, content, document_folder, score)",
        #         "schema": {
        #             "type": "array",
        #             "items": {
        #                 "type": "object",
        #                 "properties": {
        #                     "id":               { "type": "string" },
        #                     "content":          { "type": "string" },
        #                     "document_folder":  { "type": "string" },
        #                     "score":            { "type": "number" }
        #                 },
        #                 "required": ["id","content","document_folder","score"]
        #             }
        #         }
        #     },
        #     {
        #         "name": "query",
        #         "description": "Původní uživatelský dotaz",
        #         "schema": { "type": "string" }
        #     }
        # ]
    )
    async def summarize(
        self,
        documents: Annotated[
            List[Dict[str, Any]], 
            "Seznam dokumentů: každý má id (str), content (str), document_folder (str) a score (float)"],
        query: Annotated[str, "Původní dotaz"]
    ) -> str:
        client = AzureOpenAI(
            azure_endpoint=ai_endpoint,
            api_key=openai_key,
            api_version="2024-02-01"
        )

        # Sestavíme prompt
        context = "\n\n".join(
            f"[{i+1}] {d['content']}\nSource: {d['document_folder']}"
            for i, d in enumerate(documents)
        )
        prompt = (
            f"Na základě následujících textů odpověz na dotaz:\n{query}\n\n"
            f"Texty:\n{context}\n\n"
            "Ve své odpovědi odkazuj na zdroje [1], [2], ... a na konci uveď jejich seznam s URL."
        )

        response = client.chat.completions.create(model=chat_model_name, messages=[
                {"role": "system", "content": "Jsi nápomocný asistent, cituj zdroje."},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1000)

        # vytáhneme usage
        usage = response.usage  # nebo response["usage"]
        print(f"Prompt tokens: {usage.prompt_tokens}")
        print(f"Completion tokens: {usage.completion_tokens}")
        print(f"Total tokens: {usage.total_tokens}")
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "in": usage.prompt_tokens,
                "out": usage.completion_tokens
            }
        }
    
    @kernel_function(
        description="filtruje dokumenty podle dostupnosti pro uzivatele"
    )
    async def filter_docs(self, documents) -> list:
        # Dummy filtr - vše povoleno
        return documents    

# Pro použití v Azure Functions (async)
import azure.functions as func

kernel = Kernel()
kernel.add_service(
    AzureChatCompletion(
        service_id     = "chat",                  # jméno, kterým bude service identifikována
        api_key        = ai_api_key,              # tvůj OPENAI_API_KEY
        deployment_name= chat_model_name,         # název chat deploymentu
        # base_url       = ai_endpoint,             # tvůj Azure OpenAI endpoint
        api_version    = "2024-02-01",            # stejná verze jako u AzureOpenAI        
        endpoint=ai_endpoint
    )
)

kernel.add_plugin(SearchPlugin(), plugin_name="search")
# 3) Nastavení pro auto volání funkcí
settings = AzureChatPromptExecutionSettings()
settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

async def run_pipeline(query):
    print("run_pipeline")

    # Embedding dotazu
    print("run_pipeline.embedding")
    # embedding = await kernel.Embeddings.generate_embedding(text=query)
    embedding = await kernel.invoke(plugin_name="search", function_name="generate_embedding", text=query)

    # Vyhledání dokumentů
    print("run_pipeline.search_by_vector")
    # docs = await kernel.Embeddings.search_by_vector(vector=embedding)
    docs = await kernel.invoke(plugin_name="search", function_name="search_by_vector", vector=embedding.value)

    # Filtrování (dummy)
    print("run_pipeline.filter_docs")
    # accessible_docs = await kernel.Security.filter_docs(documents=docs)
    accessible_docs=docs
    # docs = await kernel.invoke(plugin_name="Embeddings", function_name="search_by_vector", text=query)

    # Sumarizace
    print("run_pipeline.summarize")
    # summary = await kernel.Sumarize.summarize(documents=accessible_docs, query=query)
    summary = await kernel.invoke(plugin_name="search", function_name="summarize", documents=accessible_docs.value, query=query)
    summary = summary.value
    return {
        "query": query,
        "summary": summary["content"],
        "usage": summary["usage"],
        "documents": accessible_docs.value
    }

async def searchkernelsPluginhandler(req: func.HttpRequest) -> func.HttpResponse:
    print("searchkernelshandler")
    try:
        # body = req.get_json()
        # query = body.get("q") or req.params.get("q")
        query = req.params.get("q")
        if not query:
            return func.HttpResponse("Chybí parametr 'q'", status_code=400)
        # result = asyncio.run(run_pipeline(query))
        print(f"searchkernelshandler.q={query}")

        result = await run_pipeline(query)

        # try:
        #     history = ChatHistory()
        #     history.add_user_message(f"Najdi relevantní části v dokumentech k dotazu \n\n{query}\n\n a shrň odpověď.")
        #     responses = await kernel.get_service(type=AzureChatCompletion).get_chat_message_contents(
        #         chat_history=history,
        #         settings=settings,
        #         kernel=kernel,
        #         arguments=KernelArguments()
        #     )

        #     # výsledek
        #     print("Asistent:", responses[0].content)
        # except Exception as ein:
        #     print(ein)

        return func.HttpResponse(json.dumps(result, ensure_ascii=False), mimetype="application/json", status_code=200)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
    
print("import search_kernels OK")