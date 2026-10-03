from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def _mock_macos_frameworks(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Stub out pyobjc Cocoa and Quartz so tests run on any platform."""
    appkit = MagicMock()
    foundation = MagicMock()
    cocoa = MagicMock()

    pb = MagicMock()
    appkit.NSPasteboard.generalPasteboard.return_value = pb
    appkit.NSPasteboardTypeString = "public.utf8-plain-text"

    monkeypatch.setitem(sys.modules, "AppKit", appkit)
    monkeypatch.setitem(sys.modules, "Foundation", foundation)
    monkeypatch.setitem(sys.modules, "Cocoa", cocoa)

    quartz = MagicMock()
    monkeypatch.setitem(sys.modules, "Quartz", quartz)
    monkeypatch.setitem(sys.modules, "Quartz.CoreGraphics", MagicMock())

    monkeypatch.delitem(sys.modules, "dictate.desktop.paste", raising=False)

    return pb


def _get_pb() -> MagicMock:
    appkit = sys.modules["AppKit"]
    return appkit.NSPasteboard.generalPasteboard()


def test_save_and_restore_clipboard() -> None:
    from dictate.desktop.paste import restore_clipboard, save_clipboard

    pb = _get_pb()
    pb.stringForType_.return_value = "original text"
    saved = save_clipboard()

    assert saved == "original text"

    restore_clipboard(saved)
    pb.clearContents.assert_called()
    pb.setString_forType_.assert_called()


def test_set_clipboard() -> None:
    from dictate.desktop.paste import set_clipboard

    pb = _get_pb()
    set_clipboard("new text")
    pb.clearContents.assert_called()
    pb.setString_forType_.assert_called()


def test_paste_into_active_app() -> None:
    from dictate.desktop.paste import paste_text

    pb = _get_pb()
    paste_text("hello world")
    pb.clearContents.assert_called()
