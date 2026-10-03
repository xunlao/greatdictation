from __future__ import annotations

from dictate.core.cleanup import cleanup


def test_cleanup_passthrough() -> None:
    assert cleanup("hello world") == "hello world"


def test_cleanup_with_vocab() -> None:
    assert cleanup("hello world", vocab=["pytest"]) == "hello world"
