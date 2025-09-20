# middleware_easyauth.py
from __future__ import annotations
from typing import Iterable, Callable, Optional
from urllib.parse import urlencode

import logging

from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .core import EntraIDClient, make_easyauth_headers_from_claims, require_authorization

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
class EntraEasyAuthMiddleware(BaseHTTPMiddleware):

    def __init__(
        self,
        app,
        *,
        entra_client: EntraIDClient,
        pass_through: Iterable[str] = (),           # cesty/prefixy, které mají projít bez auth
        login_path: str = "/login",                 # login endpoint (cesta nebo jméno routy)
        external_base_url: str | None = None,       # veřejná URL za reverse proxy (např. https://app.example.com)
        redirect_on_unauth: bool = True,            # u GET/HEAD přesměrovat na login místo 401
        cookie_name: str = "authorization",         # název cookie s access tokenem
        add_easyauth_headers: bool = True,          # doplnit X-MS-CLIENT-PRINCIPAL* hlavičky
        propagate_cookie_to_bearer: bool = True,    # když chybí Authorization, udělat ho z cookie
        csrf_cookie_name: str = "csrf-token",       # pro double-submit (jen pokud autentizace jde z cookie)
        csrf_header_name: str = "x-csrf-token",
        require_csrf: bool = False,                 # zapnout CSRF kontrolu pro unsafe metody
    ):
        super().__init__(app)
        self.entra = entra_client
        self.pass_through = tuple(pass_through)
        self.login_path = login_path
        self.external_base_url = external_base_url.rstrip("/") if external_base_url else None
        self.redirect_on_unauth = redirect_on_unauth
        self.cookie_name = cookie_name
        self.add_easyauth_headers = add_easyauth_headers
        self.propagate_cookie_to_bearer = propagate_cookie_to_bearer
        self.csrf_cookie_name = csrf_cookie_name.lower()
        self.csrf_header_name = csrf_header_name.lower()
        self.require_csrf = require_csrf

    # ---- helpers -------------------------------------------------------------

    def _is_pass_through(self, path: str) -> bool:
        return any(path.startswith(p) for p in self.pass_through)

    def _build_login_url(self, request: Request) -> str:
        # základ login URL (cesta nebo pojmenovaná routa)
        if self.login_path.startswith("/"):
            if self.external_base_url:
                base = self.external_base_url + self.login_path
            else:
                base = str(request.base_url).rstrip("/") + self.login_path
        else:
            # jméno routy
            base = str(request.url_for(self.login_path))
        # přidej ?next=<absolute-url> (vč. query)
        return f"{base}?{urlencode({'next': str(request.url)})}"

    @staticmethod
    def _get_header(scope_headers: list[tuple[bytes, bytes]], key_lower: bytes) -> Optional[bytes]:
        for k, v in scope_headers:
            if k.lower() == key_lower:
                return v
        return None

    @staticmethod
    def _set_header(scope_headers: list[tuple[bytes, bytes]], key: str, value: str) -> None:
        scope_headers.append((key.encode("latin-1"), value.encode("latin-1")))

    def _check_csrf(self, request: Request) -> Optional[JSONResponse]:
        """Double-submit: pro unsafe metody vyžaduj shodu cookie vs. header."""
        if request.method in UNSAFE_METHODS:
            cookie_val = request.cookies.get(self.csrf_cookie_name)
            # najdi hlavičku case-insensitively
            hdrs = list(request.scope.get("headers", []))
            header_val = None
            for k, v in hdrs:
                if k.decode().lower() == self.csrf_header_name:
                    header_val = v.decode()
                    break
            if not cookie_val or not header_val or cookie_val != header_val:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "CSRF validation failed"},
                )
        return None

    # ---- main dispatch -------------------------------------------------------

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # CORS preflight neautentizujeme
        if request.method == "OPTIONS":
            return await call_next(request)

        if self._is_pass_through(path):
            return await call_next(request)

        # připrav Authorization z cookie, pokud chybí
        hdrs = list(request.scope.get("headers", []))
        auth_hdr = self._get_header(hdrs, b"authorization")
        token_from_cookie = request.cookies.get(self.cookie_name)

        if not auth_hdr and self.propagate_cookie_to_bearer and token_from_cookie:
            bearer_val = token_from_cookie if token_from_cookie.lower().startswith("bearer ") else f"Bearer {token_from_cookie}"
            self._set_header(hdrs, "authorization", bearer_val)
            request.scope["headers"] = hdrs
            auth_hdr = bearer_val.encode()

        # volitelná CSRF ochrana, jen pokud autentizace jde z cookie
        if self.require_csrf and token_from_cookie:
            csrf_error = self._check_csrf(request)
            if csrf_error:
                return csrf_error

        # ověř token
        try:
            logging.info("testing token")
            claims = await self.entra.validate_bearer_token(
                (auth_hdr.decode() if isinstance(auth_hdr, (bytes, bytearray)) else auth_hdr) or ""
            )
            logging.info("token is ok")
        except ValueError as e:
            logging.info((
                "token is NOT ok"
                f" (error: {e}, "
            ))
            if self.redirect_on_unauth and request.method in {"GET", "HEAD"}:
                return RedirectResponse(self._build_login_url(request), status_code=302)
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(e) or "Unauthorized"},
            )

        # ulož claims do request.state
        request.state.principal = claims

        # doplň EasyAuth hlavičky (do downstream/mounted apps)
        if self.add_easyauth_headers:
            ea = make_easyauth_headers_from_claims(claims)
            hdrs = list(request.scope.get("headers", []))
            for k, v in ea.items():
                self._set_header(hdrs, k, v)
            request.scope["headers"] = hdrs

        return await call_next(request)


# Guard pro endpointy (scopes/roles)
def require(scopes: Optional[Iterable[str]] = None, roles: Optional[Iterable[str]] = None):
    def _guard(request: Request):
        claims = getattr(request.state, "principal", None)
        try:
            require_authorization(claims, scopes=scopes, roles=roles)
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e))
        return claims
    return _guard
