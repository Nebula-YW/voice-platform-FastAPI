import io
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from .language_service import get_language_service
from .schemas import (
    LanguageDetectBatchRequest,
    LanguageDetectBatchResponse,
    LanguageDetectRequest,
    LanguageDetectResponse,
    LanguageResult,
    SupportedLanguage,
    SupportedLanguagesResponse,
    TTSSynthesizeRequest,
    TTSSynthesizeResponse,
    TTSVoiceSearchRequest,
    TTSVoiceSearchResponse,
    TTSVoicesResponse,
)
from .tts_service import (
    VoiceNotFoundError,
    list_voices,
    search_voices,
    synthesize_speech,
)

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TTS endpoints
@router.get("/tts/voices", response_model=TTSVoicesResponse)
async def get_tts_voices():
    """获取所有可用的TTS声音列表"""
    try:
        logger.info("Getting all available TTS voices")
        tts_voices = await list_voices()
        return TTSVoicesResponse(voices=tts_voices, total_count=len(tts_voices))
    except Exception as e:
        logger.error(f"Failed to get TTS voices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get TTS voices: {e!s}")


@router.post("/tts/voices/search", response_model=TTSVoiceSearchResponse)
async def search_tts_voices(search_request: TTSVoiceSearchRequest):
    """按条件搜索TTS声音"""
    try:
        logger.info(
            f"Searching TTS voices with filters: {search_request.model_dump(exclude_none=True)}"
        )
        tts_voices, total_count, search_params = await search_voices(
            language=search_request.language,
            locale=search_request.locale,
            gender=search_request.gender,
            limit=search_request.limit,
        )
        return TTSVoiceSearchResponse(
            voices=tts_voices,
            total_count=total_count,
            filtered_count=len(tts_voices),
            filters_applied=search_params,
        )
    except Exception as e:
        logger.error(f"Failed to search TTS voices: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to search TTS voices: {e!s}"
        )


@router.post("/tts/synthesize", response_model=TTSSynthesizeResponse)
async def synthesize_speech_file(request: TTSSynthesizeRequest):
    """将文本转换为语音并返回元数据"""
    try:
        logger.info(
            f"Synthesizing speech for text: {request.text[:50]}... with voice: {request.voice}"
        )
        result = await synthesize_speech(
            text=request.text,
            voice=request.voice,
            rate=request.rate,
            volume=request.volume,
            pitch=request.pitch,
        )
        return TTSSynthesizeResponse(
            message="Speech synthesis completed successfully",
            audio_size=len(result.audio),
            voice_used=result.voice,
            parameters={
                "text_length": result.text_length,
                "voice": result.voice,
                "rate": result.rate,
                "volume": result.volume,
                "pitch": result.pitch,
            },
        )
    except VoiceNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Failed to synthesize speech: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to synthesize speech: {e!s}"
        )


@router.post("/tts/synthesize/stream")
async def synthesize_speech_stream(request: TTSSynthesizeRequest):
    """将文本转换为语音并返回音频流"""
    try:
        logger.info(
            f"Streaming speech synthesis for text: {request.text[:50]}... with voice: {request.voice}"
        )
        result = await synthesize_speech(
            text=request.text,
            voice=request.voice,
            rate=request.rate,
            volume=request.volume,
            pitch=request.pitch,
        )
        return StreamingResponse(
            io.BytesIO(result.audio),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "Content-Length": str(len(result.audio)),
            },
        )
    except VoiceNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Failed to synthesize speech stream: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to synthesize speech stream: {e!s}"
        )


# Language Detection endpoints
@router.get("/language/supported", response_model=SupportedLanguagesResponse)
async def get_supported_languages():
    """获取支持的语言列表"""
    try:
        logger.info("Getting supported languages list")

        language_service = get_language_service()
        languages = language_service.get_supported_languages()

        supported_languages = [
            SupportedLanguage(
                code=lang["code"], name=lang["name"], native_name=lang["native_name"]
            )
            for lang in languages
        ]

        return SupportedLanguagesResponse(
            languages=supported_languages, total_count=len(supported_languages)
        )

    except Exception as e:
        logger.error(f"Failed to get supported languages: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get supported languages: {e!s}"
        )


@router.post("/language/detect", response_model=LanguageDetectResponse)
async def detect_language(request: LanguageDetectRequest):
    """检测单个文本的语言"""
    try:
        logger.info(f"Detecting language for text: {request.text[:50]}...")

        language_service = get_language_service()
        result = language_service.detect_language(
            text=request.text, with_confidence=request.with_confidence
        )

        language_result = LanguageResult(
            text=result["text"],
            language=result["language"],
            language_name=result["language_name"],
            confidence=result.get("confidence"),
        )

        return LanguageDetectResponse(result=language_result)

    except ValueError as e:
        logger.error(f"Invalid input for language detection: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to detect language: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to detect language: {e!s}")


@router.post("/language/detect/batch", response_model=LanguageDetectBatchResponse)
async def detect_languages_batch(request: LanguageDetectBatchRequest):
    """批量检测多个文本的语言"""
    try:
        logger.info(f"Batch detecting languages for {len(request.texts)} texts")

        language_service = get_language_service()
        results = language_service.detect_languages_batch(
            texts=request.texts, with_confidence=request.with_confidence
        )

        language_results = [
            LanguageResult(
                text=result["text"],
                language=result["language"],
                language_name=result["language_name"],
                confidence=result.get("confidence"),
            )
            for result in results
        ]

        return LanguageDetectBatchResponse(
            results=language_results, total_count=len(language_results)
        )

    except ValueError as e:
        logger.error(f"Invalid input for batch language detection: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to detect languages in batch: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to detect languages in batch: {e!s}"
        )


@router.post("/language/detect/confidence", response_model=LanguageDetectResponse)
async def detect_language_with_confidence(request: LanguageDetectRequest):
    """检测文本语言并强制返回置信度信息"""
    try:
        logger.info(
            f"Detecting language with confidence for text: {request.text[:50]}..."
        )

        language_service = get_language_service()
        result = language_service.detect_language(
            text=request.text,
            with_confidence=True,  # 强制返回置信度
        )

        language_result = LanguageResult(
            text=result["text"],
            language=result["language"],
            language_name=result["language_name"],
            confidence=result.get("confidence", 0.0),
        )

        return LanguageDetectResponse(result=language_result)

    except ValueError as e:
        logger.error(f"Invalid input for language detection with confidence: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to detect language with confidence: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect language with confidence: {e!s}",
        )
