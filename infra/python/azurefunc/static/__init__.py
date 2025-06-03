import os
import json
import logging
import msal
import requests
import jwt

import azure.functions as func

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI
from result import HTML
# --- HELPERS -------------------------------------------------



def main(req: func.HttpRequest) -> func.HttpResponse:
    html = HTML
    return func.HttpResponse(
        html,
        status_code=200
    )
