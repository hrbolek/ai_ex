import os

from openai import AzureOpenAI

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

def getenv(key_name, default_value):
    proxied_key_name = ENV_KEY_NAMES.get(key_name, None)
    assert proxied_key_name is not None, f"missing {key_name} in proxied list of key_names"
    result = os.getenv(proxied_key_name, default_value)
    return result

search_service = getenv("AZURE_SEARCH_SERVICE_NAME", "")
search_index   = getenv("AZURE_SEARCH_INDEX_NAME", "")
search_api_key = getenv("AZURE_SEARCH_API_KEY","")
ai_api_key     = getenv("OPENAI_API_KEY","")

cog_account = getenv("AZURE_COGNITIVE_ACCOUNT_NAME", None)
if not cog_account:
    raise ValueError("Chybí proměnná AZURE_COGNITIVE_ACCOUNT_NAME")
endpoint = f"https://{cog_account}.openai.azure.com"
model_name = getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME", "embedding-deployment")
vector_dimensions = 1536

from semantic_kernel.functions import kernel_function

@kernel_function(
    description="Vygeneruje embedding (vektorové zastoupení) pro daný text pomocí Azure OpenAI.",
    # input_variables=[
    #     {"name": "text", "description": "Text k vektorování"}
    # ]
)
async def generate_embedding(text) -> list[list[float]]:
    """
    Volá Azure AI Inference EmbeddingsClient pro batch textů.
    Vrací seznam embeddingů (pořadí odpovídá vstupu).
    """

    print(f"generate_embedding for {text}")

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=ai_api_key,
        api_version="2024-02-01"
    )
    response = client.embeddings.create(model=model_name, input=text, dimensions=int(vector_dimensions))
    # response.data je seznam, každý prvek má .embedding
    embedding = response.data[0].embedding

    # print(f"generate_embedding {embedding}")
    return embedding