from __future__ import annotations

from click.testing import CliRunner

from dictate.cli import main


def test_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Personal push-to-talk dictation tool" in result.output


def test_version() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_transcribe_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["transcribe", "--help"])
    assert result.exit_code == 0
    assert "--engine" in result.output
    assert "openai-whisper" in result.output
    assert "deepgram" in result.output


def test_transcribe_missing_key(tmp_path) -> None:  # type: ignore[no-untyped-def]
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"fake")
    runner = CliRunner(env={"OPENAI_API_KEY": ""})
    result = runner.invoke(main, ["transcribe", str(wav)])
    assert result.exit_code != 0
    assert "OPENAI_API_KEY" in result.output


def test_eval_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["eval", "--help"])
    assert result.exit_code == 0
