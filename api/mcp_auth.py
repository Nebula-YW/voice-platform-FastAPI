"""Standard MCP Resource Server authentication for the hosted voice endpoint."""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from threading import Lock
from typing import Any
from urllib.request import Request as UrlRequest
from urllib.request import urlopen
from urllib.parse import urlsplit

import jwt
from starlette.types import ASGIApp, Receive, Scope, Send


@dataclass(frozen=True)
class McpOAuthSettings:
    issuer: str
    resource: str
    jwks_uri: str
    scopes: tuple[str, ...]

    def __post_init__(self) -> None:
        for value in (self.issuer, self.resource, self.jwks_uri):
            parsed = urlsplit(value)
            if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
                raise ValueError("MCP OAuth URLs must use HTTPS outside loopback development")
        resource = urlsplit(self.resource)
        if resource.path != "/mcp":
            raise ValueError("MCP OAuth resource must end in /mcp")

    @classmethod
    def from_environment(cls) -> McpOAuthSettings | None:
        issuer = os.environ.get("MCP_OAUTH_ISSUER", "").strip().rstrip("/")
        if not issuer:
            return None
        resource = os.environ.get(
            "MCP_OAUTH_RESOURCE", "https://voice-fastapi.nebula-tech.design/mcp"
        ).strip().rstrip("/")
        jwks_uri = os.environ.get(
            "MCP_OAUTH_JWKS_URI", f"{issuer}/.well-known/jwks.json"
        ).strip()
        scopes = tuple(value for value in os.environ.get("MCP_OAUTH_SCOPES", "mcp:read").split() if value)
        if not resource or not jwks_uri or not scopes:
            raise RuntimeError("MCP OAuth resource, JWKS URI, and scopes are required")
        return cls(issuer=issuer, resource=resource, jwks_uri=jwks_uri, scopes=scopes)


# These requests only let a client connect and see what Voice can do.
# Generating audio, detecting language, and choosing a voice still require a token.
_PUBLIC_MCP_METHODS = frozenset(
    {
        "initialize",
        "notifications/initialized",
        "ping",
        "server/discover",
        "tools/list",
    }
)
_MAX_MCP_BODY_BYTES = 1_048_576


class _BodyTooLarge(Exception):
    pass


async def _read_http_body(receive: Receive) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        message = await receive()
        if message["type"] == "http.disconnect":
            break
        if message["type"] != "http.request":
            continue
        chunk = message.get("body", b"")
        total += len(chunk)
        if total > _MAX_MCP_BODY_BYTES:
            raise _BodyTooLarge
        chunks.append(chunk)
        if not message.get("more_body", False):
            break
    return b"".join(chunks)


def _replay_http_body(body: bytes) -> Receive:
    delivered = False

    async def receive() -> dict[str, Any]:
        nonlocal delivered
        if delivered:
            return {"type": "http.request", "body": b"", "more_body": False}
        delivered = True
        return {"type": "http.request", "body": body, "more_body": False}

    return receive


def _public_mcp_message(message: Any) -> bool:
    return (
        isinstance(message, dict)
        and isinstance(message.get("method"), str)
        and message["method"] in _PUBLIC_MCP_METHODS
    )


def _public_mcp_body(body: bytes) -> bool:
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False
    if isinstance(payload, list):
        return len(payload) > 0 and all(_public_mcp_message(message) for message in payload)
    return _public_mcp_message(payload)


class _JwksCache:
    def __init__(self, uri: str) -> None:
        self.uri = uri
        self._lock = Lock()
        self._keys: dict[str, Any] = {}
        self._expires_at = 0.0

    def get(self, kid: str) -> Any:
        now = time.time()
        with self._lock:
            if now >= self._expires_at or kid not in self._keys:
                request = UrlRequest(self.uri, headers={"accept": "application/json"})
                with urlopen(request, timeout=5) as response:  # noqa: S310 - configured JWKS URL
                    payload = json.load(response)
                keys = payload.get("keys")
                if not isinstance(keys, list):
                    raise ValueError("JWKS response is invalid")
                self._keys = {
                    str(key["kid"]): jwt.algorithms.OKPAlgorithm.from_jwk(json.dumps(key))
                    for key in keys
                    if isinstance(key, dict)
                    and key.get("kid")
                    and key.get("kty") == "OKP"
                    and key.get("crv") == "Ed25519"
                    and key.get("alg") == "EdDSA"
                    and key.get("use") in (None, "sig")
                }
                self._expires_at = now + 300
            return self._keys[kid]


