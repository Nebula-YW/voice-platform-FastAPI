import json

import pytest

from api.mcp_auth import McpOAuthMiddleware, McpOAuthSettings


def _settings() -> McpOAuthSettings:
    return McpOAuthSettings(
        issuer="https://app.example.test",
        resource="https://voice.example.test/mcp",
        jwks_uri="https://app.example.test/.well-known/jwks.json",
        scopes=("mcp:read",),
    )


async def _app(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"ok"})


async def _call(middleware, path, headers=()):
    events = []
    async def send(event):
        events.append(event)
    await middleware(
        {"type": "http", "path": path, "headers": [(b"host", b"voice.example.test"), *list(headers)]},
        lambda: None,
        send,
    )
    return events


@pytest.mark.asyncio
async def test_protected_resource_metadata_is_standard():
    events = await _call(McpOAuthMiddleware(_app, _settings()), "/.well-known/oauth-protected-resource/mcp")
    assert events[0]["status"] == 200
    payload = json.loads(events[1]["body"])
    assert payload["resource"] == "https://voice.example.test/mcp"
    assert payload["authorization_servers"] == ["https://app.example.test"]


@pytest.mark.asyncio
async def test_mcp_requires_bearer_token():
    events = await _call(McpOAuthMiddleware(_app, _settings()), "/mcp")
    assert events[0]["status"] == 401
    headers = dict(events[0]["headers"])
    assert b"resource_metadata=\"https://voice.example.test/.well-known/oauth-protected-resource/mcp\"" in headers[b"www-authenticate"]
