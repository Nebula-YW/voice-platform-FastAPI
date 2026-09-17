from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from .mcp_server import mcp, streamable_http_app
from .routers import router


class _AcceptMcpWithoutSlash:
    """Serve POST /mcp without a 307. Starlette Mount('/mcp') otherwise redirects to /mcp/."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope.get("path") == "/mcp":
            scope = dict(scope)
            scope["path"] = "/mcp/"
            raw_path = scope.get("raw_path")
            if isinstance(raw_path, (bytes, bytearray)) and not raw_path.endswith(b"/"):
                scope["raw_path"] = raw_path + b"/"
        await self.app(scope, receive, send)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    title="Voice Platform API",
    description="Comprehensive voice processing platform with Text-to-Speech, language detection, and MCP 2 tools",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan,
)

app.add_middleware(_AcceptMcpWithoutSlash)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)

app.include_router(router, prefix="/api/v1")
app.mount("/mcp", streamable_http_app())


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Voice Platform API",
        "description": "Comprehensive voice processing platform with Text-to-Speech and language detection services",
        "docs": "/api/v1/docs",
        "mcp": "/mcp",
        "version": "1.0.0",
        "services": {
            "voice_synthesis": {
                "/api/v1/tts/voices": "Get all available TTS voices",
                "/api/v1/tts/voices/search": "Search TTS voices by filters",
                "/api/v1/tts/synthesize": "Convert text to speech (returns metadata)",
                "/api/v1/tts/synthesize/stream": "Convert text to speech (returns audio stream)",
            },
            "language_detection": {
                "/api/v1/language/supported": "Get supported languages for detection",
                "/api/v1/language/detect": "Detect language of single text",
                "/api/v1/language/detect/batch": "Batch detect languages for multiple texts",
                "/api/v1/language/detect/confidence": "Detect language with confidence score",
            },
            "mcp": {
                "/mcp": "Model Context Protocol 2 Streamable HTTP endpoint",
            },
        },
    }
