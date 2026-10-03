from __future__ import annotations

import struct
import wave
from dataclasses import dataclass
from io import BytesIO
from typing import TYPE_CHECKING

from dictate.core.types import Transcript
from dictate.eval.harness import EvalResult, load_clips, run_eval

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class StubEngine:
    name: str = "stub"

    @property
    def config(self) -> dict[str, str]:
        return {"model": "stub-v1"}

    def transcribe(self, audio: bytes, *, vocab: list[str]) -> Transcript:
        return Transcript(text="the quick brown fox", engine=self.name, latency_ms=42)


def _make_wav(path: Path) -> None:
    buf = BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(struct.pack("<" + "h" * 1600, *([0] * 1600)))
    path.write_bytes(buf.getvalue())


def _setup_eval_data(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    _make_wav(data_dir / "clip01.wav")
    (data_dir / "clip01.txt").write_text("the quick brown fox\n")
    _make_wav(data_dir / "clip02.wav")
    (data_dir / "clip02.txt").write_text("hello world\n")


def test_load_clips(tmp_path) -> None:  # type: ignore[no-untyped-def]
    _setup_eval_data(tmp_path / "data")
    clips = load_clips(tmp_path / "data")
    assert len(clips) == 2
    ids = {c.clip_id for c in clips}
    assert ids == {"clip01", "clip02"}
    for clip in clips:
        assert clip.reference_text.strip()
        assert len(clip.audio) > 0


def test_run_eval_produces_results(tmp_path) -> None:  # type: ignore[no-untyped-def]
    _setup_eval_data(tmp_path / "data")
    clips = load_clips(tmp_path / "data")
    engine = StubEngine()

    results = run_eval(
        clips=clips,
        engine=engine,
        vocab=[],
        cache_dir=tmp_path / "cache",
        cleanup=False,
    )
    assert len(results) == 2
    for r in results:
        assert isinstance(r, EvalResult)
        assert r.engine == "stub"
        assert r.wer >= 0.0
        assert r.latency_ms == 42


def test_run_eval_uses_cache(tmp_path) -> None:  # type: ignore[no-untyped-def]
    _setup_eval_data(tmp_path / "data")
    clips = load_clips(tmp_path / "data")

    call_count = 0

    @dataclass
    class CountingEngine:
        name: str = "counting"

        @property
        def config(self) -> dict[str, str]:
            return {"model": "counting-v1"}

        def transcribe(self, audio: bytes, *, vocab: list[str]) -> Transcript:
            nonlocal call_count
            call_count += 1
            return Transcript(text="the quick brown fox", engine=self.name, latency_ms=10)

    engine = CountingEngine()
    cache_dir = tmp_path / "cache"

    run_eval(clips=clips, engine=engine, vocab=[], cache_dir=cache_dir, cleanup=False)
    assert call_count == 2

    call_count = 0
    run_eval(clips=clips, engine=engine, vocab=[], cache_dir=cache_dir, cleanup=False)
    assert call_count == 0


def test_run_eval_wer_correct_for_perfect_match(tmp_path) -> None:  # type: ignore[no-untyped-def]
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _make_wav(data_dir / "clip01.wav")
    (data_dir / "clip01.txt").write_text("the quick brown fox\n")
    clips = load_clips(data_dir)

    engine = StubEngine()
    results = run_eval(
        clips=clips, engine=engine, vocab=[], cache_dir=tmp_path / "cache", cleanup=False
    )
    assert results[0].wer == 0.0


def test_run_eval_wer_nonzero_for_mismatch(tmp_path) -> None:  # type: ignore[no-untyped-def]
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _make_wav(data_dir / "clip01.wav")
    (data_dir / "clip01.txt").write_text("something completely different\n")
    clips = load_clips(data_dir)

    engine = StubEngine()
    results = run_eval(
        clips=clips, engine=engine, vocab=[], cache_dir=tmp_path / "cache", cleanup=False
    )
    assert results[0].wer > 0.0


def test_vocab_change_causes_cache_miss(tmp_path) -> None:  # type: ignore[no-untyped-def]
    _setup_eval_data(tmp_path / "data")
    clips = load_clips(tmp_path / "data")

    call_count = 0

    @dataclass
    class CountingEngine:
        name: str = "counting"

        @property
        def config(self) -> dict[str, str]:
            return {"model": "counting-v1"}

        def transcribe(self, audio: bytes, *, vocab: list[str]) -> Transcript:
            nonlocal call_count
            call_count += 1
            return Transcript(text="the quick brown fox", engine=self.name, latency_ms=10)

    engine = CountingEngine()
    cache_dir = tmp_path / "cache"

    run_eval(clips=clips, engine=engine, vocab=["fox"], cache_dir=cache_dir, cleanup=False)
    assert call_count == 2

    call_count = 0
    run_eval(clips=clips, engine=engine, vocab=["fox"], cache_dir=cache_dir, cleanup=False)
    assert call_count == 0  # same vocab → cache hit

    call_count = 0
    run_eval(
        clips=clips, engine=engine, vocab=["fox", "brown"], cache_dir=cache_dir, cleanup=False
    )
    assert call_count == 2  # different vocab → cache miss


def test_run_eval_with_cleanup_fn(tmp_path) -> None:  # type: ignore[no-untyped-def]
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _make_wav(data_dir / "clip01.wav")
    (data_dir / "clip01.txt").write_text("The quick brown fox.\n")
    clips = load_clips(data_dir)

    engine = StubEngine()

    def fake_cleanup(text: str) -> str:
        return "The quick brown fox."

    results = run_eval(
        clips=clips,
        engine=engine,
        vocab=[],
        cache_dir=tmp_path / "cache",
        cleanup=True,
        cleanup_config={"model": "gpt-4.1-mini", "api_url": "https://api.openai.com/v1/chat/completions"},
        cleanup_fn=fake_cleanup,
    )
    assert len(results) == 1
    assert results[0].cleanup is True
    assert results[0].hypothesis == "The quick brown fox."
    assert results[0].wer == 0.0


def test_run_eval_cleanup_uses_different_cache(tmp_path) -> None:  # type: ignore[no-untyped-def]
    _setup_eval_data(tmp_path / "data")
    clips = load_clips(tmp_path / "data")

    call_count = 0

    @dataclass
    class CountingEngine:
        name: str = "counting"

        @property
        def config(self) -> dict[str, str]:
            return {"model": "counting-v1"}

        def transcribe(self, audio: bytes, *, vocab: list[str]) -> Transcript:
            nonlocal call_count
            call_count += 1
            return Transcript(text="the quick brown fox", engine=self.name, latency_ms=10)

    engine = CountingEngine()
    cache_dir = tmp_path / "cache"

    run_eval(clips=clips, engine=engine, vocab=[], cache_dir=cache_dir, cleanup=False)
    assert call_count == 2

    call_count = 0
    run_eval(
        clips=clips,
        engine=engine,
        vocab=[],
        cache_dir=cache_dir,
        cleanup=True,
        cleanup_config={"model": "gpt-4.1-mini"},
        cleanup_fn=lambda t: t.capitalize(),
    )
    assert call_count == 2  # different fingerprint → cache miss
