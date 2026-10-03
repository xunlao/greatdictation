from __future__ import annotations

import statistics
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from dictate.eval.harness import EvalResult

COST_PER_AUDIO_MINUTE: dict[str, float] = {
    "openai-whisper": 0.006,
    "openai-transcribe": 0.006,
    "deepgram": 0.0043,
    "groq": 0.04 / 60,
}


def _percentile(values: list[int], pct: int) -> int:
    if not values:
        return 0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * pct / 100
    f = int(k)
    c = f + 1
    if c >= len(sorted_vals):
        return sorted_vals[f]
    return int(sorted_vals[f] + (k - f) * (sorted_vals[c] - sorted_vals[f]))


def format_report(
    results_by_engine: dict[str, list[EvalResult]],
) -> str:
    lines: list[str] = []
    lines.append("# Eval Results")
    lines.append("")
    lines.append(
        "| Engine | Cleanup | WER | Vocab Acc | "
        "Latency p50 (ms) | Latency p90 (ms) | $/min |"
    )
    lines.append("|--------|---------|-----|-----------|"
                 "-----------------|-----------------|-------|")

    for _key, results in sorted(results_by_engine.items()):
        if not results:
            continue
        engine = results[0].engine
        cleanup = results[0].cleanup
        avg_wer = statistics.mean(r.wer for r in results)
        avg_vacc = statistics.mean(r.vocab_acc for r in results)
        latencies = [r.latency_ms for r in results]
        p50 = _percentile(latencies, 50)
        p90 = _percentile(latencies, 90)
        cost = COST_PER_AUDIO_MINUTE.get(engine, 0.0)
        cleanup_str = "yes" if cleanup else "no"

        lines.append(
            f"| {engine} | {cleanup_str} | {avg_wer:.2%} | {avg_vacc:.2%} | "
            f"{p50} | {p90} | ${cost:.4f} |"
        )

    lines.append("")
    return "\n".join(lines)


def save_report(report: str, results_dir: Path) -> Path:
    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / f"{date.today().isoformat()}.md"
    path.write_text(report)
    return path
