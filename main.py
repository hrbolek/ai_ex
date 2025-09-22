# app.py
import json
import os
from fastapi import FastAPI, Request, Depends, HTTPException

from src.easyauth import EntraEasyAuthMiddleware, EntraIDClient, require, create_entra_router
from src.api import create_api_router

AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "<TENANT_ID>")
AUD    = "api://<YOUR_API_ID_URI>"  # nebo client_id API
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", "AZURE_CLIENT")
app = FastAPI()

entra_router = create_entra_router(
    tenant_id=AZURE_TENANT_ID,
    client_id=AZURE_CLIENT_ID,
    client_secret=AZURE_CLIENT_SECRET,
    login_path="/login",
    callback_path="/auth",
)

entra_client = EntraIDClient(tenant_id=AZURE_TENANT_ID, audience=AUD)

# app.add_middleware(
#     EntraEasyAuthMiddleware,
#     entra_client=entra_client,
#     pass_through=("/public", "/health", "/login", "/auth", "/login/", "/auth/"),
#     login_path="/login",                      # nebo jméno route, pokud používáš url_for("entra_login")
#     # external_base_url="https://app.example.com",  # za reverse proxy
#     redirect_on_unauth=True,
# )

app.include_router(entra_router)

api_router = create_api_router()
app.include_router(api_router)

@app.get("/public/ping")
async def ping(): return {"ok": True}

@app.get("/secure/me")
async def me(claims = Depends(entra_router.require_auth(scopes=["Api.Read"]))):
    return {"tid": claims.get("tid"), "oid": claims.get("oid"), "scp": claims.get("scp"), "roles": claims.get("roles")}

