from __future__ import annotations

import io
import wave
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


def _make_wav(duration_s: float = 0.5, sample_rate: int = 16000) -> bytes:
    buf = io.BytesIO()
    n_frames = int(duration_s * sample_rate)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * n_frames)
    return buf.getvalue()


@pytest.fixture()
def _server_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DICTATE_API_TOKEN", "test-secret-token")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")


@pytest.fixture()
def client(_server_env: None) -> TestClient:
    from dictate.server.app import create_app

    return TestClient(create_app())


def _auth(token: str = "test-secret-token") -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_missing_auth(client: TestClient) -> None:
    wav = _make_wav()
    resp = client.post("/transcribe", files={"file": ("clip.wav", wav, "audio/wav")})
    assert resp.status_code == 401


def test_wrong_token(client: TestClient) -> None:
    wav = _make_wav()
    resp = client.post(
        "/transcribe",
        files={"file": ("clip.wav", wav, "audio/wav")},
        headers=_auth("wrong-token"),
    )
    assert resp.status_code == 403


@patch("dictate.server.app._transcribe")
def test_transcribe_returns_text(mock_transcribe: MagicMock, client: TestClient) -> None:
    mock_transcribe.return_value = "Hello world."
    wav = _make_wav()
    resp = client.post(
        "/transcribe",
        files={"file": ("clip.wav", wav, "audio/wav")},
        headers=_auth(),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["text"] == "Hello world."
    mock_transcribe.assert_called_once()


@patch("dictate.server.app._transcribe")
def test_transcribe_with_engine_param(mock_transcribe: MagicMock, client: TestClient) -> None:
    mock_transcribe.return_value = "Hello."
    wav = _make_wav()
    resp = client.post(
        "/transcribe",
        files={"file": ("clip.wav", wav, "audio/wav")},
        data={"engine": "deepgram"},
        headers=_auth(),
    )
    assert resp.status_code == 200
    args, kwargs = mock_transcribe.call_args
    assert kwargs.get("engine_name") == "deepgram" or args[1] == "deepgram"


@patch("dictate.server.app._transcribe")
def test_transcribe_with_cleanup(
    mock_transcribe: MagicMock,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DICTATE_CLEANUP", "1")
    mock_transcribe.return_value = "Cleaned text."
    wav = _make_wav()
    resp = client.post(
        "/transcribe",
        files={"file": ("clip.wav", wav, "audio/wav")},
        headers=_auth(),
    )
    assert resp.status_code == 200
    assert resp.json()["text"] == "Cleaned text."


def test_health_check(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
