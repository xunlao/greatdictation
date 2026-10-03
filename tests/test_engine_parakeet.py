from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture()
def _mock_parakeet(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Stub parakeet_mlx so tests run without MLX / Apple Silicon."""
    mod = MagicMock()
    monkeypatch.setitem(sys.modules, "parakeet_mlx", mod)
    monkeypatch.delitem(sys.modules, "dictate.core.engines.parakeet", raising=False)
    return mod


@pytest.mark.usefixtures("_mock_parakeet")
class TestParakeetMocked:
    def test_transcribe_returns_transcript(self) -> None:
        parakeet = sys.modules["parakeet_mlx"]
        model = MagicMock()
        result = MagicMock()
        result.text = "Hello world."
        model.transcribe.return_value = result
        parakeet.from_pretrained.return_value = model

        from dictate.core.engines.parakeet import ParakeetEngine

        engine = ParakeetEngine()
        transcript = engine.transcribe(b"fake-wav-bytes", vocab=[])

        assert transcript.text == "Hello world."
        assert transcript.engine == "parakeet"
        model.transcribe.assert_called_once()

    def test_transcribe_writes_temp_file(self) -> None:
        parakeet = sys.modules["parakeet_mlx"]
        model = MagicMock()
        result = MagicMock()
        result.text = "test"
        model.transcribe.return_value = result
        parakeet.from_pretrained.return_value = model

        from dictate.core.engines.parakeet import ParakeetEngine

        engine = ParakeetEngine()
        engine.transcribe(b"fake-wav-bytes", vocab=[])

        call_args = model.transcribe.call_args
        audio_path = call_args[0][0]
        assert audio_path.endswith(".wav")
        assert not os.path.exists(audio_path)

    def test_name(self) -> None:
        from dictate.core.engines.parakeet import ParakeetEngine

        engine = ParakeetEngine()
        assert engine.name == "parakeet"

    def test_model_loaded_once(self) -> None:
        parakeet = sys.modules["parakeet_mlx"]
        model = MagicMock()
        result = MagicMock()
        result.text = "text"
        model.transcribe.return_value = result
        parakeet.from_pretrained.return_value = model

        from dictate.core.engines.parakeet import ParakeetEngine

        engine = ParakeetEngine()
        engine.transcribe(b"audio1", vocab=[])
        engine.transcribe(b"audio2", vocab=[])

        parakeet.from_pretrained.assert_called_once()


@pytest.mark.live()
def test_parakeet_live() -> None:
    try:
        import parakeet_mlx  # noqa: F401
    except ImportError:
        pytest.skip("parakeet-mlx not installed")

    from dictate.core.engines.parakeet import ParakeetEngine

    engine = ParakeetEngine()

    import io
    import wave

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 16000)
    audio = buf.getvalue()

    result = engine.transcribe(audio, vocab=[])
    assert isinstance(result.text, str)
    assert result.engine == "parakeet"
    assert result.latency_ms >= 0
