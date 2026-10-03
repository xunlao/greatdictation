from __future__ import annotations

import tempfile
import time

import parakeet_mlx

from dictate.core.types import Transcript

DEFAULT_MODEL = "mlx-community/parakeet-tdt-0.6b-v3"


class ParakeetEngine:
    name: str = "parakeet"

    def __init__(self, *, model: str = DEFAULT_MODEL) -> None:
        self._model_id = model
        self._model: object | None = None

    def _get_model(self) -> object:
        if self._model is None:
            self._model = parakeet_mlx.from_pretrained(self._model_id)
        return self._model

    def transcribe(self, audio: bytes, *, vocab: list[str]) -> Transcript:
        model = self._get_model()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            tmp.write(audio)
            tmp.flush()
            t0 = time.perf_counter()
            result = model.transcribe(tmp.name)
            latency_ms = int((time.perf_counter() - t0) * 1000)

        return Transcript(text=result.text, engine=self.name, latency_ms=latency_ms)
