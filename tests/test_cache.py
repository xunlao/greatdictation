from __future__ import annotations

from dictate.core.types import Transcript
from dictate.eval.cache import EvalCache, config_fingerprint


def test_config_fingerprint_deterministic() -> None:
    fp1 = config_fingerprint(engine_config={"model": "x"}, vocab=["a"], cleanup=False)
    fp2 = config_fingerprint(engine_config={"model": "x"}, vocab=["a"], cleanup=False)
    assert fp1 == fp2


def test_config_fingerprint_differs_on_vocab() -> None:
    fp1 = config_fingerprint(engine_config={"model": "x"}, vocab=["a"], cleanup=False)
    fp2 = config_fingerprint(engine_config={"model": "x"}, vocab=["a", "b"], cleanup=False)
    assert fp1 != fp2


def test_config_fingerprint_differs_on_engine_config() -> None:
    fp1 = config_fingerprint(engine_config={"model": "whisper-1"}, vocab=[], cleanup=False)
    fp2 = config_fingerprint(engine_config={"model": "gpt-transcribe"}, vocab=[], cleanup=False)
    assert fp1 != fp2


def test_config_fingerprint_differs_on_cleanup() -> None:
    fp1 = config_fingerprint(engine_config={"model": "x"}, vocab=[], cleanup=False)
    fp2 = config_fingerprint(engine_config={"model": "x"}, vocab=[], cleanup=True)
    assert fp1 != fp2


def test_config_fingerprint_differs_on_cleanup_config() -> None:
    fp1 = config_fingerprint(
        engine_config={"model": "x"}, vocab=[], cleanup=True, cleanup_config={"model": "a"}
    )
    fp2 = config_fingerprint(
        engine_config={"model": "x"}, vocab=[], cleanup=True, cleanup_config={"model": "b"}
    )
    assert fp1 != fp2


def test_config_fingerprint_vocab_order_independent() -> None:
    fp1 = config_fingerprint(engine_config={}, vocab=["b", "a"], cleanup=False)
    fp2 = config_fingerprint(engine_config={}, vocab=["a", "b"], cleanup=False)
    assert fp1 == fp2


def test_cache_miss(tmp_path) -> None:  # type: ignore[no-untyped-def]
    cache = EvalCache(cache_dir=tmp_path)
    result = cache.get("clip01", "openai-whisper", "abc123")
    assert result is None


def test_cache_roundtrip(tmp_path) -> None:  # type: ignore[no-untyped-def]
    cache = EvalCache(cache_dir=tmp_path)
    fp = config_fingerprint(engine_config={"model": "whisper-1"}, vocab=[], cleanup=False)
    transcript = Transcript(text="hello world", engine="openai-whisper", latency_ms=150)
    cache.put("clip01", "openai-whisper", fp, transcript=transcript)

    result = cache.get("clip01", "openai-whisper", fp)
    assert result is not None
    assert result.text == "hello world"
    assert result.engine == "openai-whisper"
    assert result.latency_ms == 150


def test_cache_different_fingerprints(tmp_path) -> None:  # type: ignore[no-untyped-def]
    cache = EvalCache(cache_dir=tmp_path)
    fp1 = config_fingerprint(engine_config={"model": "x"}, vocab=[], cleanup=False)
    fp2 = config_fingerprint(engine_config={"model": "x"}, vocab=[], cleanup=True)
    transcript = Transcript(text="hello", engine="deepgram", latency_ms=100)
    cache.put("clip01", "deepgram", fp1, transcript=transcript)

    assert cache.get("clip01", "deepgram", fp2) is None
    assert cache.get("clip01", "deepgram", fp1) is not None


def test_cache_different_engines(tmp_path) -> None:  # type: ignore[no-untyped-def]
    cache = EvalCache(cache_dir=tmp_path)
    fp = config_fingerprint(engine_config={}, vocab=[], cleanup=False)
    t1 = Transcript(text="from whisper", engine="openai-whisper", latency_ms=200)
    t2 = Transcript(text="from deepgram", engine="deepgram", latency_ms=100)
    cache.put("clip01", "openai-whisper", fp, transcript=t1)
    cache.put("clip01", "deepgram", fp, transcript=t2)

    r1 = cache.get("clip01", "openai-whisper", fp)
    r2 = cache.get("clip01", "deepgram", fp)
    assert r1 is not None and r1.text == "from whisper"
    assert r2 is not None and r2.text == "from deepgram"
