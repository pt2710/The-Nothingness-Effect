"""Canonical import smoke test for flowpoint_math_operations."""

from importlib import import_module


def test_canonical_module_imports():
    assert import_module('the_nothingness_effect.mathematical_architecture.flowpoint_math_operations') is not None
