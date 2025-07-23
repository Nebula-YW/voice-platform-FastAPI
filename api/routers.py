from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import logging
import edge_tts
import io

from .schemas import (
    TTSSynthesizeRequest,
    TTSSynthesizeResponse,
    TTSVoice,
    TTSVoicesResponse,
    TTSVoiceSearchRequest,
    TTSVoiceSearchResponse,
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
        
        voices_manager = await edge_tts.VoicesManager.create()
        all_voices = voices_manager.voices
        
        tts_voices = []
        for voice in all_voices:
            tts_voice = TTSVoice(
                name=voice.get('Name', ''),
                short_name=voice.get('ShortName', ''),
                gender=voice.get('Gender', ''),
                locale=voice.get('Locale', ''),
                language=voice.get('Language', voice.get('Locale', '').split('-')[0] if voice.get('Locale') else ''),
                display_name=voice.get('FriendlyName', ''),
                local_name=voice.get('FriendlyName', '')
            )
            tts_voices.append(tts_voice)
        
        return TTSVoicesResponse(
            voices=tts_voices,
            total_count=len(tts_voices)
        )
        
    except Exception as e:
        logger.error(f"Failed to get TTS voices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get TTS voices: {str(e)}")


@router.post("/tts/voices/search", response_model=TTSVoiceSearchResponse)
async def search_tts_voices(search_request: TTSVoiceSearchRequest):
    """按条件搜索TTS声音"""
    try:
        logger.info(f"Searching TTS voices with filters: {search_request.model_dump(exclude_none=True)}")
        
        voices_manager = await edge_tts.VoicesManager.create()
        
        # 构建搜索参数
        search_params = {}
        if search_request.language:
            search_params['Language'] = search_request.language
        if search_request.locale:
            search_params['Locale'] = search_request.locale
        if search_request.gender:
            search_params['Gender'] = search_request.gender
            
        # 执行搜索
        if search_params:
            filtered_voices = voices_manager.find(**search_params)
        else:
            filtered_voices = voices_manager.voices
            
        # 应用数量限制
        if search_request.limit:
            filtered_voices = filtered_voices[:search_request.limit]
        
        tts_voices = []
        for voice in filtered_voices:
            tts_voice = TTSVoice(
                name=voice.get('Name', ''),
                short_name=voice.get('ShortName', ''),
                gender=voice.get('Gender', ''),
                locale=voice.get('Locale', ''),
                language=voice.get('Language', voice.get('Locale', '').split('-')[0] if voice.get('Locale') else ''),
                display_name=voice.get('FriendlyName', ''),
                local_name=voice.get('FriendlyName', '')
            )
            tts_voices.append(tts_voice)
        
        return TTSVoiceSearchResponse(
            voices=tts_voices,
            total_count=len(voices_manager.voices),
            filtered_count=len(tts_voices),
            filters_applied=search_params
        )
        
    except Exception as e:
        logger.error(f"Failed to search TTS voices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search TTS voices: {str(e)}")


@router.post("/tts/synthesize", response_model=TTSSynthesizeResponse)
async def synthesize_speech_file(request: TTSSynthesizeRequest):
    """将文本转换为语音并返回音频流"""
    try:
        logger.info(f"Synthesizing speech for text: {request.text[:50]}... with voice: {request.voice}")
        
        # 验证声音是否存在
        voices_manager = await edge_tts.VoicesManager.create()
        available_voices = [voice['Name'] for voice in voices_manager.voices]
        
        if request.voice not in available_voices:
            raise HTTPException(
                status_code=400, 
                detail=f"Voice '{request.voice}' not found. Use /tts/voices to get available voices."
            )
        
        # 创建Communicate对象
        communicate_kwargs = {
            'text': request.text,
            'voice': request.voice
        }
        if request.rate:
            communicate_kwargs['rate'] = request.rate
        if request.volume:
            communicate_kwargs['volume'] = request.volume
        if request.pitch:
            communicate_kwargs['pitch'] = request.pitch
            
        communicate = edge_tts.Communicate(**communicate_kwargs)
        
        # 收集音频数据
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        if not audio_data:
            raise HTTPException(status_code=500, detail="Failed to generate audio data")
        
        # 返回参数信息
        parameters = {
            "text_length": len(request.text),
            "voice": request.voice,
            "rate": request.rate,
            "volume": request.volume,  
            "pitch": request.pitch
        }
        
        return TTSSynthesizeResponse(
            message="Speech synthesis completed successfully",
            audio_size=len(audio_data),
            voice_used=request.voice,
            parameters=parameters
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to synthesize speech: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to synthesize speech: {str(e)}")


@router.post("/tts/synthesize/stream")
async def synthesize_speech_stream(request: TTSSynthesizeRequest):
    """将文本转换为语音并返回音频流"""
    try:
        logger.info(f"Streaming speech synthesis for text: {request.text[:50]}... with voice: {request.voice}")
        
        # 验证声音是否存在
        voices_manager = await edge_tts.VoicesManager.create()
        available_voices = [voice['Name'] for voice in voices_manager.voices]
        
        if request.voice not in available_voices:
            raise HTTPException(
                status_code=400, 
                detail=f"Voice '{request.voice}' not found. Use /tts/voices to get available voices."
            )
        
        # 创建Communicate对象
        communicate_kwargs = {
            'text': request.text,
            'voice': request.voice
        }
        if request.rate:
            communicate_kwargs['rate'] = request.rate
        if request.volume:
            communicate_kwargs['volume'] = request.volume
        if request.pitch:
            communicate_kwargs['pitch'] = request.pitch
            
        communicate = edge_tts.Communicate(**communicate_kwargs)
        
        # 收集音频数据
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        if not audio_data:
            raise HTTPException(status_code=500, detail="Failed to generate audio data")
        
        # 创建音频流
        audio_stream = io.BytesIO(audio_data)
        
        # 返回流式响应
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "Content-Length": str(len(audio_data))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to synthesize speech stream: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to synthesize speech stream: {str(e)}")
