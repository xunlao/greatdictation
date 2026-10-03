from __future__ import annotations

from typing import TYPE_CHECKING

from dictate.core.engines.deepgram import DeepgramEngine
from dictate.core.engines.groq import GroqEngine
from dictate.core.engines.openai_transcribe import OpenAITranscribeEngine
from dictate.core.engines.openai_whisper import OpenAIWhisperEngine

if TYPE_CHECKING:
    from dictate.core.types import Engine


ENGINE_KEYS: dict[str, str] = {
    "openai-whisper": "OPENAI_API_KEY",
    "openai-transcribe": "OPENAI_API_KEY",
    "deepgram": "DEEPGRAM_API_KEY",
    "groq": "GROQ_API_KEY",
    "parakeet": "",
}

AVAILABLE_ENGINES = list(ENGINE_KEYS)


def get_engine(name: str, *, api_key: str = "") -> Engine:
    match name:
        case "openai-whisper":
            return OpenAIWhisperEngine(api_key=api_key)
        case "openai-transcribe":
            return OpenAITranscribeEngine(api_key=api_key)
        case "deepgram":
            return DeepgramEngine(api_key=api_key)
        case "groq":
            return GroqEngine(api_key=api_key)
        case "parakeet":
            from dictate.core.engines.parakeet import ParakeetEngine

            return ParakeetEngine()
        case _:
            raise ValueError(f"Unknown engine: {name!r}. Available: {AVAILABLE_ENGINES}")
