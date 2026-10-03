from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from dictate.core.types import Transcript


def config_fingerprint(
    *,
    engine_config: dict[str, str],
    vocab: list[str],
    cleanup: bool,
    cleanup_config: dict[str, str] | None = None,
) -> str:
    blob = {
        "engine_config": engine_config,
        "vocab": sorted(vocab),
        "cleanup": cleanup,
        "cleanup_config": cleanup_config or {},
    }
    raw = json.dumps(blob, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()[:12]


class EvalCache:
    def __init__(self, cache_dir: Path) -> None:
        self._dir = cache_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def _key_path(self, clip_id: str, engine: str, fingerprint: str) -> Path:
        return self._dir / f"{clip_id}_{engine}_{fingerprint}.json"

    def get(self, clip_id: str, engine: str, fingerprint: str) -> Transcript | None:
        path = self._key_path(clip_id, engine, fingerprint)
        if not path.exists():
            return None
        from dictate.core.types import Transcript as _Transcript

        data = json.loads(path.read_text())
        return _Transcript(
            text=data["text"], engine=data["engine"], latency_ms=data["latency_ms"]
        )

    def put(
        self, clip_id: str, engine: str, fingerprint: str, *, transcript: Transcript
    ) -> None:
        path = self._key_path(clip_id, engine, fingerprint)
        data = {
            "text": transcript.text,
            "engine": transcript.engine,
            "latency_ms": transcript.latency_ms,
        }
        path.write_text(json.dumps(data, indent=2))
