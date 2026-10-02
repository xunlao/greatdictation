from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dictate.core.types import Engine, Transcript


def transcribe(audio: bytes, *, engine: Engine, vocab: list[str] | None = None) -> Transcript:
    return engine.transcribe(audio, vocab=vocab or [])
