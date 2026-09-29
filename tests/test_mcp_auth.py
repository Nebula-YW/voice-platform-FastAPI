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


async def _call(middleware, path, headers=(), *, method="POST", body=b""):
    events = []

    async def send(event):
        events.append(event)

    delivered = False

    async def receive():
        nonlocal delivered
        if delivered:
            return {"type": "http.request", "body": b"", "more_body": False}
        delivered = True
        return {"type": "http.request", "body": body, "more_body": False}

    await middleware(
        {
            "type": "http",
            "method": method,
            "path": path,
            "headers": [(b"host", b"voice.example.test"), *list(headers)],
        },
        receive,
        send,
    )
    return events


def _rpc(method: str) -> bytes:
    return json.dumps({"jsonrpc": "2.0", "id": 1, "method": method}).encode()


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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method",
    ["initialize", "notifications/initialized", "ping", "server/discover", "tools/list"],
)
async def test_mcp_discovery_does_not_require_login(method):
    events = await _call(McpOAuthMiddleware(_app, _settings()), "/mcp", body=_rpc(method))
    assert events[0]["status"] == 200


@pytest.mark.asyncio
async def test_mcp_tool_call_still_requires_login():
    events = await _call(
        McpOAuthMiddleware(_app, _settings()),
        "/mcp/",
        body=_rpc("tools/call"),
    )
    assert events[0]["status"] == 401


@pytest.mark.asyncio
async def test_mixed_batch_still_requires_login():
    body = json.dumps(
        [
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call"},
        ]
    ).encode()
    events = await _call(McpOAuthMiddleware(_app, _settings()), "/mcp", body=body)
    assert events[0]["status"] == 401
