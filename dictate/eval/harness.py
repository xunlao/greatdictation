from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from dictate.eval.cache import EvalCache, config_fingerprint
from dictate.eval.scorer import vocab_accuracy, word_error_rate

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from dictate.core.types import Engine


@dataclass(frozen=True)
class Clip:
    clip_id: str
    audio: bytes
    reference_text: str


@dataclass(frozen=True)
class EvalResult:
    clip_id: str
    engine: str
    cleanup: bool
    hypothesis: str
    reference: str
    wer: float
    vocab_acc: float
    latency_ms: int


def load_clips(data_dir: Path) -> list[Clip]:
    clips: list[Clip] = []
    for wav_path in sorted(data_dir.glob("*.wav")):
        clip_id = wav_path.stem
        txt_path = wav_path.with_suffix(".txt")
        if not txt_path.exists():
            continue
        clips.append(
            Clip(
                clip_id=clip_id,
                audio=wav_path.read_bytes(),
                reference_text=txt_path.read_text().strip(),
            )
        )
    return clips


def run_eval(
    *,
    clips: list[Clip],
    engine: Engine,
    vocab: list[str],
    cache_dir: Path,
    cleanup: bool,
    cleanup_config: dict[str, str] | None = None,
    cleanup_fn: Callable[[str], str] | None = None,
) -> list[EvalResult]:
    engine_config: dict[str, str] = getattr(engine, "config", {})
    fp = config_fingerprint(
        engine_config=engine_config,
        vocab=vocab,
        cleanup=cleanup,
        cleanup_config=cleanup_config,
    )

    cache = EvalCache(cache_dir)
    results: list[EvalResult] = []

    for clip in clips:
        cached = cache.get(clip.clip_id, engine.name, fp)
        if cached is not None:
            transcript = cached
        else:
            transcript = engine.transcribe(clip.audio, vocab=vocab)
            if cleanup and cleanup_fn is not None:
                from dictate.core.types import Transcript

                cleaned_text = cleanup_fn(transcript.text)
                transcript = Transcript(
                    text=cleaned_text,
                    engine=transcript.engine,
                    latency_ms=transcript.latency_ms,
                )
            cache.put(clip.clip_id, engine.name, fp, transcript=transcript)

        wer = word_error_rate(clip.reference_text, transcript.text)
        vacc = vocab_accuracy(clip.reference_text, transcript.text, vocab=vocab)

        results.append(
            EvalResult(
                clip_id=clip.clip_id,
                engine=engine.name,
                cleanup=cleanup,
                hypothesis=transcript.text,
                reference=clip.reference_text,
                wer=wer,
                vocab_acc=vacc,
                latency_ms=transcript.latency_ms,
            )
        )

    return results
