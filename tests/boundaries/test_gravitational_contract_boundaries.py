"""Shared domain boundaries for physical field theorem contracts."""

from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import FieldLawInput, source_operator
from the_nothingness_effect._runtime.theorem_complex_runtime.types import DomainViolationError, NonFiniteValueError


def test_nonuniform_spatial_grid_is_rejected():
    with pytest.raises(DomainViolationError, match="uniform"):
        source_operator("ripple_wave", FieldLawInput(np.array([0.0, 1.0, 2.0, 4.0, 5.0]), np.ones(5)))


@pytest.mark.parametrize("scale", [0.0, -1.0, np.inf, np.nan])
def test_nonpositive_or_nonfinite_scale_is_rejected(scale):
    with pytest.raises(DomainViolationError):
        source_operator("dubler_ratio", FieldLawInput(np.arange(5.0), np.ones(5), scale=scale))


def test_nonfinite_field_is_not_masked():
    with pytest.raises(NonFiniteValueError):
        source_operator("log_curvature", FieldLawInput(np.arange(5.0), np.array([1.0, 2.0, np.nan, 4.0, 5.0])))


def test_too_short_field_fails_before_a_stencil_is_applied():
    with pytest.raises(DomainViolationError, match="at least five"):
        source_operator("log_curvature", FieldLawInput(np.arange(4.0), np.ones(4)))
