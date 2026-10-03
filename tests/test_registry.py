from __future__ import annotations

import pytest

from dictate.core.engines.registry import AVAILABLE_ENGINES, get_engine


def test_all_engines_instantiate() -> None:
    for name in AVAILABLE_ENGINES:
        engine = get_engine(name, api_key="dummy")
        assert engine.name == name


def test_unknown_engine_raises() -> None:
    with pytest.raises(ValueError, match="Unknown engine"):
        get_engine("nonexistent", api_key="dummy")
