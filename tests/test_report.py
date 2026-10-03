from __future__ import annotations

from dictate.eval.harness import EvalResult
from dictate.eval.report import format_report, save_report


def _make_results(engine: str, cleanup: bool) -> list[EvalResult]:
    return [
        EvalResult(
            clip_id="clip01",
            engine=engine,
            cleanup=cleanup,
            hypothesis="the quick brown fox",
            reference="the quick brown fox",
            wer=0.0,
            vocab_acc=1.0,
            latency_ms=100,
        ),
        EvalResult(
            clip_id="clip02",
            engine=engine,
            cleanup=cleanup,
            hypothesis="hello world",
            reference="hello world",
            wer=0.0,
            vocab_acc=1.0,
            latency_ms=200,
        ),
    ]


def test_format_report_has_table() -> None:
    results = {"openai-whisper_raw": _make_results("openai-whisper", False)}
    report = format_report(results)
    assert "| openai-whisper |" in report
    assert "| Engine |" in report
    assert "0.00%" in report


def test_format_report_multiple_engines() -> None:
    results = {
        "openai-whisper_raw": _make_results("openai-whisper", False),
        "deepgram_raw": _make_results("deepgram", False),
    }
    report = format_report(results)
    assert "openai-whisper" in report
    assert "deepgram" in report


def test_save_report(tmp_path) -> None:  # type: ignore[no-untyped-def]
    report = "# Test Report\n\nSome content"
    path = save_report(report, tmp_path / "results")
    assert path.exists()
    assert path.read_text() == report
    assert path.suffix == ".md"
