import asyncio

import os
import json
from semantic_kernel import Kernel

from .AccessControlSkill import filter_docs
from .AzureSearchSkill import search_by_vector
from .EmbeddingSkill import generate_embedding
from .SummarizationSkill import summarize

# Config načítání
def getenv(key, default=""):
    return os.getenv(key, default)

async def run_pipeline(query):
    print("run_pipeline")
    kernel = Kernel()


    kernel.add_function(function=generate_embedding, function_name="generate_embedding", plugin_name="Embeddings")
    print("run_pipeline.1 add")
    kernel.add_function(function=search_by_vector, function_name="search_by_vector", plugin_name="Embeddings")
    kernel.add_function(function=filter_docs, function_name="filter_docs", plugin_name="Security")
    kernel.add_function(function=summarize, function_name="summarize", plugin_name="Sumarize")

    # Embedding dotazu
    print("run_pipeline.embedding")
    # embedding = await kernel.Embeddings.generate_embedding(text=query)
    embedding = await kernel.invoke(plugin_name="Embeddings", function_name="generate_embedding", text=query)

    # Vyhledání dokumentů
    print("run_pipeline.search_by_vector")
    # docs = await kernel.Embeddings.search_by_vector(vector=embedding)
    docs = await kernel.invoke(plugin_name="Embeddings", function_name="search_by_vector", vector=embedding.value)

    # Filtrování (dummy)
    print("run_pipeline.filter_docs")
    # accessible_docs = await kernel.Security.filter_docs(documents=docs)
    accessible_docs=docs
    # docs = await kernel.invoke(plugin_name="Embeddings", function_name="search_by_vector", text=query)

    # Sumarizace
    print("run_pipeline.summarize")
    # summary = await kernel.Sumarize.summarize(documents=accessible_docs, query=query)
    summary = await kernel.invoke(plugin_name="Sumarize", function_name="summarize", documents=accessible_docs.value, query=query)
    return {
        "query": query,
        "summary": summary.value,
        "documents": accessible_docs.value
    }

# Pro použití v Azure Functions (async)
import azure.functions as func

async def searchkernelshandler(req: func.HttpRequest) -> func.HttpResponse:
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
        return func.HttpResponse(json.dumps(result, ensure_ascii=False), mimetype="application/json", status_code=200)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
    
print("import search_kernels OK")