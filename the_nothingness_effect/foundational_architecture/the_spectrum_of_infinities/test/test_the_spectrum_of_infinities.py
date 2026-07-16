"""Canonical import smoke test for the_spectrum_of_infinities."""

from importlib import import_module


def test_canonical_module_imports():
    assert import_module('the_nothingness_effect.foundational_architecture.the_spectrum_of_infinities') is not None
