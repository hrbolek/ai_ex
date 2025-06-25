import os
import json
import uuid
import asyncio
import typing
import fastapi 
import jwt
import aiohttp

from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, FileResponse
# from authlib.integrations.starlette_client import OAuth
import os
import logging

import strawberry.fastapi

logging.basicConfig(
    level=logging.INFO,     # nebo DEBUG, pokud chceš detailnější logy
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

import functools
import datetime
def limitedCache(func):
    storage = {
        "counter": 0,
        "datetime": datetime.datetime.now()
    }

    def wrapped(old_cache_func):
        storage["counter"] += 1
        now = datetime.datetime.now()
        delta: datetime.timedelta = now - storage["datetime"]
        if delta.seconds > 60:
            storage["datetime"] = now
            return functools.cache(func)
        else:
            return old_cache_func
        
    return wrapped
    
def lcache(f):
    storage = {
        "counter": 0,
        "result": None,
        "datetime": datetime.datetime.now()
    }
    def wrapped():
        counter = storage["counter"] + 1
        result = storage["result"]
        now = datetime.datetime.now()
        delta: datetime.timedelta = now - storage["datetime"]
        if (delta.seconds > 60) or (counter > 100) or (result is No):
            result = f()
            storage["datetime"] = now
            storage["result"] = result
            storage["counter"] = 0
            return result
        else:
            storage["counter"] = counter
            return storage["result"]
    return wrapped

app = FastAPI()
@app.get("/health")
async def health_check():
    logging.info("Health check endpoint called")
    return {"status": "ok"}

@app.get("/check")
async def health_check():
    logging.info("Health check endpoint called")
    return {"check_status": "ok"}

server_metadata_url=f'https://login.microsoftonline.com/{os.getenv("AZURE_TENANT_ID")}/v2.0/.well-known/openid-configuration'
callback_url = "/auth"
simple_database = {}
token_database = {}
def prejson(data):
    return json.dumps(data, indent=4, ensure_ascii=False)

tenant_id = os.getenv("AZURE_TENANT_ID")
jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
jwk_client = jwt.PyJWKClient(jwks_url)

def decodeJWTToken_sync(jwt_token):
    if isinstance(jwt_token, bytes):
        jwt_token = jwt_token.decode("utf-8")
    if not isinstance(jwt_token, str):
        raise ValueError("JWT token must be a string or bytes")

    # Ověření pomocí veřejného klíče z Azure
    client_id = os.getenv("AZURE_CLIENT_ID")
    issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
    signing_key = jwk_client.get_signing_key_from_jwt(jwt_token)

    decoded = jwt.decode(
        jwt_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=client_id,
        issuer=issuer,
        options={"verify_exp": True, "verify_aud": True, "verify_iss": True}
    )
    return decoded

async def decodeJWTToken(jwt_token):
    decoded_token = await asyncio.to_thread(decodeJWTToken_sync, jwt_token)
    return decoded_token
    
async def logged_user_id(request):
    access_token = request.cookies.get("authorization")
    token_data = token_database.get(access_token)
    user_id = None
    if token_data:
        jwt_token = token_data["token_data"].get("id_token") or token_data["token_data"].get("access_token")
        if jwt_token:
            decoded_token = await decodeJWTToken(jwt_token)
            user_id = decoded_token.get("oid")
    return user_id

async def is_user_logged(request):
    access_token = request.cookies.get("authorization")
    token_data = token_database.get(access_token)
    result = None
    if token_data:
        jwt_token = token_data["token_data"].get("id_token") or token_data["token_data"].get("access_token")
        if jwt_token:
            result = await decodeJWTToken(jwt_token)
    return result

@app.get("/")
async def homepage(request: Request):
    # Zjisti, zda uživatel má session/token (např. v cookies, session, headeru...)
    access_token = request.cookies.get("authorization")
    token_data = token_database.get(access_token)
    message = "<div>Hello, Guest! Please <a href='/login'>log in</a></div>."
    if token_data:
        jwt_token = token_data["token_data"].get("id_token") or token_data["token_data"].get("access_token")
        if jwt_token:
            decoded_token = await decodeJWTToken(jwt_token)
            message = f"<pre>token{prejson(decoded_token)}</pre>"

            return FileResponse(serve_file(""))

        else:
            message = "<pre>token not found in token_data</pre>"

    text_response = f"""
    <div>
        <pre>access_token: {access_token}</pre>
        <pre>token_data: {prejson(token_data)}</pre>
        <pre>simple_database: {prejson(simple_database)}</pre>
        <pre>token_database: {prejson(token_database)}</pre>
        {message}
    </div>
    """        
    return fastapi.responses.HTMLResponse(text_response)


@app.get("/login")
async def login(request: Request):
    callback_base_url = f"{request.url.scheme}://{request.url.netloc}"
    from urllib.parse import urlencode
    state = uuid.uuid4().hex  # Generuj bezpečný náhodný stav
    while state in simple_database:
        state = uuid.uuid4().hex
    params = request.query_params
    simple_database[state] = {
        "state": state,
        "redirect_uri": params.get("redirect_uri", "/"),
        "nonce": params.get("nonce", uuid.uuid4().hex)  # Přidání nonce pro bezpečnost
    }  # Ulož stav do jednoduché databáze
    params = {
        "client_id": os.getenv("AZURE_CLIENT_ID"),
        "response_type": "code",
        "redirect_uri": f"{callback_base_url}{callback_url}",
        "response_mode": "query",
        "scope": "openid profile email",
        "state": state
    }
    tenant_id = os.getenv("AZURE_TENANT_ID")
    authorize_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?" + urlencode(params)
    return fastapi.responses.RedirectResponse(authorize_url)

@app.route(callback_url)
async def auth(request: Request):
    params = request.query_params
    logging.info(f"{callback_url} called")
    state = params.get("state")
    code = params.get("code")
    if not state or state not in simple_database:
        # return RedirectResponse(url="/login")
        state_data = {
            "state": state,
            "redirect_uri": "/",
            "nonce": uuid.uuid4().hex  # Přidání nonce pro bezpečnost
        }
        pass
    else:
        state_data = simple_database[state]
        if not state_data.get("redirect_uri"):
            state_data['redirect_uri'] = "/"
    if not code:
        return RedirectResponse(url="/")
    logging.info(f"State: {state}, Code: {code}")
    # https://login.microsoftonline.com/organizations/oauth2/v2.0/token
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    tenant_id = os.getenv("AZURE_TENANT_ID")
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    callback_base_url = f"{request.url.scheme}://{request.url.netloc}"
    token_params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": f"{callback_base_url}{callback_url}"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(token_url, data=token_params) as entra_response:
            if entra_response.status != 200:
                text = await entra_response.text()
                logging.error(f"Error fetching token: {entra_response.status} - {text}")
                return RedirectResponse(url="/")
            token_data = await entra_response.json()
            logging.info(f"got token_data: {token_data}")
            access_token = token_data.get("access_token")
            token_database[access_token] = {
                "token_data": token_data
            }
            if not access_token:
                logging.info("auth.redirecting")
                return RedirectResponse(url="/")
            result = RedirectResponse(url=state_data['redirect_uri'])
            cookie_setup = {
                "key": "authorization",
                "value": access_token,
                "httponly": True,
                "max_age": token_data.get("expires_in", 3600),  # Výchozí hodnota 1 hodina
                "secure": True if request.url.scheme == "https" else False
            }
            result.set_cookie(**cookie_setup)

            # # Získání informací o uživateli
            # logging.info("going to query user info")
            # user_info_url = "https://graph.microsoft.com/v1.0/me"
            # headers = {"Authorization": f"Bearer {access_token}"}
            # async with session.get(user_info_url, headers=headers) as user_response:
            #     if user_response.status != 200:
            #         return RedirectResponse(url="/")
            #     user_info = await user_response.json()
            # token_database[access_token] = {
            #     "user": user_info,
            #     "token_data": token_data
            # }

    return result

# Volitelně endpoint na odhlášení
@app.get("/logout")
async def logout(request: Request):
    access_token = request.cookies.get("authorization")
    token_data = token_database.get(access_token)
    if not token_data:
        return RedirectResponse(url="/")
    del token_database[access_token]
    result = RedirectResponse(url="/")
    result.delete_cookie("authorization")
    # request.session.pop('user', None)
    return result


import strawberry
from strawberry.fastapi import GraphQLRouter

async def get_context(
    self, request: typing.Union[Request, fastapi.WebSocket], response: typing.Union[fastapi.Response, fastapi.WebSocket]
) :  # pragma: no cover -> strawberry.fastapi.fastapi.BaseContext
    authcookie = request.cookies.get("authorization")
    return {
        "request": Request,

    }
    # raise ValueError("`get_context` is not used by FastAPI GraphQL Router")

from .gql import schema
graphql_app = GraphQLRouter(
    schema=schema, 
    # graphiql=True, 
    allow_queries_via_get=False,
    multipart_uploads_enabled=True
)

# FILE_PATH = os.path.join(os.path.dirname(__file__), "static", "graphiql.html")
# @app.get("/gql", response_class=fastapi.responses.FileResponse)
# async def graphiql():
#     return FILE_PATH

app.include_router(graphql_app, prefix="/gql")


def serve_file(relative):
    if relative == "":
        relative = "frontend/index.html"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "static", relative)
    return FILE_PATH
 
from fastapi.staticfiles import StaticFiles
app.mount("/assets", StaticFiles(directory="backend/static/assets"), name="static")
# @app.get("/assets")
# async def serve_assets