"""Canonical import smoke test for mathematical_architecture."""

from importlib import import_module


def test_canonical_module_imports():
    assert import_module('the_nothingness_effect.mathematical_architecture') is not None