class McpOAuthMiddleware:
    """Protect only /mcp and expose its standard protected-resource metadata."""

    def __init__(self, app: ASGIApp, settings: McpOAuthSettings | None) -> None:
        self.app = app
        self.settings = settings
        self._jwks = _JwksCache(settings.jwks_uri) if settings else None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        settings = self.settings
        if settings is None or scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path = scope.get("path", "")
        if path == "/.well-known/oauth-protected-resource/mcp":
            host = dict(scope.get("headers", [])).get(b"host", b"").decode().split(":", 1)[0]
            if host != urlsplit(settings.resource).hostname:
                await self._send_response(send, 404, b"Not Found")
                return
            body = json.dumps({
                "resource": settings.resource,
                "authorization_servers": [settings.issuer],
                "scopes_supported": list(settings.scopes),
            }).encode()
            await self._send_response(send, 200, body, ((b"content-type", b"application/json"),))
            return
        if path not in {"/mcp", "/mcp/"}:
            await self.app(scope, receive, send)
            return
        if str(scope.get("method", "")).upper() == "OPTIONS":
            await self.app(scope, receive, send)
            return
        if str(scope.get("method", "")).upper() == "POST":
            try:
                body = await _read_http_body(receive)
            except _BodyTooLarge:
                await self._send_response(send, 413, b'{"error":"too_large"}')
                return
            receive = _replay_http_body(body)
            if _public_mcp_body(body):
                await self.app(scope, receive, send)
                return
        headers = {key.decode().lower(): value.decode() for key, value in scope.get("headers", [])}
        authorization = headers.get("authorization", "")
        match = re.fullmatch(r"Bearer\s+([^\s]+)", authorization, flags=re.IGNORECASE)
        if match is None:
            await self._unauthorized(send, settings)
            return
        try:
            token = match.group(1)
            header = jwt.get_unverified_header(token)
            if header.get("typ") != "at+jwt":
                raise ValueError("invalid token type")
            key = self._jwks.get(str(header["kid"])) if self._jwks else None
            claims = jwt.decode(
                token,
                key=key,
                algorithms=["EdDSA"],
                issuer=settings.issuer,
                audience=settings.resource,
                options={"require": ["iss", "sub", "aud", "scope", "exp", "iat", "jti"]},
            )
            raw_scope = claims["scope"]
            if not isinstance(raw_scope, str) or not re.fullmatch(r"(?:[\x21\x23-\x5B\x5D-\x7E]+)(?:\s+(?:[\x21\x23-\x5B\x5D-\x7E]+))*", raw_scope):
                raise ValueError("invalid scope claim")
            if not set(settings.scopes).issubset(set(raw_scope.split())):
                await self._insufficient_scope(send, settings)
                return
        except Exception:
            await self._unauthorized(send, settings)
            return
        enriched = dict(scope)
        enriched["mcp.oauth.identity"] = {
            "principal_id": claims["sub"],
            "scopes": tuple(str(claims["scope"]).split()),
            "token_id": claims["jti"],
            "expires_at": claims["exp"],
        }
        await self.app(enriched, receive, send)

    @staticmethod
    async def _send_response(send: Send, status: int, body: bytes, headers=()) -> None:
        await send({"type": "http.response.start", "status": status, "headers": headers})
        await send({"type": "http.response.body", "body": body})

    async def _unauthorized(self, send: Send, settings: McpOAuthSettings) -> None:
        parsed = urlsplit(settings.resource)
        metadata = f"{parsed.scheme}://{parsed.netloc}/.well-known/oauth-protected-resource{parsed.path}"
        challenge = f'Bearer resource_metadata="{metadata}", scope="{" ".join(settings.scopes)}"'
        await self._send_response(
            send,
            401,
            b'{"error":"invalid_token"}',
            ((b"content-type", b"application/json"), (b"cache-control", b"no-store"), (b"www-authenticate", challenge.encode())),
        )

    async def _insufficient_scope(self, send: Send, settings: McpOAuthSettings) -> None:
        parsed = urlsplit(settings.resource)
        metadata = f"{parsed.scheme}://{parsed.netloc}/.well-known/oauth-protected-resource{parsed.path}"
        challenge = f'Bearer resource_metadata="{metadata}", error="insufficient_scope", scope="{" ".join(settings.scopes)}"'
        await self._send_response(
            send,
            403,
            b'{"error":"insufficient_scope"}',
            ((b"content-type", b"application/json"), (b"cache-control", b"no-store"), (b"www-authenticate", challenge.encode())),
        )
