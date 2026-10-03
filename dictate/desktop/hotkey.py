from __future__ import annotations

from typing import TYPE_CHECKING

from Quartz import (
    CFMachPortCreateRunLoopSource,
    CFRunLoopAddSource,
    CFRunLoopGetCurrent,
    CFRunLoopRun,
    CFRunLoopStop,
    CGEventGetIntegerValueField,
    CGEventMaskBit,
    CGEventTapCreate,
    CGEventTapEnable,
    kCFRunLoopCommonModes,
    kCGEventFlagMaskAlternate,
    kCGEventFlagsChanged,
    kCGEventTapDisabledByTimeout,
    kCGHeadInsertEventTap,
    kCGKeyboardEventKeycode,
    kCGSessionEventTap,
)

if TYPE_CHECKING:
    from collections.abc import Callable

RIGHT_OPTION_KEYCODE = 61


class HoldToTalkListener:
    """Listens for a hold-to-talk hotkey via a Quartz event tap."""

    def __init__(
        self,
        *,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
        keycode: int = RIGHT_OPTION_KEYCODE,
    ) -> None:
        self._on_press = on_press
        self._on_release = on_release
        self._keycode = keycode
        self._held = False
        self._tap = None
        self._loop = None

    def _callback(self, proxy, event_type, event, refcon):  # noqa: ANN001, ANN201
        if event_type == kCGEventTapDisabledByTimeout:
            if self._tap is not None:
                CGEventTapEnable(self._tap, True)
            return event

        if event_type != kCGEventFlagsChanged:
            return event

        keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
        if keycode != self._keycode:
            return event

        from Quartz import CGEventGetFlags

        flags = CGEventGetFlags(event)
        option_held = bool(flags & kCGEventFlagMaskAlternate)

        if option_held and not self._held:
            self._held = True
            self._on_press()
        elif not option_held and self._held:
            self._held = False
            self._on_release()

        return event

    def start(self) -> None:
        """Start listening. Blocks the calling thread."""
        mask = CGEventMaskBit(kCGEventFlagsChanged)
        self._tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            0,
            mask,
            self._callback,
            None,
        )
        if self._tap is None:
            raise RuntimeError(
                "Failed to create event tap. "
                "Grant Accessibility permission in System Settings → "
                "Privacy & Security → Accessibility."
            )

        source = CFMachPortCreateRunLoopSource(None, self._tap, 0)
        self._loop = CFRunLoopGetCurrent()
        CFRunLoopAddSource(self._loop, source, kCFRunLoopCommonModes)
        CGEventTapEnable(self._tap, True)
        CFRunLoopRun()

    def stop(self) -> None:
        """Stop the run loop."""
        if self._loop is not None:
            CFRunLoopStop(self._loop)
