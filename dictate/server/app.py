from __future__ import annotations

import os

from fastapi import Depends, FastAPI, Form, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from dictate.core.cleanup import cleanup
from dictate.core.engines.registry import AVAILABLE_ENGINES, ENGINE_KEYS, get_engine

_bearer = HTTPBearer()


def _get_token() -> str:
    token = os.environ.get("DICTATE_API_TOKEN", "")
    if not token:
        raise RuntimeError("DICTATE_API_TOKEN must be set")
    return token


def _verify_token(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),  # noqa: B008
) -> str:
    if creds.credentials != _get_token():
        raise HTTPException(status_code=403, detail="Invalid token")
    return creds.credentials


def _load_vocab() -> list[str]:
    path = os.environ.get("DICTATE_VOCAB_FILE", "")
    if not path or not os.path.isfile(path):
        return []
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]


def _transcribe(
    audio: bytes,
    *,
    engine_name: str | None = None,
) -> str:
    name = engine_name or os.environ.get("DICTATE_ENGINE", "openai-whisper")
    if name not in AVAILABLE_ENGINES:
        raise HTTPException(status_code=400, detail=f"Unknown engine: {name}")

    env_var = ENGINE_KEYS[name]
    api_key = os.environ.get(env_var, "")
    if not api_key:
        raise HTTPException(status_code=500, detail=f"{env_var} not set")

    engine = get_engine(name, api_key=api_key)
    vocab = _load_vocab()
    result = engine.transcribe(audio, vocab=vocab)
    text = result.text

    if os.environ.get("DICTATE_CLEANUP", "0") == "1":
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if openai_key:
            text = cleanup(text, api_key=openai_key, vocab=vocab)

    return text


def create_app() -> FastAPI:
    app = FastAPI(title="Dictate", docs_url=None, redoc_url=None)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/transcribe")
    async def transcribe(
        file: UploadFile,
        engine: str | None = Form(default=None),
        _token: str = Depends(_verify_token),
    ) -> dict[str, str]:
        audio = await file.read()
        text = _transcribe(audio, engine_name=engine)
        return {"text": text}

    return app
