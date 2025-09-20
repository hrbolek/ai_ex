# pip install fastapi authlib python-multipart
import os
import json
import jwt
from jwt import InvalidTokenError, PyJWKClientError
import asyncio
import uuid
import aiohttp

from typing import Iterable, Optional
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.responses import RedirectResponse
import fastapi
# from authlib.integrations.starlette_client import OAuth
from starlette.datastructures import URL

import logging

logging.basicConfig(
    level=logging.INFO,     
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

from .toke_store import TokenStore
def create_entra_router(
    *,
    tenant_id: str,
    client_id: str,
    client_secret: str,
    scopes: Iterable[str] = ("openid", "profile", "email"),
    api_audience: str | None = None,
    login_path: str = "/login",
    callback_path: str = "/auth/callback",
    logout_path: str = "/logout",
    session_key: str = "user",                 # kde bude uložen uživatel/claims
    external_base_url: str | None = None,      # např. "https://app.example.com"
):
    """
    Vytvoří APIRouter s /login, /auth/callback, /logout a dependency require_auth().
    Router můžeš připojit pod libovolný prefix a funguje i za reverzní proxy.
    """
    router = APIRouter()
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    jwks_url  = f"{authority}/discovery/v2.0/keys"
    jwk_client = jwt.PyJWKClient(jwks_url)

    issuer = f"{authority}/v2.0"         # reuse v decodeJWTToken_sync
    callback_url = callback_path         # "/auth" nebo "/auth/callback" podle argumentu

    simple_database = {}
    token_database = TokenStore()
    token_database.start()

    def prejson(data):
        return json.dumps(data, indent=4, ensure_ascii=False)

    def decodeJWTToken_sync(jwt_token: str) -> dict:
        try:
            signing_key = jwk_client.get_signing_key_from_jwt(jwt_token)
        except (PyJWKClientError, InvalidTokenError) as e:
            raise ValueError(f"Signing key error: {e}") from e

        audiences = [client_id]
        if api_audience:
            audiences.append(api_audience)

        try:
            return jwt.decode(
                jwt_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=audiences,
                issuer=issuer,
                options={"verify_exp": True, "verify_aud": True, "verify_iss": True},
            )
        except InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}") from e

    async def decodeJWTToken(jwt_token):
        decoded_token = await asyncio.to_thread(decodeJWTToken_sync, jwt_token)
        return decoded_token
        
    # ------- Dependency pro chráněné routy -------
    def require_auth(
        required_scopes: Optional[Iterable[str]] = None,
        required_roles: Optional[Iterable[str]] = None,
        **aliases,  # např. scopes=["Api.Read"] nebo scopes_alias="scopes" (z query param)
    ):
        async def _dep(request: Request):
            token = request.cookies.get("authorization")
            scopes_alias = aliases.get("scopes")
            if scopes_alias is not None and required_scopes is None:
                required_scopes = scopes_alias
            if not token:
                raise HTTPException(status_code=401, detail="Not authenticated")

            try:
                claims = await decodeJWTToken(token)
            except ValueError as e:
                raise HTTPException(status_code=401, detail=str(e))
            # scopes
            if required_scopes:
                granted = set((claims.get("scp") or "").split())
                if not set(required_scopes).issubset(granted):
                    raise HTTPException(status_code=403, detail="Insufficient scope")
            # roles
            if required_roles:
                roles = set(claims.get("roles") or [])
                if not set(required_roles).issubset(roles):
                    raise HTTPException(status_code=403, detail="Insufficient role")
            return claims
        return _dep


    # ------- Endpoints -------
    @router.get(login_path, name="entra_login", include_in_schema=False)
    async def login(request: Request):
        # callback_base_url = f"{request.url.scheme}://{request.url.netloc}"
        from urllib.parse import urlencode
        state = uuid.uuid4().hex  # Generuj bezpečný náhodný stav
        while state in simple_database:
            state = uuid.uuid4().hex
        params = request.query_params   
        redir = params.get("redirect_uri", "/")
        if not isinstance(redir, str) or not redir.startswith("/"):
            redir = "/"
        simple_database[state] = {
            "state": state,
            "redirect_uri": redir,
            "nonce": params.get("nonce", uuid.uuid4().hex)  # Přidání nonce pro bezpečnost
        }  # Ulož stav do jednoduché databáze
        scopes_str = " ".join(scopes)  # scopes z argumentu create_entra_router
        base = external_base_url.rstrip("/") if external_base_url else f"{request.url.scheme}://{request.url.netloc}"
        redirect_uri = f"{base}{callback_url}"
        params = {
            "client_id": client_id,
            "response_type": "code",
            # "redirect_uri": f"{request.url.scheme}://{request.url.netloc}{callback_url}",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": scopes_str,        # včetně api://.../Api.Read
            "state": state,
        }
        authorize_url = f"{authority}/oauth2/v2.0/authorize?" + urlencode(params)
        return fastapi.responses.RedirectResponse(authorize_url)

    @router.get(callback_path, name="entra_callback", include_in_schema=False)
    async def auth_callback(request: Request):
        params = request.query_params
        logging.info(f"{callback_url} called")
        state = params.get("state")
        code = params.get("code")
        if not state:
            return RedirectResponse(url="/login")
        state_data = simple_database.pop(state, None)
        if not state_data:
            state_data = {"redirect_uri": "/", "nonce": uuid.uuid4().hex}

        if not state_data.get("redirect_uri"):
            state_data['redirect_uri'] = "/"

        if not code:
            return RedirectResponse(url="/")
        
        logging.info(f"State: {state}, Code: {code}")
        token_url = f"{authority}/oauth2/v2.0/token"

        base = external_base_url.rstrip("/") if external_base_url else f"{request.url.scheme}://{request.url.netloc}"
        redirect_uri = f"{base}{callback_url}"
        token_params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "code": code,
            # "redirect_uri": f"{callback_base_url}{callback_url}"
            "redirect_uri": redirect_uri
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
                expires_in = int(token_data.get("expires_in", 3600))
                
                token_database.set(access_token, token_data, expires_in)
                # token_database[access_token] = {
                #     "token_data": token_data
                # }
                if not access_token:
                    logging.info("auth.redirecting to root, access_token missing")
                    return RedirectResponse(url="/")
                url=state_data['redirect_uri']
                logging.info(f"auth.redirecting to {url}")
                result = RedirectResponse(url=state_data['redirect_uri'])
                cookie_setup = {
                    "key": "authorization",
                    "value": access_token,
                    "httponly": True,
                    # "max_age": token_data.get("expires_in", 3600),  # Výchozí hodnota 1 hodina
                    "secure": True if request.url.scheme == "https" else False,
                    "samesite": "lax",
                    "max_age": int(token_data.get("expires_in", 3600)), # Výchozí hodnota 1 hodina
                    "path": "/",
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

    @router.get(logout_path, name="entra_logout", include_in_schema=False)
    async def logout(request: Request):
        access_token = request.cookies.get("authorization")
        if access_token in token_database:
            token_database.delete(access_token)
            # del token_database[access_token]
        resp = RedirectResponse(url="/")
        resp.delete_cookie("authorization", path="/")
        return resp



    @router.get("/me")
    async def homepage(request: Request):
        # Zjisti, zda uživatel má session/token (např. v cookies, session, headeru...)
        access_token = request.cookies.get("authorization")
        token_data = token_database.get(access_token)
        message = "<div>Hello, Guest! Please <a href='/login?redirect_uri=/me'>log in</a></div>."
        if token_data:
            jwt_token = token_data["token_data"].get("id_token") or token_data["token_data"].get("access_token")
            if jwt_token:
                decoded_token = await decodeJWTToken(jwt_token)
                message = f"<pre>token{prejson(decoded_token)}</pre>"

                return fastapi.responses.HTMLResponse(message)

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


    # Exportuj také hlídač jako atribut (snadné použití v Depends)
    router.require_auth = require_auth  # type: ignore[attr-defined]
    return router
