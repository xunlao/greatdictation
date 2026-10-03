from __future__ import annotations

from dictate.core.types import Transcript
from dictate.eval.cache import EvalCache


def test_cache_miss(tmp_path) -> None:  # type: ignore[no-untyped-def]
    cache = EvalCache(cache_dir=tmp_path)
    result = cache.get("clip01", "openai-whisper", cleanup=False)
    assert result is None


def test_cache_roundtrip(tmp_path) -> None:  # type: ignore[no-untyped-def]
    cache = EvalCache(cache_dir=tmp_path)
    transcript = Transcript(text="hello world", engine="openai-whisper", latency_ms=150)
    cache.put("clip01", "openai-whisper", cleanup=False, transcript=transcript)

    result = cache.get("clip01", "openai-whisper", cleanup=False)
    assert result is not None
    assert result.text == "hello world"
    assert result.engine == "openai-whisper"
    assert result.latency_ms == 150


def test_cache_different_cleanup_flag(tmp_path) -> None:  # type: ignore[no-untyped-def]
    cache = EvalCache(cache_dir=tmp_path)
    transcript = Transcript(text="hello", engine="deepgram", latency_ms=100)
    cache.put("clip01", "deepgram", cleanup=False, transcript=transcript)

    assert cache.get("clip01", "deepgram", cleanup=True) is None
    assert cache.get("clip01", "deepgram", cleanup=False) is not None


def test_cache_different_engines(tmp_path) -> None:  # type: ignore[no-untyped-def]
    cache = EvalCache(cache_dir=tmp_path)
    t1 = Transcript(text="from whisper", engine="openai-whisper", latency_ms=200)
    t2 = Transcript(text="from deepgram", engine="deepgram", latency_ms=100)
    cache.put("clip01", "openai-whisper", cleanup=False, transcript=t1)
    cache.put("clip01", "deepgram", cleanup=False, transcript=t2)

    r1 = cache.get("clip01", "openai-whisper", cleanup=False)
    r2 = cache.get("clip01", "deepgram", cleanup=False)
    assert r1 is not None and r1.text == "from whisper"
    assert r2 is not None and r2.text == "from deepgram"
