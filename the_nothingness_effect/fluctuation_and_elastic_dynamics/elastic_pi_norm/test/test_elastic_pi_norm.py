"""Canonical import smoke test for elastic_pi_norm."""

from importlib import import_module


def test_canonical_module_imports():
    assert import_module('the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi_norm') is not None
