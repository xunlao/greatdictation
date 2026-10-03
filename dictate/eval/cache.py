from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from dictate.core.types import Transcript


class EvalCache:
    def __init__(self, cache_dir: Path) -> None:
        self._dir = cache_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def _key_path(self, clip_id: str, engine: str, *, cleanup: bool) -> Path:
        suffix = "cleanup" if cleanup else "raw"
        return self._dir / f"{clip_id}_{engine}_{suffix}.json"

    def get(self, clip_id: str, engine: str, *, cleanup: bool) -> Transcript | None:
        path = self._key_path(clip_id, engine, cleanup=cleanup)
        if not path.exists():
            return None
        from dictate.core.types import Transcript as _Transcript

        data = json.loads(path.read_text())
        return _Transcript(
            text=data["text"], engine=data["engine"], latency_ms=data["latency_ms"]
        )

    def put(
        self, clip_id: str, engine: str, *, cleanup: bool, transcript: Transcript
    ) -> None:
        path = self._key_path(clip_id, engine, cleanup=cleanup)
        data = {
            "text": transcript.text,
            "engine": transcript.engine,
            "latency_ms": transcript.latency_ms,
        }
        path.write_text(json.dumps(data, indent=2))
