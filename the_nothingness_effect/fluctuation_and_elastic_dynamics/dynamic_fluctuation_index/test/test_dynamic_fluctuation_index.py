"""Canonical import smoke test for dynamic_fluctuation_index."""

from importlib import import_module


def test_canonical_module_imports():
    assert import_module('the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index') is not None
