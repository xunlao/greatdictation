from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def _mock_desktop_deps(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub macOS-only modules so tests run anywhere."""
    for mod in [
        "sounddevice",
        "AppKit",
        "Foundation",
        "Cocoa",
        "Quartz",
        "Quartz.CoreGraphics",
    ]:
        monkeypatch.setitem(sys.modules, mod, MagicMock())


def test_get_config_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DICTATE_ENGINE", raising=False)
    monkeypatch.delenv("DICTATE_CLEANUP", raising=False)

    from dictate.desktop.app import _get_config

    config = _get_config()
    assert config["engine"] == "openai-whisper"
    assert config["cleanup"] == "0"


def test_get_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DICTATE_ENGINE", "deepgram")
    monkeypatch.setenv("DICTATE_CLEANUP", "1")

    from dictate.desktop.app import _get_config

    config = _get_config()
    assert config["engine"] == "deepgram"
    assert config["cleanup"] == "1"
