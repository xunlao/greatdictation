from __future__ import annotations

import wave
from io import BytesIO

import sounddevice as sd


def record_audio(*, duration_s: float, sample_rate: int = 16000) -> bytes:
    """Record from the default mic and return WAV bytes."""
    frames = int(duration_s * sample_rate)
    recording = sd.rec(frames, samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()

    buf = BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(recording.tobytes())
    return buf.getvalue()
