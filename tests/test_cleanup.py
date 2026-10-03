from __future__ import annotations

import json

import httpx
import pytest
import respx

from dictate.core.cleanup import CleanupConfig, cleanup

CLEANUP_URL = "https://api.openai.com/v1/chat/completions"


@respx.mock
def test_cleanup_removes_filler_and_fixes_punctuation() -> None:
    respx.post(CLEANUP_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "Hello, how are you doing today?"}}],
            },
        )
    )
    result = cleanup(
        "um hello uh how are you doing today",
        api_key="test-key",
        vocab=["pytest"],
    )
    assert result == "Hello, how are you doing today?"

    req = respx.calls.last.request
    body = json.loads(req.content)
    assert body["model"] == "gpt-4.1-mini"
    assert any("pytest" in m["content"] for m in body["messages"])


@respx.mock
def test_cleanup_passes_vocab_in_prompt() -> None:
    respx.post(CLEANUP_URL).mock(
        return_value=httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Set up PyTorch and Kubernetes."}}]},
        )
    )
    result = cleanup(
        "set up pie torch and kuber netties",
        api_key="test-key",
        vocab=["PyTorch", "Kubernetes"],
    )
    assert result == "Set up PyTorch and Kubernetes."

    req = respx.calls.last.request
    body = json.loads(req.content)
    user_msg = next(m["content"] for m in body["messages"] if m["role"] == "user")
    assert "pie torch and kuber netties" in user_msg


@respx.mock
def test_cleanup_with_empty_vocab() -> None:
    respx.post(CLEANUP_URL).mock(
        return_value=httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Hello world."}}]},
        )
    )
    result = cleanup("hello world", api_key="test-key", vocab=[])
    assert result == "Hello world."


@respx.mock
def test_cleanup_preserves_meaning() -> None:
    respx.post(CLEANUP_URL).mock(
        return_value=httpx.Response(
            200,
            json={"choices": [{"message": {"content": "I disagree with that approach."}}]},
        )
    )
    result = cleanup(
        "I disagree with that approach",
        api_key="test-key",
    )
    assert result == "I disagree with that approach."

    req = respx.calls.last.request
    body = json.loads(req.content)
    system_msg = next(m["content"] for m in body["messages"] if m["role"] == "system")
    assert "never add" in system_msg.lower() or "do not add" in system_msg.lower()


def test_cleanup_without_api_key_returns_original() -> None:
    result = cleanup("hello world")
    assert result == "hello world"


def test_cleanup_config_has_model_and_url() -> None:
    cfg = CleanupConfig(api_key="test-key")
    config_dict = cfg.config
    assert "model" in config_dict
    assert "api_url" in config_dict


def test_cleanup_config_default_model() -> None:
    cfg = CleanupConfig(api_key="test-key")
    assert cfg.config["model"] == "gpt-4.1-mini"


def test_cleanup_config_custom_model() -> None:
    cfg = CleanupConfig(api_key="test-key", model="gpt-4.1")
    assert cfg.config["model"] == "gpt-4.1"


@pytest.mark.skipif(
    not __import__("os").environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set",
)
def test_cleanup_live() -> None:
    import os

    result = cleanup(
        "um so like I was uh thinking about using pie test for the tests",
        api_key=os.environ["OPENAI_API_KEY"],
        vocab=["pytest"],
    )
    assert "pytest" in result.lower()
    assert "um" not in result.lower()
