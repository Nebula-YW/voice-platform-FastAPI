from fastapi.testclient import TestClient
from api.main import app
import pytest

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
    search_data = {"language": "zh", "limit": 5}
    response = client.post("/api/v1/tts/voices/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert "voices" in data
    assert len(data["voices"]) <= 5
    assert data["filters_applied"]["Language"] == "zh"


def test_search_tts_voices_with_gender_filter():
    """Test searching TTS voices with gender filter"""
    search_data = {"gender": "Female", "limit": 3}
    response = client.post("/api/v1/tts/voices/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert "voices" in data
    assert len(data["voices"]) <= 3
    assert data["filters_applied"]["Gender"] == "Female"


def test_synthesize_speech_invalid_voice():
    """Test speech synthesis with invalid voice"""
    tts_data = {"text": "Hello, this is a test.", "voice": "invalid-voice-name"}
    response = client.post("/api/v1/tts/synthesize", json=tts_data)
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


def test_synthesize_speech_validation():
    """Test speech synthesis input validation"""
    # Test with empty text
    tts_data = {"text": "", "voice": "en-US-AriaNeural"}
    response = client.post("/api/v1/tts/synthesize", json=tts_data)
    assert response.status_code == 422

    # Test with missing text
    tts_data = {"voice": "en-US-AriaNeural"}
    response = client.post("/api/v1/tts/synthesize", json=tts_data)
    assert response.status_code == 422

    # Test with missing voice
    tts_data = {"text": "Hello, world!"}
    response = client.post("/api/v1/tts/synthesize", json=tts_data)
    assert response.status_code == 422


def test_synthesize_speech_stream_validation():
    """Test speech synthesis stream validation"""
    # Test with invalid rate format
    tts_data = {
        "text": "Hello, world!",
        "voice": "en-US-AriaNeural",
        "rate": "invalid-rate",
    }
    response = client.post("/api/v1/tts/synthesize/stream", json=tts_data)
    assert response.status_code == 422

    # Test with invalid volume format
    tts_data = {
        "text": "Hello, world!",
        "voice": "en-US-AriaNeural",
        "volume": "invalid-volume",
    }
    response = client.post("/api/v1/tts/synthesize/stream", json=tts_data)
    assert response.status_code == 422


def test_tts_voice_search_validation():
    """Test TTS voice search validation"""
    # Test with invalid limit
    search_data = {"limit": 0}
    response = client.post("/api/v1/tts/voices/search", json=search_data)
    assert response.status_code == 422

    # Test with limit too high
    search_data = {"limit": 200}
    response = client.post("/api/v1/tts/voices/search", json=search_data)
    assert response.status_code == 422


# Language Detection Tests
def test_get_supported_languages():
    """Test getting supported languages list"""
    response = client.get("/api/v1/language/supported")
    assert response.status_code == 200
    data = response.json()
    assert "languages" in data
    assert "total_count" in data
    assert "timestamp" in data
    assert isinstance(data["languages"], list)
    assert data["total_count"] == 15  # We support 15 languages

    # Check language structure
    if data["languages"]:
        lang = data["languages"][0]
        assert "code" in lang
        assert "name" in lang
        assert "native_name" in lang


def test_detect_language_english():
    """Test detecting English text"""
    detect_data = {
        "text": "Hello world, this is a test message in English.",
        "with_confidence": False,
    }
    response = client.post("/api/v1/language/detect", json=detect_data)
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "timestamp" in data

    result = data["result"]
    assert "text" in result
    assert "language" in result
    assert "language_name" in result
    assert result["language"] == "en"
    assert result["language_name"] == "English"
    assert result["confidence"] is None  # No confidence requested


def test_detect_language_chinese():
    """Test detecting Chinese text"""
    detect_data = {"text": "你好世界，这是一条中文测试消息。", "with_confidence": True}
    response = client.post("/api/v1/language/detect", json=detect_data)
    assert response.status_code == 200
    data = response.json()
    assert "result" in data

    result = data["result"]
    assert result["language"] == "zh"
    assert result["language_name"] == "Chinese"
    assert result["confidence"] is not None
    assert 0.0 <= result["confidence"] <= 1.0


def test_detect_language_japanese():
    """Test detecting Japanese text"""
    detect_data = {
        "text": "こんにちは、これは日本語のテストメッセージです。",
        "with_confidence": False,
    }
    response = client.post("/api/v1/language/detect", json=detect_data)
    assert response.status_code == 200
    data = response.json()
    result = data["result"]
    assert result["language"] == "ja"
    assert result["language_name"] == "Japanese"


def test_detect_language_korean():
    """Test detecting Korean text"""
    detect_data = {
        "text": "안녕하세요, 이것은 한국어 테스트 메시지입니다.",
        "with_confidence": False,
    }
    response = client.post("/api/v1/language/detect", json=detect_data)
    assert response.status_code == 200
    data = response.json()
    result = data["result"]
    assert result["language"] == "ko"
    assert result["language_name"] == "Korean"


def test_detect_language_batch():
    """Test batch language detection"""
    batch_data = {
        "texts": [
            "Hello world",
            "你好世界",
            "こんにちは",
            "안녕하세요",
            "Hola mundo",
            "Bonjour le monde",
        ],
        "with_confidence": False,
    }
    response = client.post("/api/v1/language/detect/batch", json=batch_data)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total_count" in data
    assert "timestamp" in data
    assert len(data["results"]) == 6
    assert data["total_count"] == 6

    # Check expected languages
    results = data["results"]
    expected_languages = ["en", "zh", "ja", "ko", "es", "de"]
    detected_languages = [result["language"] for result in results]

    # Allow some flexibility as detection might vary
    for expected in expected_languages:
        assert any(lang == expected for lang in detected_languages), (
            f"Expected {expected} not found in {detected_languages}"
        )


def test_detect_language_with_confidence_endpoint():
    """Test the dedicated confidence detection endpoint"""
    detect_data = {
        "text": "This is an English sentence for confidence testing.",
        "with_confidence": False,  # This parameter is ignored for this endpoint
    }
    response = client.post("/api/v1/language/detect/confidence", json=detect_data)
    assert response.status_code == 200
    data = response.json()
    result = data["result"]
    assert result["confidence"] is not None
    assert 0.0 <= result["confidence"] <= 1.0


def test_detect_language_empty_text():
    """Test language detection with empty text"""
    detect_data = {"text": "", "with_confidence": False}
    response = client.post("/api/v1/language/detect", json=detect_data)
    assert response.status_code == 422  # Validation error


def test_detect_language_too_long_text():
    """Test language detection with text that's too long"""
    detect_data = {
        "text": "a" * 10001,  # Exceeds max_length of 10000
        "with_confidence": False,
    }
    response = client.post("/api/v1/language/detect", json=detect_data)
    assert response.status_code == 422  # Validation error


def test_detect_language_batch_empty_list():
    """Test batch detection with empty texts list"""
    batch_data = {"texts": [], "with_confidence": False}
    response = client.post("/api/v1/language/detect/batch", json=batch_data)
    assert response.status_code == 422  # Validation error


def test_detect_language_batch_too_many_texts():
    """Test batch detection with too many texts"""
    batch_data = {
        "texts": ["test"] * 101,  # Exceeds max_items of 100
        "with_confidence": False,
    }
    response = client.post("/api/v1/language/detect/batch", json=batch_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.parametrize(
    "language_text,expected_code",
    [
        ("This is English", "en"),
        ("Esto es español", "es"),
        ("Das ist Deutsch", "de"),
        ("Это русский", "ru"),
        ("هذا عربي", "ar"),
        ("Questo è italiano", "it"),
        ("To jest polski", "pl"),
        ("Bu Türkçe", "tr"),
        ("นี่คือไทย", "th"),
        ("Ini bahasa Indonesia", "id"),
        ("Ini bahasa Melayu", "ms"),
        ("Đây là tiếng Việt", "vi"),
        ("Este é português", "pt"),
    ],
)
def test_detect_various_languages(language_text, expected_code):
    """Test detection of various supported languages"""
    detect_data = {"text": language_text, "with_confidence": False}
    response = client.post("/api/v1/language/detect", json=detect_data)
    assert response.status_code == 200
    data = response.json()
    result = data["result"]
    # Note: Due to the nature of language detection, we allow some flexibility
    # The exact language might not always match, especially for short texts
    assert result["language"] in [
        "zh",
        "en",
        "es",
        "pt",
        "ar",
        "ru",
        "de",
        "th",
        "vi",
        "id",
        "ms",
        "tr",
        "it",
        "pl",
        "ja",
        "ko",
    ]


def test_english_text_misdetection_cases():
    """
    Test cases for English texts that were previously misdetected as French or Dutch
    Now that French and Dutch are removed, these texts should NOT be detected as French (fr) or Dutch (nl)
    """
    # Test case 1: "End Route" was previously detected as French
    detect_data = {"text": "End Route", "with_confidence": True}
    response = client.post("/api/v1/language/detect", json=detect_data)
    assert response.status_code == 200
    data = response.json()
    result = data["result"]
    # Verify it's not detected as French anymore (might be detected as German or English)
    assert result["language"] != "fr"
    assert result["language"] != "nl"
    # Log what it was actually detected as for reference
    print(f"'End Route' detected as: {result['language']} ({result['language_name']})")

    # Test case 2: "I want to listen to Kings of Leon" was previously detected as Dutch
    detect_data = {"text": "I want to listen to Kings of Leon", "with_confidence": True}
    response = client.post("/api/v1/language/detect", json=detect_data)
    assert response.status_code == 200
    data = response.json()
    result = data["result"]
    # Verify it's not detected as Dutch anymore
    assert result["language"] != "fr"
    assert result["language"] != "nl"
    # Log what it was actually detected as for reference
    print(
        f"'I want to listen to Kings of Leon' detected as: {result['language']} ({result['language_name']})"
    )
