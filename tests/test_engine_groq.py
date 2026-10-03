from __future__ import annotations

import os

import httpx
import pytest
import respx

from dictate.core.engines.groq import GroqEngine


class TestGroqMocked:
    def setup_method(self) -> None:
        self.engine = GroqEngine(api_key="test-key")

    @respx.mock
    def test_transcribe_sends_correct_request(self, wav_bytes: bytes) -> None:
        route = respx.post(
            "https://api.groq.com/openai/v1/audio/transcriptions"
        ).mock(return_value=httpx.Response(200, json={"text": "hello world"}))
        self.engine.transcribe(wav_bytes, vocab=[])
        assert route.called
        request = route.calls[0].request
        assert request.headers["authorization"] == "Bearer test-key"
        assert b"whisper-large-v3-turbo" in request.content

    @respx.mock
    def test_transcribe_returns_transcript(self, wav_bytes: bytes) -> None:
        respx.post("https://api.groq.com/openai/v1/audio/transcriptions").mock(
            return_value=httpx.Response(200, json={"text": "the quick brown fox"})
        )
        result = self.engine.transcribe(wav_bytes, vocab=[])
        assert result.text == "the quick brown fox"
        assert result.engine == "groq"
        assert result.latency_ms >= 0

    @respx.mock
    def test_transcribe_sends_prompt_from_vocab(self, wav_bytes: bytes) -> None:
        route = respx.post(
            "https://api.groq.com/openai/v1/audio/transcriptions"
        ).mock(return_value=httpx.Response(200, json={"text": "hello"}))
        self.engine.transcribe(wav_bytes, vocab=["Kubernetes", "FastAPI"])
        request = route.calls[0].request
        assert b"Kubernetes" in request.content

    @respx.mock
    def test_name(self) -> None:
        assert self.engine.name == "groq"


@pytest.mark.live
def test_groq_live(wav_bytes: bytes) -> None:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        pytest.skip("GROQ_API_KEY not set")
    engine = GroqEngine(api_key=api_key)
    result = engine.transcribe(wav_bytes, vocab=[])
    assert isinstance(result.text, str)
    assert result.engine == "groq"
    assert result.latency_ms >= 0
