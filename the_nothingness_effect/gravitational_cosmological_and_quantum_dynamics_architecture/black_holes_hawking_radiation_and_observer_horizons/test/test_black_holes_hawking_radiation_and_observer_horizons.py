"""Canonical import smoke test for black_holes_hawking_radiation_and_observer_horizons."""

from importlib import import_module


def test_canonical_module_imports():
    assert import_module('the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons') is not None
