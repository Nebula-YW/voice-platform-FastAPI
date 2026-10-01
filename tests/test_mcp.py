from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from mcp import Client

from api import mcp_server
from api.app import app
from api.mcp_server import mcp


def _json_message(response) -> dict:
    assert response.headers["content-type"].startswith("application/json")
    return response.json()


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


@pytest.mark.asyncio
async def test_synthesize_returns_writable_structured_audio(monkeypatch):
    audio = b"ID3\x04\x00test-mp3"

    async def fake_synthesize_speech(**_kwargs):
        return SimpleNamespace(audio=audio, voice="zh-CN-XiaoxiaoNeural")

    monkeypatch.setattr(mcp_server, "synthesize_speech", fake_synthesize_speech)
    async with Client(mcp) as client:
        result = await client.call_tool(
            "synthesize_speech_audio",
            {"text": "你好", "voice": "zh-CN-XiaoxiaoNeural"},
        )

    assert result.is_error is False
    payload = result.structured_content or {}
    assert payload["audio_base64"] == "SUQzBAB0ZXN0LW1wMw=="
    assert payload["mime_type"] == "audio/mpeg"
    assert payload["format"] == "mp3"
    assert payload["byte_length"] == len(audio)
    assert payload["sha256"]
    assert result.content[0].mime_type == "audio/mpeg"


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
        initialized = _json_message(redirected)
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
        payload = _json_message(detected)["result"]["structuredContent"]
        assert payload["language"] == "en"


def test_mcp_http_modern_discover_2026_wire():
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }
    with TestClient(app) as client:
        response = client.post(
            "/mcp",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "server/discover",
                "params": {
                    "_meta": {
                        "io.modelcontextprotocol/protocolVersion": "2026-07-28",
                        "io.modelcontextprotocol/clientInfo": {
                            "name": "wire-smoke",
                            "version": "0",
                        },
                        "io.modelcontextprotocol/clientCapabilities": {},
                    }
                },
            },
        )
        assert response.status_code == 200
        discovered = _json_message(response)
        assert "2026-07-28" in discovered["result"]["supportedVersions"]
