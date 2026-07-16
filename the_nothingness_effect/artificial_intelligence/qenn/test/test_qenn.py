"""Canonical import smoke test for qenn."""

from importlib import import_module


def test_canonical_module_imports():
    assert import_module('the_nothingness_effect.artificial_intelligence.qenn') is not None
