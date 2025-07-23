from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Edge TTS API" in data["message"]


# TTS Tests
def test_get_tts_voices():
    """Test getting all TTS voices"""
    response = client.get("/api/v1/tts/voices")
    assert response.status_code == 200
    data = response.json()
    assert "voices" in data
    assert "total_count" in data
    assert "timestamp" in data
    assert isinstance(data["voices"], list)
    assert data["total_count"] >= 0


def test_search_tts_voices_no_filters():
    """Test searching TTS voices without filters"""
    search_data = {}
    response = client.post("/api/v1/tts/voices/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert "voices" in data
    assert "total_count" in data
    assert "filtered_count" in data
    assert "filters_applied" in data
    assert "timestamp" in data


def test_search_tts_voices_with_language_filter():
    """Test searching TTS voices with language filter"""
    search_data = {
        "language": "zh",
        "limit": 5
    }
    response = client.post("/api/v1/tts/voices/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert "voices" in data
    assert len(data["voices"]) <= 5
    assert data["filters_applied"]["Language"] == "zh"


def test_search_tts_voices_with_gender_filter():
    """Test searching TTS voices with gender filter"""
    search_data = {
        "gender": "Female",
        "limit": 3
    }
    response = client.post("/api/v1/tts/voices/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert "voices" in data
    assert len(data["voices"]) <= 3
    assert data["filters_applied"]["Gender"] == "Female"


def test_synthesize_speech_invalid_voice():
    """Test speech synthesis with invalid voice"""
    tts_data = {
        "text": "Hello, this is a test.",
        "voice": "invalid-voice-name"
    }
    response = client.post("/api/v1/tts/synthesize", json=tts_data)
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


def test_synthesize_speech_validation():
    """Test speech synthesis input validation"""
    # Test with empty text
    tts_data = {
        "text": "",
        "voice": "en-US-AriaNeural"
    }
    response = client.post("/api/v1/tts/synthesize", json=tts_data)
    assert response.status_code == 422

    # Test with missing text
    tts_data = {
        "voice": "en-US-AriaNeural"
    }
    response = client.post("/api/v1/tts/synthesize", json=tts_data)
    assert response.status_code == 422

    # Test with missing voice
    tts_data = {
        "text": "Hello, world!"
    }
    response = client.post("/api/v1/tts/synthesize", json=tts_data)
    assert response.status_code == 422


def test_synthesize_speech_stream_validation():
    """Test speech synthesis stream validation"""
    # Test with invalid rate format
    tts_data = {
        "text": "Hello, world!",
        "voice": "en-US-AriaNeural",
        "rate": "invalid-rate"
    }
    response = client.post("/api/v1/tts/synthesize/stream", json=tts_data)
    assert response.status_code == 422

    # Test with invalid volume format
    tts_data = {
        "text": "Hello, world!",
        "voice": "en-US-AriaNeural",
        "volume": "invalid-volume"
    }
    response = client.post("/api/v1/tts/synthesize/stream", json=tts_data)
    assert response.status_code == 422


def test_tts_voice_search_validation():
    """Test TTS voice search validation"""
    # Test with invalid limit
    search_data = {
        "limit": 0
    }
    response = client.post("/api/v1/tts/voices/search", json=search_data)
    assert response.status_code == 422

    # Test with limit too high
    search_data = {
        "limit": 200
    }
    response = client.post("/api/v1/tts/voices/search", json=search_data)
    assert response.status_code == 422
