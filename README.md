# Voice Platform API

A comprehensive voice processing platform built with FastAPI and MCP, optimized for Vercel deployment with serverless functions. The platform integrates Text-to-Speech (TTS) and intelligent language detection services for complete voice processing solutions.

## ✨ Features

### Voice Processing Capabilities
- **Text-to-Speech (TTS)** - Microsoft Edge's online text-to-speech service with 200+ voices
- **Language Detection** - High-accuracy language detection supporting 15 languages using lingua-rs
- **Voice Management** - Advanced voice search and filtering capabilities
- **Batch Processing** - Efficient batch language detection for multiple texts
- **Confidence Scoring** - Optional confidence values for language detection results

### Technical Features
- **FastAPI** - Modern, fast web framework for building APIs
- **Vercel Ready** - Optimized for Vercel serverless deployment
- **Auto Documentation** - Interactive API docs with Swagger UI
- **CORS Support** - Cross-origin resource sharing configured
- **Environment Variables** - Dotenv support for configuration
- **Pydantic Models** - Comprehensive data validation and serialization
- **Structured Logging** - Built-in logging configuration
- **Testing Setup** - Pytest configuration with comprehensive test coverage
- **Type Hints** - Full type annotations throughout
- **MCP 2** - Official Model Context Protocol Python SDK 2 Streamable HTTP tools
- **UV Package Manager** - Fast Python package manager with lock file support

## 🚀 Quick Start

### Local Development

1. **Clone and install dependencies:**
```bash
git clone <your-repo>
cd voice-platform-api
uv sync
```

2. **Run the development server:**
```bash
uv run uvicorn main:app --reload --port 3000
```

3. **Visit your API:**
- API: http://localhost:3000
- Interactive docs: http://localhost:3000/api/v1/docs
- ReDoc: http://localhost:3000/api/v1/redoc
- MCP (SDK 2 Streamable HTTP): http://localhost:3000/mcp

### Deploy to Vercel

1. **Push to GitHub** and connect to Vercel
2. **Deploy** - Vercel will automatically detect the FastAPI app
3. **Environment Variables** - Add any required env vars in Vercel dashboard

## 📁 Project Structure

```
voice-platform-api/
├── api/
│   ├── __init__.py
│   ├── app.py               # FastAPI app, CORS, REST routes, MCP mount
│   ├── mcp_server.py        # MCP 2 tools (language, voices, synthesize)
│   ├── routers.py           # Voice processing API routes
│   ├── schemas.py           # Pydantic models for TTS and language detection
│   ├── tts_service.py       # Edge TTS voice search and synthesis
│   └── language_service.py  # Language detection service using lingua-rs
├── tests/
│   ├── conftest.py          # Test configuration
│   ├── test_all.py          # REST API test cases
│   └── test_mcp.py          # MCP 2 in-process tool tests
├── .env.example             # Example environment variables
├── .gitignore              # Git ignore file
├── vercel.json              # Vercel configuration
├── requirements.txt         # Python dependencies (for Vercel)
├── pyproject.toml           # Project configuration with UV dependencies
├── uv.lock                 # UV lock file
├── CLAUDE.md               # Development guidelines
└── README.md
```

## 🔗 API Endpoints

### Core Endpoint
- `GET /` - Voice Platform API information and service overview

### Voice Synthesis Services
- `GET /api/v1/tts/voices` - Get all available TTS voices
- `POST /api/v1/tts/voices/search` - Search voices by language, locale, or gender
- `POST /api/v1/tts/synthesize` - Convert text to speech (returns metadata)
- `POST /api/v1/tts/synthesize/stream` - Convert text to speech (returns audio stream)

### Language Detection Services
- `GET /api/v1/language/supported` - Get supported languages for detection
- `POST /api/v1/language/detect` - Detect language of single text
- `POST /api/v1/language/detect/batch` - Batch detect languages for multiple texts
- `POST /api/v1/language/detect/confidence` - Detect language with confidence score

### MCP 2
- `POST /mcp` - Streamable HTTP MCP using the official Python SDK 2. Tools: `detect_language`, `search_tts_voices`, `synthesize_speech_audio`

## 📊 Example Usage

### Voice Synthesis Examples

#### Get Available Voices
```bash
curl "http://localhost:3000/api/v1/tts/voices"
```

#### Search Chinese Female Voices
```bash
curl -X POST "http://localhost:3000/api/v1/tts/voices/search" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "zh",
    "gender": "Female",
    "limit": 5
  }'
```

#### Generate Speech Metadata
```bash
curl -X POST "http://localhost:3000/api/v1/tts/synthesize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，欢迎使用Voice Platform！",
    "voice": "zh-CN-XiaoxiaoNeural",
    "rate": "+20%",
    "volume": "+0%"
  }'
```

#### Download Speech Audio
```bash
curl -X POST "http://localhost:3000/api/v1/tts/synthesize/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of the Voice Platform!",
    "voice": "en-US-AriaNeural",
    "rate": "+0%"
  }' \
  --output speech.mp3
```

#### Generate Chinese Speech with Custom Parameters
```bash
curl -X POST "http://localhost:3000/api/v1/tts/synthesize/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "这是一个中文语音合成的示例，演示如何调整语速和音调。",
    "voice": "zh-CN-XiaoxiaoNeural",
    "rate": "+50%",
    "volume": "+0%",
    "pitch": "+100Hz"
  }' \
  --output chinese_speech.mp3
```

