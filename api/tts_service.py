import logging
from dataclasses import dataclass

import edge_tts

from .schemas import TTSVoice

logger = logging.getLogger(__name__)


class VoiceNotFoundError(ValueError):
    """Requested TTS voice is not available."""


@dataclass(frozen=True)
class SynthesizedSpeech:
    audio: bytes
    voice: str
    text_length: int
    rate: str | None
    volume: str | None
    pitch: str | None


def voice_from_edge(voice: dict) -> TTSVoice:
    locale = voice.get("Locale", "")
    language = voice.get("Language") or (locale.split("-")[0] if locale else "")
    display_name = voice.get("FriendlyName", "")
    return TTSVoice(
        name=voice.get("Name", ""),
        short_name=voice.get("ShortName", ""),
        gender=voice.get("Gender", ""),
        locale=locale,
        language=language,
        display_name=display_name,
        local_name=display_name,
    )


async def list_edge_voices() -> list[dict]:
    voices_manager = await edge_tts.VoicesManager.create()
    return list(voices_manager.voices)


async def list_voices() -> list[TTSVoice]:
    return [voice_from_edge(voice) for voice in await list_edge_voices()]


async def search_voices(
    *,
    language: str | None = None,
    locale: str | None = None,
    gender: str | None = None,
    limit: int | None = 10,
) -> tuple[list[TTSVoice], int, dict]:
    voices_manager = await edge_tts.VoicesManager.create()
    search_params: dict[str, str] = {}
    if language:
        search_params["Language"] = language
    if locale:
        search_params["Locale"] = locale
    if gender:
        search_params["Gender"] = gender

    filtered = (
        voices_manager.find(**search_params) if search_params else voices_manager.voices
    )
    if limit:
        filtered = filtered[:limit]

    return (
        [voice_from_edge(voice) for voice in filtered],
        len(voices_manager.voices),
        search_params,
    )


async def resolve_voice(requested: str) -> dict:
    for voice in await list_edge_voices():
        if requested in {voice.get("ShortName"), voice.get("Name")}:
            return voice
    raise VoiceNotFoundError(
        f"Voice '{requested}' not found. Use search_voices to list available voices."
    )


async def synthesize_speech(
    *,
    text: str,
    voice: str,
    rate: str | None = None,
    volume: str | None = None,
    pitch: str | None = None,
) -> SynthesizedSpeech:
    resolved = await resolve_voice(voice)
    short_name = resolved.get("ShortName") or voice
    communicate_kwargs = {"text": text, "voice": short_name}
    if rate:
        communicate_kwargs["rate"] = rate
    if volume:
        communicate_kwargs["volume"] = volume
    if pitch:
        communicate_kwargs["pitch"] = pitch

    logger.info("Synthesizing speech with voice %s", short_name)
    communicate = edge_tts.Communicate(**communicate_kwargs)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]

    if not audio_data:
        raise RuntimeError("Failed to generate audio data")

    return SynthesizedSpeech(
        audio=audio_data,
        voice=short_name,
        text_length=len(text),
        rate=rate,
        volume=volume,
        pitch=pitch,
    )
