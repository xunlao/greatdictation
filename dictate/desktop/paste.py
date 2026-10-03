from __future__ import annotations

import time

from AppKit import NSPasteboard, NSPasteboardTypeString
from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventPost,
    CGEventSetFlags,
    kCGEventFlagMaskCommand,
    kCGHIDEventTap,
)


def save_clipboard() -> str | None:
    """Return current clipboard text (or None)."""
    pb = NSPasteboard.generalPasteboard()
    return pb.stringForType_(NSPasteboardTypeString)


def restore_clipboard(text: str | None) -> None:
    """Put *text* back on the clipboard."""
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    if text is not None:
        pb.setString_forType_(text, NSPasteboardTypeString)


def set_clipboard(text: str) -> None:
    """Set clipboard to *text*."""
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    pb.setString_forType_(text, NSPasteboardTypeString)


def _send_cmd_v() -> None:
    """Simulate Cmd+V keypress."""
    # 'v' virtual keycode is 9
    v_keycode = 9
    event_down = CGEventCreateKeyboardEvent(None, v_keycode, True)
    CGEventSetFlags(event_down, kCGEventFlagMaskCommand)
    event_up = CGEventCreateKeyboardEvent(None, v_keycode, False)
    CGEventSetFlags(event_up, kCGEventFlagMaskCommand)

    CGEventPost(kCGHIDEventTap, event_down)
    CGEventPost(kCGHIDEventTap, event_up)


def paste_text(text: str) -> None:
    """Set clipboard to *text* and paste via Cmd+V."""
    set_clipboard(text)
    time.sleep(0.05)
    _send_cmd_v()
