"""Canonical import smoke test for soinets."""

from importlib import import_module


def test_canonical_module_imports():
    assert import_module('the_nothingness_effect.artificial_intelligence.soinets') is not None
