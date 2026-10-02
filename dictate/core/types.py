from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Transcript:
    text: str
    engine: str
    latency_ms: int


class Engine(Protocol):
    name: str

    def transcribe(self, audio: bytes, *, vocab: list[str]) -> Transcript: ...
