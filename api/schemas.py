from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# TTS相关模型
class TTSSynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="要转换为语音的文本")
    voice: str = Field(..., description="声音名称，如：zh-CN-XiaoxiaoNeural")
    rate: Optional[str] = Field(None, description="语速调整，如：+50%, -25%", pattern=r"^[+-]\d{1,3}%$")
    volume: Optional[str] = Field(None, description="音量调整，如：+0%, -50%", pattern=r"^[+-]\d{1,3}%$")  
    pitch: Optional[str] = Field(None, description="音调调整，如：+100Hz, -50Hz")


class TTSSynthesizeResponse(BaseModel):
    message: str
    audio_size: int = Field(..., description="音频文件大小（字节）")
    voice_used: str
    parameters: dict
    timestamp: datetime = Field(default_factory=datetime.now)


class TTSVoice(BaseModel):
    name: str = Field(..., description="声音的完整名称")
    short_name: str = Field(..., description="声音的简短名称")
    gender: str = Field(..., description="性别：Male/Female")
    locale: str = Field(..., description="语言地区代码，如：zh-CN")
    language: str = Field(..., description="语言代码，如：zh")
    display_name: str = Field(..., description="显示名称")
    local_name: str = Field(..., description="本地语言名称")


class TTSVoicesResponse(BaseModel):
    voices: List[TTSVoice]
    total_count: int
    timestamp: datetime = Field(default_factory=datetime.now)


class TTSVoiceSearchRequest(BaseModel):
    language: Optional[str] = Field(None, description="按语言筛选，如：zh, en")
    locale: Optional[str] = Field(None, description="按地区筛选，如：zh-CN, en-US")
    gender: Optional[str] = Field(None, description="按性别筛选：Male/Female")
    limit: Optional[int] = Field(10, ge=1, le=100, description="返回结果数量限制")


class TTSVoiceSearchResponse(BaseModel):
    voices: List[TTSVoice]
    total_count: int
    filtered_count: int
    filters_applied: dict
    timestamp: datetime = Field(default_factory=datetime.now)
