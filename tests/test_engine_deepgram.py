from __future__ import annotations

import os

import httpx
import pytest
import respx

from dictate.core.engines.deepgram import DeepgramEngine

SAMPLE_RESPONSE = {
    "results": {
        "channels": [
            {
                "alternatives": [
                    {"transcript": "the quick brown fox"}
                ]
            }
        ]
    }
}


class TestDeepgramMocked:
    def setup_method(self) -> None:
        self.engine = DeepgramEngine(api_key="test-key")

    @respx.mock
    def test_transcribe_sends_correct_request(self, wav_bytes: bytes) -> None:
        route = respx.post(url__startswith="https://api.deepgram.com/v1/listen").mock(
            return_value=httpx.Response(200, json=SAMPLE_RESPONSE)
        )
        self.engine.transcribe(wav_bytes, vocab=[])
        assert route.called
        request = route.calls[0].request
        assert request.headers["authorization"] == "Token test-key"
        assert "model=nova-3" in str(request.url)

    @respx.mock
    def test_transcribe_returns_transcript(self, wav_bytes: bytes) -> None:
        respx.post(url__startswith="https://api.deepgram.com/v1/listen").mock(
            return_value=httpx.Response(200, json=SAMPLE_RESPONSE)
        )
        result = self.engine.transcribe(wav_bytes, vocab=[])
        assert result.text == "the quick brown fox"
        assert result.engine == "deepgram"
        assert result.latency_ms >= 0

    @respx.mock
    def test_transcribe_sends_keyterms(self, wav_bytes: bytes) -> None:
        route = respx.post(url__startswith="https://api.deepgram.com/v1/listen").mock(
            return_value=httpx.Response(200, json=SAMPLE_RESPONSE)
        )
        self.engine.transcribe(wav_bytes, vocab=["pytest", "ruff"])
        url = str(route.calls[0].request.url)
        assert "keyterm=pytest" in url
        assert "keyterm=ruff" in url

    @respx.mock
    def test_transcribe_smart_format_enabled(self, wav_bytes: bytes) -> None:
        route = respx.post(url__startswith="https://api.deepgram.com/v1/listen").mock(
            return_value=httpx.Response(200, json=SAMPLE_RESPONSE)
        )
        self.engine.transcribe(wav_bytes, vocab=[])
        url = str(route.calls[0].request.url)
        assert "smart_format=true" in url

    @respx.mock
    def test_name(self) -> None:
        assert self.engine.name == "deepgram"


@pytest.mark.live
def test_deepgram_live(wav_bytes: bytes) -> None:
    api_key = os.environ.get("DEEPGRAM_API_KEY")
    if not api_key:
        pytest.skip("DEEPGRAM_API_KEY not set")
    engine = DeepgramEngine(api_key=api_key)
    result = engine.transcribe(wav_bytes, vocab=[])
    assert isinstance(result.text, str)
    assert result.engine == "deepgram"
    assert result.latency_ms >= 0
