# auth_core.py
import time, json, base64, httpx
from typing import Iterable, Optional, Sequence
from jose import jwt, JWTError, jwk as jose_jwk
# import jwt
DEFAULT_TIMEOUT = httpx.Timeout(5.0)


import logging
class JwksCache:
    def __init__(self, oidc_doc: str, *, ttl_sec: int = 600, client: Optional[httpx.AsyncClient] = None):
        self._oidc_doc = oidc_doc
        self._ttl = ttl_sec
        self._jwks = None
        self._exp = 0
        self._client = client  # může být sdílený z lifespan

    async def _client_get(self, url: str) -> dict:
        if self._client:
            return (await self._client.get(url, timeout=DEFAULT_TIMEOUT)).json()
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as c:
            return (await c.get(url)).json()

    async def get(self) -> dict:
        now = time.time()
        if self._jwks and now < self._exp:
            return self._jwks
        conf = await self._client_get(self._oidc_doc)
        self._jwks = await self._client_get(conf["jwks_uri"])
        self._exp = now + self._ttl
        return self._jwks

    async def get_key_by_kid(self, kid: str) -> Optional[dict]:
        jwks = await self.get()
        for k in jwks.get("keys", []):
            if k.get("kid") == kid:
                return k
        # key miss → okamžitý refresh (rotace klíčů)
        self._jwks, self._exp = None, 0
        jwks = await self.get()
        for k in jwks.get("keys", []):
            if k.get("kid") == kid:
                return k
        return None


class EntraIDClient:
    def __init__(
        self,
        tenant_id: str,
        audience: str | Sequence[str] | None,   # povol více aud nebo None
        *,
        http_client: Optional[httpx.AsyncClient] = None,
        leeway_sec: int = 60,
        enforce_access_token: bool = False,
    ):
        self.tenant_id = tenant_id
        self.issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        self.oidc_doc = f"{self.issuer}/.well-known/openid-configuration"
        self.jwks_cache = JwksCache(self.oidc_doc, client=http_client)
        if audience is None:
            self.audience: Optional[list[str]] = None
        elif isinstance(audience, str):
            self.audience = [audience]
        else:
            self.audience = list(audience)
        self.leeway = leeway_sec
        self.enforce_access = enforce_access_token

    async def validate_bearer_token(self, authorization_header: str) -> dict:
        if not authorization_header or not authorization_header.startswith("Bearer "):
            raise ValueError("Missing Bearer token")
        token = authorization_header.split(" ", 1)[1]

        try:
            unverified_header = jwt.get_unverified_header(token)
            unverified_claims = jwt.get_unverified_claims(token)
        except JWTError as e:
            raise ValueError(f"Invalid token header: {e}")
        kid = unverified_header.get("kid")
        alg = unverified_header.get("alg", "RS256")
        if not kid:
            raise ValueError("Missing 'kid' in token header")



        jwk_dict = await self.jwks_cache.get_key_by_kid(kid)
        if not jwk_dict:
            raise ValueError("Signing key not found")
        alg = unverified_header.get("alg", "RS256")
        # Vytvoř jose-key z JWK
        key_obj = jose_jwk.construct(jwk_dict, algorithm=alg)

        try:
            claims = jwt.decode(
                token,
                key_obj,
                algorithms=[unverified_header.get("alg", "RS256")],
                # audience=self.audience,
                issuer=self.issuer,
                options={
                    "verify_signature": True,
                    # "verify_aud": self.audience is not None,
                    "verify_aud": False,
                    "verify_iss": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_at_hash": False,
                },
                # leeway=self.leeway,
            )
        except JWTError as e:
            logging.info("JWT verification failed: %s", e)
            logging.info("JWT header: alg=%s, kid=%s", alg, kid)
            logging.info(
                "Unverified claims: iss=%s, aud=%s, scp=%s, roles=%s, tid=%s, oid=%s",
                unverified_claims.get("iss"),
                unverified_claims.get("aud"),
                unverified_claims.get("scp"),
                unverified_claims.get("roles"),
                unverified_claims.get("tid"),
                unverified_claims.get("oid"),
            )
            logging.info("Expected issuer=%s; audience(s)=%s", self.issuer, self.audience)            
            raise ValueError(f"Invalid token: {e}")

        # Volitelně vynutit, že je to access token (ne ID token)
        if self.enforce_access and not (claims.get("scp") or claims.get("roles")):
            raise ValueError("Token is not an access token (missing 'scp' and 'roles')")

        return claims


def make_easyauth_headers_from_claims(claims: dict) -> dict[str, str]:
    principal = {
        "auth_typ": "aad",
        "name_typ": "name",
        "role_typ": "roles",
        "claims": [
            {"typ": k, "val": (",".join(map(str, v)) if isinstance(v, list) else str(v))}
            for k, v in claims.items()
        ],
    }
    b64 = base64.b64encode(json.dumps(principal).encode()).decode()
    out = {"x-ms-client-principal": b64}
    if oid := (claims.get("oid") or claims.get("sub")):
        out["x-ms-client-principal-id"] = str(oid)
    if upn := (claims.get("preferred_username") or claims.get("unique_name") or claims.get("name")):
        out["x-ms-client-principal-name"] = str(upn)
    return out


def require_authorization(
    claims: dict | None,
    *,
    scopes: Optional[Iterable[str]] = None,
    roles: Optional[Iterable[str]] = None,
):
    if not claims:
        raise PermissionError("Not authenticated")
    if scopes:
        granted = set((claims.get("scp") or "").split())
        if not set(scopes).issubset(granted):
            raise PermissionError("Insufficient scope")
    if roles:
        granted_roles = set(claims.get("roles") or [])
        if not set(roles).issubset(granted_roles):
            raise PermissionError("Insufficient role")
    return True