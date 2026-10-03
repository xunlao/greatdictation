from __future__ import annotations

import os

import httpx
import pytest
import respx

from dictate.core.engines.openai_whisper import OpenAIWhisperEngine


class TestOpenAIWhisperMocked:
    def setup_method(self) -> None:
        self.engine = OpenAIWhisperEngine(api_key="test-key")

    @respx.mock
    def test_transcribe_sends_correct_request(self, wav_bytes: bytes) -> None:
        route = respx.post("https://api.openai.com/v1/audio/transcriptions").mock(
            return_value=httpx.Response(200, json={"text": "hello world"})
        )
        self.engine.transcribe(wav_bytes, vocab=[])
        assert route.called
        request = route.calls[0].request
        assert request.headers["authorization"] == "Bearer test-key"
        assert b"whisper-1" in request.content

    @respx.mock
    def test_transcribe_returns_transcript(self, wav_bytes: bytes) -> None:
        respx.post("https://api.openai.com/v1/audio/transcriptions").mock(
            return_value=httpx.Response(200, json={"text": "the quick brown fox"})
        )
        result = self.engine.transcribe(wav_bytes, vocab=[])
        assert result.text == "the quick brown fox"
        assert result.engine == "openai-whisper"
        assert result.latency_ms >= 0

    @respx.mock
    def test_transcribe_sends_prompt_from_vocab(self, wav_bytes: bytes) -> None:
        route = respx.post("https://api.openai.com/v1/audio/transcriptions").mock(
            return_value=httpx.Response(200, json={"text": "hello"})
        )
        self.engine.transcribe(wav_bytes, vocab=["pytest", "ruff"])
        request = route.calls[0].request
        assert b"pytest" in request.content

    @respx.mock
    def test_name(self) -> None:
        assert self.engine.name == "openai-whisper"


@pytest.mark.live
def test_openai_whisper_live(wav_bytes: bytes) -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")
    engine = OpenAIWhisperEngine(api_key=api_key)
    result = engine.transcribe(wav_bytes, vocab=[])
    assert isinstance(result.text, str)
    assert result.engine == "openai-whisper"
    assert result.latency_ms >= 0
