from __future__ import annotations

import time

import httpx

from dictate.core.types import Transcript

API_URL = "https://api.deepgram.com/v1/listen"


class DeepgramEngine:
    name: str = "deepgram"

    def __init__(self, *, api_key: str) -> None:
        self._api_key = api_key

    @property
    def config(self) -> dict[str, str]:
        return {"model": "nova-3", "api_url": API_URL, "smart_format": "true"}

    def transcribe(self, audio: bytes, *, vocab: list[str]) -> Transcript:
        params: list[tuple[str, str]] = [
            ("model", "nova-3"),
            ("smart_format", "true"),
        ]
        for term in vocab:
            params.append(("keyterm", term))

        t0 = time.monotonic()
        resp = httpx.post(
            API_URL,
            params=params,
            headers={
                "Authorization": f"Token {self._api_key}",
                "Content-Type": "audio/wav",
            },
            content=audio,
            timeout=60,
        )
        latency_ms = int((time.monotonic() - t0) * 1000)
        resp.raise_for_status()

        data = resp.json()
        text = data["results"]["channels"][0]["alternatives"][0]["transcript"]

        return Transcript(text=text, engine=self.name, latency_ms=latency_ms)
