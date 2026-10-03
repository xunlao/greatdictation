from __future__ import annotations

import sys

import pytest

from dictate.core.engines.registry import AVAILABLE_ENGINES, get_engine

_SKIP_ENGINES: set[str] = set()
if "parakeet_mlx" not in sys.modules:
    try:
        import parakeet_mlx  # noqa: F401
    except ImportError:
        _SKIP_ENGINES.add("parakeet")


def test_all_engines_instantiate() -> None:
    for name in AVAILABLE_ENGINES:
        if name in _SKIP_ENGINES:
            continue
        engine = get_engine(name, api_key="dummy")
        assert engine.name == name


def test_unknown_engine_raises() -> None:
    with pytest.raises(ValueError, match="Unknown engine"):
        get_engine("nonexistent", api_key="dummy")
