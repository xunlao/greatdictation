from __future__ import annotations

import io
import sys
import wave
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from pathlib import Path

import pytest
from click.testing import CliRunner

from dictate.cli import main


@pytest.fixture(autouse=True)
def _mock_sounddevice(monkeypatch: pytest.MonkeyPatch) -> None:
    sd = MagicMock()
    monkeypatch.setitem(sys.modules, "sounddevice", sd)


def test_clips_empty(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["clips", "--data-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No clips" in result.output


def test_clips_lists_pairs(tmp_path: Path) -> None:
    _write_wav(tmp_path / "greeting.wav")
    (tmp_path / "greeting.txt").write_text("Hello there.")

    _write_wav(tmp_path / "orphan.wav")

    runner = CliRunner()
    result = runner.invoke(main, ["clips", "--data-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "greeting" in result.output
    assert "orphan" not in result.output


def test_record_clip_creates_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sd = sys.modules["sounddevice"]
    sd.rec.return_value = _fake_array(16000 * 2)

    monkeypatch.delitem(sys.modules, "dictate.desktop.recorder", raising=False)

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["record-clip", "--data-dir", str(tmp_path), "--name", "test-clip", "--duration", "2"],
        input="This is my reference text.\n",
    )
    assert result.exit_code == 0

    wav_path = tmp_path / "test-clip.wav"
    txt_path = tmp_path / "test-clip.txt"
    assert wav_path.exists()
    assert txt_path.exists()
    assert txt_path.read_text().strip() == "This is my reference text."


def test_record_clip_refuses_duplicate(tmp_path: Path) -> None:
    _write_wav(tmp_path / "existing.wav")
    (tmp_path / "existing.txt").write_text("already here")

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["record-clip", "--data-dir", str(tmp_path), "--name", "existing", "--duration", "2"],
    )
    assert result.exit_code != 0
    assert "already exists" in result.output


class _FakeArray:
    def __init__(self, n_frames: int) -> None:
        self._data = b"\x00\x00" * n_frames

    def tobytes(self) -> bytes:
        return self._data


def _fake_array(n_frames: int) -> _FakeArray:
    return _FakeArray(n_frames)


def _write_wav(path: Path, n_frames: int = 16000) -> None:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * n_frames)
    path.write_bytes(buf.getvalue())
