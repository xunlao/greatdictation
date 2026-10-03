from __future__ import annotations

import time

import httpx

from dictate.core.types import Transcript

API_URL = "https://api.openai.com/v1/audio/transcriptions"
MODEL = "gpt-transcribe"


class OpenAITranscribeEngine:
    name: str = "openai-transcribe"

    def __init__(self, *, api_key: str) -> None:
        self._api_key = api_key

    def transcribe(self, audio: bytes, *, vocab: list[str]) -> Transcript:
        fields: dict[str, str] = {"model": MODEL}
        if vocab:
            fields["prompt"] = ", ".join(vocab)

        t0 = time.monotonic()
        resp = httpx.post(
            API_URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
            files={"file": ("audio.wav", audio, "audio/wav")},
            data=fields,
            timeout=60,
        )
        latency_ms = int((time.monotonic() - t0) * 1000)
        resp.raise_for_status()

        return Transcript(
            text=resp.json()["text"],
            engine=self.name,
            latency_ms=latency_ms,
        )
