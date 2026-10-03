from __future__ import annotations

import struct
import wave
from io import BytesIO

import pytest


@pytest.fixture
def wav_bytes() -> bytes:
    """A minimal valid WAV file (0.1s of silence at 16kHz mono 16-bit)."""
    buf = BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(struct.pack("<" + "h" * 1600, *([0] * 1600)))
    return buf.getvalue()
