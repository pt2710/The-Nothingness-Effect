"""Canonical import smoke test for observation_and_collapse."""

from importlib import import_module


def test_canonical_module_imports():
    assert import_module('the_nothingness_effect.foundational_architecture.observation_and_collapse') is not None
