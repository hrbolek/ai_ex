import os
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from openai import AzureOpenAI

# Config načítání
def getenv(key, default=""):
    return os.getenv(key, default)


openai_key = getenv("OPENAI_API_KEY")
endpoint = f"https://{getenv('AZURE_COGNITIVE_ACCOUNT_NAME')}.openai.azure.com"
model_name = getenv("AZURE_CHAT_DEPLOYMENT_NAME")

from semantic_kernel.functions import kernel_function

@kernel_function()
async def summarize(documents, query) -> str:
    client = AzureOpenAI(
        azure_endpoint=endpoint,
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

    response = client.chat.completions.create(model=model_name, messages=[
            {"role": "system", "content": "Jsi nápomocný asistent, cituj zdroje."},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.3,
        max_tokens=1000)

    return response.choices[0].message.content
