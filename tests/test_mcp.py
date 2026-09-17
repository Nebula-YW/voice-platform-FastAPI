import json

import pytest
from fastapi.testclient import TestClient
from mcp import Client

from api.app import app
from api.mcp_server import mcp


def _sse_json(response) -> dict:
    for line in response.text.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:])
    raise AssertionError(f"No SSE data in: {response.text[:500]}")


@pytest.mark.asyncio
async def test_detect_language_tool_english():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "detect_language",
            {
                "text": "Hello world, this is a test message in English.",
                "with_confidence": False,
            },
        )
        assert result.is_error is False
        payload = result.structured_content or {}
        assert payload.get("language") == "en"
        assert payload.get("language_name") == "English"


@pytest.mark.asyncio
async def test_detect_language_tool_chinese():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "detect_language",
            {"text": "你好世界，这是一条中文测试消息。", "with_confidence": True},
        )
        assert result.is_error is False
        payload = result.structured_content or {}
        assert payload.get("language") == "zh"
        assert payload.get("confidence") is not None


@pytest.mark.asyncio
async def test_synthesize_unknown_voice_is_tool_error():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "synthesize_speech_audio",
            {"text": "Hello", "voice": "invalid-voice-name"},
        )
        assert result.is_error is True


def test_mcp_http_initialize_and_detect_without_slash_redirect():
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }
    with TestClient(app) as client:
        redirected = client.post(
            "/mcp",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "dep-smoke", "version": "0.0.1"},
                },
            },
            follow_redirects=False,
        )
        assert redirected.status_code == 200
        initialized = _sse_json(redirected)
        assert initialized["result"]["protocolVersion"] == "2025-06-18"
        assert initialized["result"]["serverInfo"]["name"] == "Voice Platform"

        detected = client.post(
            "/mcp",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "detect_language",
                    "arguments": {
                        "text": "Hello world, this is a test message in English.",
                        "with_confidence": False,
                    },
                },
            },
            follow_redirects=False,
        )
        assert detected.status_code == 200
        payload = _sse_json(detected)["result"]["structuredContent"]
        assert payload["language"] == "en"
