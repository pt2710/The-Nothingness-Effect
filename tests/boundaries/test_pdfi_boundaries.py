"""Domain and source-law boundaries of the orbit pDFI."""

from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.parity_dfi import parity_dfi, parity_inverse_recurrence
from the_nothingness_effect._runtime.theorem_complex_runtime.types import DomainViolationError


def test_orbit_formula_matches_manual_parity_filtered_average():
    trajectory = np.array([7, 22, 11, 34])
    result = parity_dfi(trajectory)
    expected = np.mean(
        np.abs(np.diff(trajectory % 2))
        * np.abs(np.diff(trajectory) / trajectory[:-1])
    )

    assert np.isclose(result.value, expected)
    assert result.normalization == 3


def test_zero_predecessor_is_an_explicit_domain_failure():
    with pytest.raises(DomainViolationError, match="zero predecessors"):
        parity_dfi([1, 0, 3])


def test_noninteger_orbit_does_not_acquire_an_implicit_parity_label():
    with pytest.raises(DomainViolationError, match="integer-valued"):
        parity_dfi([1.0, 2.5, 3.0])


def test_inverse_recurrence_has_exact_two_cycle_and_inverse_product():
    response = parity_inverse_recurrence(3.0, 8)

    assert np.allclose(response[:-1] * response[1:], 1.0)
    assert np.allclose(response[2:], response[:-2])


@pytest.mark.parametrize("seed", [0.0, -1.0, np.inf, np.nan])
def test_inverse_recurrence_requires_a_positive_finite_seed(seed):
    with pytest.raises(DomainViolationError):
        parity_inverse_recurrence(seed, 3)
