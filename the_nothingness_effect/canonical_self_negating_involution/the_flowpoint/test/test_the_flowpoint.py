"""Canonical import smoke test for the_flowpoint."""

from importlib import import_module


def test_canonical_module_imports():
    assert import_module('the_nothingness_effect.canonical_self_negating_involution.the_flowpoint') is not None
