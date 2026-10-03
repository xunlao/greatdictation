from __future__ import annotations

import sys
import wave
from io import BytesIO
from unittest.mock import MagicMock

import pytest


class FakeArray:
    """Minimal stand-in for a numpy int16 array."""

    def __init__(self, n_frames: int) -> None:
        self._data = b"\x00\x00" * n_frames

    def tobytes(self) -> bytes:
        return self._data


@pytest.fixture(autouse=True)
def _mock_sounddevice(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    sd = MagicMock(spec=["rec", "wait", "default", "query_devices"])
    sd.default = MagicMock()
    monkeypatch.setitem(sys.modules, "sounddevice", sd)
    monkeypatch.delitem(sys.modules, "dictate.desktop.recorder", raising=False)
    return sd


def test_record_returns_wav_bytes() -> None:
    sd = sys.modules["sounddevice"]
    sd.rec.return_value = FakeArray(16000)

    from dictate.desktop.recorder import record_audio

    audio = record_audio(duration_s=1.0, sample_rate=16000)

    sd.rec.assert_called_once()
    sd.wait.assert_called_once()
    assert isinstance(audio, bytes)

    buf = BytesIO(audio)
    with wave.open(buf, "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 16000
        assert wf.getnframes() == 16000


def test_record_audio_uses_correct_params() -> None:
    sd = sys.modules["sounddevice"]
    sd.rec.return_value = FakeArray(48000 * 3)

    from dictate.desktop.recorder import record_audio

    record_audio(duration_s=3.0, sample_rate=48000)

    call_args = sd.rec.call_args
    assert call_args[0][0] == 3 * 48000
    assert call_args[1]["samplerate"] == 48000
    assert call_args[1]["channels"] == 1
