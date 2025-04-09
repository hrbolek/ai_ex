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
async def getUser_id(req: func.HttpRequest) -> str:
    """Extract user ID from the request headers."""
    user_id = req.headers.get('x-ms-client-principal-id')
    # if not user_id:
    #     raise ValueError("User ID not found in request headers.")
    return user_id

async def updateUserQuota(req: func.HttpRequest) -> bool:
    """Update user quota in the database."""
    user_id = await getUser_id(req)
    # Here you would typically update the user's quota in your database.
    # For demonstration purposes, we'll just return True which means that this still can be processed for the user.
    return True


@app.route(route="search", auth_level=func.AuthLevel.ANONYMOUS)
async def query_vector_index(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function for querying vector index.')
    userHasQuota = await updateUserQuota(req)
    if not userHasQuota:
        return func.HttpResponse(
            "User has exceeded their quota.",
            status_code=403
        )

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
        search_service_name = os.getenv("SEARCH_SERVICE_NAME")
        index_name = os.getenv("VECTOR_INDEX_NAME")

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