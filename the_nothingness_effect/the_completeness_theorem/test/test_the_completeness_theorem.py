"""Canonical import smoke test for the_completeness_theorem."""

from importlib import import_module


def test_canonical_module_imports():
    assert import_module('the_nothingness_effect.the_completeness_theorem') is not None
