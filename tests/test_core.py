from __future__ import annotations

from dataclasses import dataclass

from dictate.core import Engine, Transcript
from dictate.core.pipeline import transcribe


@dataclass
class FakeEngine:
    name: str = "fake"

    def transcribe(self, audio: bytes, *, vocab: list[str]) -> Transcript:
        return Transcript(text="hello world", engine=self.name, latency_ms=42)


def test_transcript_fields() -> None:
    t = Transcript(text="hello", engine="test", latency_ms=10)
    assert t.text == "hello"
    assert t.engine == "test"
    assert t.latency_ms == 10


def test_fake_engine_satisfies_protocol() -> None:
    engine: Engine = FakeEngine()
    result = engine.transcribe(b"audio", vocab=[])
    assert result.text == "hello world"


def test_pipeline_transcribe() -> None:
    engine = FakeEngine()
    result = transcribe(b"audio", engine=engine)
    assert result.text == "hello world"
    assert result.engine == "fake"
    assert result.latency_ms == 42


def test_pipeline_with_vocab() -> None:
    engine = FakeEngine()
    result = transcribe(b"audio", engine=engine, vocab=["pytest", "ruff"])
    assert result.text == "hello world"
