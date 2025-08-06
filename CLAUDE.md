# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management (UV)
- `uv sync` - Install dependencies from lock file
- `uv add package-name` - Add new dependency
- `uv add --dev package-name` - Add development dependency
- `uv run command` - Run command in project environment
- `uv pip compile pyproject.toml > requirements.txt` - Generate requirements.txt for production deployment (excludes dev dependencies)

### Running the Application
- `uv run uvicorn api.main:app --reload --port 3000` - Start development server
- Access API at http://localhost:3000
- Interactive docs at http://localhost:3000/api/v1/docs

### Testing
- `uv run pytest tests/` - Run all tests
- `uv run pytest tests/ --cov=api` - Run tests with coverage
- `uv run pytest tests/test_all.py -v` - Run specific test file with verbose output

### Code Quality
- `uv run ruff check .` - Run linter
- `uv run ruff format .` - Format code

## Architecture Overview

This is a comprehensive Voice Platform API built with FastAPI, optimized for Vercel deployment with serverless functions. The platform integrates multiple voice processing capabilities including Text-to-Speech (TTS) and intelligent language detection services.

### Project Structure
- `api/main.py` - FastAPI app initialization, CORS middleware, and root endpoint
- `api/routers.py` - All API route handlers (TTS synthesis, language detection)
- `api/schemas.py` - Pydantic models for request/response validation (TTS and language detection models)
- `api/language_service.py` - Language detection service using lingua-rs
- `tests/` - Test suite using pytest and TestClient
- `vercel.json` - Vercel serverless configuration
- `pyproject.toml` - Project dependencies managed by UV

### Key Components

**FastAPI App (`api/main.py`):**
- Configured with custom OpenAPI docs URLs (`/api/v1/docs`, `/api/v1/redoc`)
- CORS middleware configured for all origins (configure for production)
- All API routes prefixed with `/api/v1`

**Router System (`api/routers.py`):**
- Unified router handling voice processing endpoints
- TTS synthesis with Edge TTS integration and voice management
- Language detection with 15-language support via lingua-rs
- Structured logging throughout all voice services
- Comprehensive error handling and validation

**Data Models (`api/schemas.py`):**
- Comprehensive Pydantic models with validation
- Voice synthesis models (TTSSynthesizeRequest, TTSVoice, etc.)
- Language detection models (LanguageDetectRequest, LanguageResult, etc.)
- Unified response patterns with timestamp fields

### API Endpoints Structure
- Root: `/` - Voice Platform API information and service overview
- **Voice Synthesis Services:**
  - `/api/v1/tts/voices` - Get all available TTS voices
  - `/api/v1/tts/voices/search` - Search voices by language, gender, locale
  - `/api/v1/tts/synthesize` - Convert text to speech (metadata response)
  - `/api/v1/tts/synthesize/stream` - Convert text to speech (audio stream)
- **Language Detection Services:**
  - `/api/v1/language/supported` - Get supported languages list
  - `/api/v1/language/detect` - Detect single text language
  - `/api/v1/language/detect/batch` - Batch language detection
  - `/api/v1/language/detect/confidence` - Language detection with confidence

### Deployment Configuration
- Vercel uses `requirements.txt` for deployment
- Development uses `uv.lock` for dependency management
- Function memory: 3009MB, max duration: 300s
- All routes handled by `/api/main` through rewrites

### Testing Strategy
- Uses FastAPI TestClient for comprehensive API testing
- Voice synthesis endpoint testing with voice validation and audio generation
- Language detection testing with multi-language support validation
- Error handling, parameter validation, and edge case coverage
- Batch processing and confidence scoring test scenarios

### Voice Platform Integration Details

**Text-to-Speech (TTS):**
- **Edge TTS Library**: Uses `edge-tts>=6.1.0` for Microsoft's TTS service
- **No API Keys**: Works out-of-the-box without authentication
- **Voice Management**: Async voice discovery and filtering
- **Audio Streaming**: Direct MP3 stream responses  
- **Parameter Support**: Rate, volume, and pitch adjustments
- **Error Handling**: Voice validation and comprehensive error responses

**Language Detection:**
- **Lingua-rs Integration**: Uses `lingua-language-detector>=2.0.0` for high-accuracy detection
- **20 Language Support**: Optimized for Chinese, English, Japanese, Korean, French, German, Spanish, Russian, Italian, Portuguese, Dutch, Polish, Arabic, Hindi, Thai, Vietnamese, Indonesian, Turkish, Swedish, Catalan
- **Confidence Scoring**: Optional confidence values for detection results
- **Batch Processing**: Efficient multi-text language detection
- **Fallback Handling**: Robust error handling with English defaults