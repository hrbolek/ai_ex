import azure.functions as func
import datetime
import json
import logging
import requests
from openai import AzureOpenAI
import os
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

app = func.FunctionApp()

@app.route(route="search", auth_level=func.AuthLevel.ANONYMOUS)
def query_vector_index(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function for querying vector index.')

    try:
        query = req.params.get('query')  # Retrieve 'text' from query string
        if not query:
            return func.HttpResponse(
                "Please provide a 'query' parameter in the query string.",
                status_code=400
            )
        
        # Extract the API key for Azure OpenAI from environment variables
        api_key = os.getenv("AZURE_OPENAI_API_KEY")  # Ensure this is set in the environment
        if not api_key:
            raise ValueError("Azure OpenAI API key is not set in environment variables.")

        # Initialize the client
        endpoint = "https://ai-acr500896758024.openai.azure.com/"
        client = AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint=endpoint,
            api_key=api_key
        )

        embedding_response = client.embeddings.create(
            model="text-embedding-3-large",
            input=query
        )

        # Extract the embedding vector
        vector = embedding_response.data[0].embedding
        search_service_name = "semantic-search-1"
        index_name = "silly-arch-9ndt33qyrc"

        # Extract the API key from environment variables
        api_key = os.getenv("AZURE_SEARCH_API_KEY")  # Ensure this is set in the environment
        if not api_key:
            raise ValueError("Azure Search API key is not set in environment variables.")

        # Initialize the search client
        endpoint = f"https://{search_service_name}.search.windows.net/"
        credential = AzureKeyCredential(api_key)
        search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
        print("Search client initialized.")
        # Check if the index exists
        # Perform vector search
        results = search_client.search(
            search_text=None,  # No text query
            
            vector_queries=[{
                "vector": vector,
                "kind": "vector",
                "fields": "contentVector",  # The field containing your document embeddings
                "k": 10,  # Number of results to return
                "exhaustive": True  # For higher accuracy (optional)
            }],
            select=["title", "url", "id"]  # Fields to return
        )
        response_data = []
        for result in results:
            response_data.append({
            "id": result["id"],
            "title": result["title"],
            "url": result["url"],
            "score": result["@search.score"]
            })
       
        # Process the results
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error occured: {e}")
        return func.HttpResponse(
            f"Error occured {e}.",
            status_code=500
        )