### Language Detection Examples

#### Detect Single Text Language
```bash
curl -X POST "http://localhost:3000/api/v1/language/detect" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world! This is a test.",
    "with_confidence": true
  }'
```

#### Batch Language Detection
```bash
curl -X POST "http://localhost:3000/api/v1/language/detect/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Hello world!",
      "你好世界！",
      "Hola mundo!",
      "Bonjour le monde!"
    ],
    "with_confidence": true
  }'
```

#### Get Supported Languages
```bash
curl "http://localhost:3000/api/v1/language/supported"
```

#### Language Detection with Confidence
```bash
curl -X POST "http://localhost:3000/api/v1/language/detect/confidence" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "这是一段中文文本，用于测试语言检测功能。"
  }'
```

## 🧪 Testing

Run tests with pytest:
```bash
uv run pytest tests/
```

Run with coverage:
```bash
uv run pytest tests/ --cov=api
```

Run specific test file:
```bash
uv run pytest tests/test_all.py -v
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory (copy from `.env.example`):
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
```env
# Optional environment variables
API_TITLE="Voice Platform API"
API_VERSION="1.0.0"
DEBUG=false

# Voice Platform configuration
# TTS: Edge TTS doesn't require API keys - works out of the box
# Language Detection: lingua-rs works locally without API keys
# All voice processing functionality works without additional configuration
```

### CORS Configuration

Update CORS settings in `api/app.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify domains in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 🔧 Customization

### Voice Platform Integration Features

**Text-to-Speech (TTS):**
- **No API Key Required**: Uses Microsoft Edge's free online TTS service
- **200+ Voices**: Support for multiple languages and dialects
- **Voice Customization**: Adjust rate, volume, and pitch
- **Streaming Audio**: Direct MP3 audio stream output
- **Voice Search**: Filter voices by language, locale, and gender
- **Async Support**: Full async/await support for high performance

**Language Detection:**
- **High Accuracy**: Uses lingua-rs for superior short text detection
- **15 Language Support**: Chinese, English, Spanish, Portuguese, Arabic, Russian, Thai, Vietnamese, Indonesian, Malay, Turkish, Italian, Polish, Japanese, Korean
- **Confidence Scoring**: Optional confidence values for detection results
- **Batch Processing**: Efficient multi-text language detection
- **No API Keys**: Works completely offline with no external dependencies
- **Fast Performance**: Optimized for real-time processing

#### Popular Voice Examples
```python
# Chinese voices
"zh-CN-XiaoxiaoNeural"  # Female, friendly
"zh-CN-YunxiNeural"     # Male, casual
"zh-CN-XiaoyiNeural"    # Female, cute

# English voices  
"en-US-AriaNeural"      # Female, natural
"en-US-DavisNeural"     # Male, professional
"en-GB-SoniaNeural"     # Female, British
```

### Extending Voice Platform

#### Adding New Voice Services
1. **Define Pydantic models** in `api/schemas.py`
2. **Add route handlers** in `api/routers.py` 
3. **Update service logic** in appropriate service files
4. **Update tests** in `tests/test_all.py`
5. **Update documentation** in README.md and CLAUDE.md

#### Integrating Additional TTS Providers
1. Create new service modules (e.g., `api/google_tts_service.py`)
2. Extend schemas with provider-specific models
3. Add provider selection logic in routers
4. Update configuration and documentation

### Database Integration

To add database support:
1. Add your preferred database library to `pyproject.toml` (e.g., `sqlalchemy`, `databases`)
2. Run `uv sync` to install dependencies
3. Create database models and connection logic
4. Update the dependency injection in your routes

### Authentication

To add authentication:
1. Add `python-jose` and `passlib` to `pyproject.toml`
2. Run `uv sync` to install dependencies
3. Create authentication middleware
4. Add protected routes with dependencies

### Adding New Dependencies

To add new packages:
```bash
uv add package-name
```

To add development dependencies:
```bash
uv add --dev package-name
```

## 📈 Production Considerations

- **Environment Variables**: Use Vercel's environment variable system
- **CORS**: Configure appropriate origins for production
- **Rate Limiting**: Consider adding rate limiting middleware for voice services
- **Monitoring**: Add logging and monitoring solutions for voice processing
- **Caching**: Implement Redis caching for frequently requested TTS audio
- **Storage**: Consider cloud storage for generated audio files
- **Language Model Updates**: Monitor lingua-rs updates for improved language detection
- **TTS Service Limits**: Monitor Edge TTS usage and implement fallback providers
- **Dependencies**: Vercel uses `requirements.txt` for deployment, while development uses `uv.lock`

## 🛠️ UV Package Manager

This template uses [UV](https://github.com/astral-sh/uv) as the package manager for faster dependency resolution and installation.

### Key UV Commands

- `uv sync` - Install dependencies from lock file
- `uv add package-name` - Add a new dependency
- `uv add --dev package-name` - Add a development dependency
- `uv remove package-name` - Remove a dependency
- `uv run command` - Run a command in the project environment
- `uv lock` - Update the lock file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
