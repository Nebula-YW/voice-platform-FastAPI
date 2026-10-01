import base64
import hashlib
import json
import os
from typing import Annotated, Literal

from mcp.server import MCPServer
from mcp.server.mcpserver import Audio
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import CallToolResult, TextContent, ToolAnnotations
from pydantic import Field

from .language_service import get_language_service
from .schemas import LanguageResult, TTSVoice
from .tts_service import VoiceNotFoundError, search_voices, synthesize_speech

DEFAULT_PUBLIC_HOST = "voice-fastapi.nebula-tech.design"

mcp = MCPServer(
    "Voice Platform",
    instructions=(
        "Detect the language of text, search Edge TTS voices, and synthesize MP3 audio. "
        "The synthesize result includes an audio content block and a structured base64 "
        "representation so the calling Agent can save it in the current Project."
    ),
)


def transport_security_settings() -> TransportSecuritySettings:
    public_host = os.environ.get("MCP_PUBLIC_HOST", DEFAULT_PUBLIC_HOST).strip()
    extra_hosts = [
        host.strip()
        for host in os.environ.get("MCP_ALLOWED_HOSTS", "").split(",")
        if host.strip()
    ]
    allowed_hosts = [
        public_host,
        f"{public_host}:*",
        "localhost",
        "localhost:*",
        "127.0.0.1",
        "127.0.0.1:*",
        "[::1]",
        "[::1]:*",
        "testserver",
        "testserver:*",
        *extra_hosts,
    ]
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
        allowed_origins=[],
    )


def streamable_http_app():
    return mcp.streamable_http_app(
        stateless_http=True,
        # Vercel's serverless response path does not reliably flush the
        # request-scoped SSE stream. JSON responses keep each stateless MCP
        # request self-contained while remaining valid Streamable HTTP.
        json_response=True,
        streamable_http_path="/",
        transport_security=transport_security_settings(),
    )


@mcp.tool(
    title="Detect language",
    annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False),
)
def detect_language(
    text: Annotated[
        str, Field(min_length=1, max_length=10000, description="Text to detect.")
    ],
    with_confidence: bool = False,
) -> LanguageResult:
    """Detect the language of a single text. Use this before picking a TTS voice."""
    try:
        result = get_language_service().detect_language(
            text, with_confidence=with_confidence
        )
    except ValueError as error:
        raise ToolError(str(error)) from error
    return LanguageResult(
        text=result["text"],
        language=result["language"],
        language_name=result["language_name"],
        confidence=result.get("confidence"),
    )


@mcp.tool(
    title="Search TTS voices",
    annotations=ToolAnnotations(read_only_hint=True, open_world_hint=True),
)
async def search_tts_voices(
    language: Annotated[
        str | None, Field(description="Language code such as zh or en.")
    ] = None,
    locale: Annotated[
        str | None, Field(description="Locale such as zh-CN or en-US.")
    ] = None,
    gender: Literal["Female", "Male"] | None = None,
    limit: Annotated[
        int, Field(ge=1, le=50, description="Maximum voices to return.")
    ] = 8,
) -> list[TTSVoice]:
    """Search Microsoft Edge TTS voices. Prefer short_name when calling synthesize_speech."""
    voices, _total, _filters = await search_voices(
        language=language,
        locale=locale,
        gender=gender,
        limit=limit,
    )
    return voices


@mcp.tool(
    title="Synthesize speech",
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    ),
)
async def synthesize_speech_audio(
    text: Annotated[
        str, Field(min_length=1, max_length=2000, description="Text to speak.")
    ],
    voice: Annotated[
        str,
        Field(
            description="Voice short_name from search_tts_voices, e.g. zh-CN-XiaoxiaoNeural."
        ),
    ],
    rate: Annotated[
        str | None, Field(description="Rate adjustment such as +20% or -10%.")
    ] = None,
    volume: Annotated[
        str | None, Field(description="Volume adjustment such as +0%.")
    ] = None,
    pitch: Annotated[
        str | None, Field(description="Pitch adjustment such as +50Hz.")
    ] = None,
) -> CallToolResult:
    """Convert text to MP3 speech and return bytes in a directly writable form.

    The audio content is kept for clients with native media handling.  The structured
    representation is deliberately explicit because some MCP clients display audio
    content without exposing its bytes to the Agent.
    """
    try:
        result = await synthesize_speech(
            text=text,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
        )
    except VoiceNotFoundError as error:
        raise ToolError(str(error)) from error
    except RuntimeError as error:
        raise ToolError(str(error)) from error
    encoded = base64.b64encode(result.audio).decode("ascii")
    structured_content = {
        "audio_base64": encoded,
        "mime_type": "audio/mpeg",
        "format": "mp3",
        "byte_length": len(result.audio),
        "sha256": hashlib.sha256(result.audio).hexdigest(),
        "voice": result.voice,
    }
    return CallToolResult(
        content=[
            Audio(data=result.audio, format="mpeg").to_audio_content(),
            TextContent(type="text", text=json.dumps(structured_content)),
        ],
        structured_content=structured_content,
    )
