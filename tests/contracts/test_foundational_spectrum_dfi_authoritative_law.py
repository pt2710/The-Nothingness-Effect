"""Authoritative finite checks for Spectrum--DFI scaling and divergence gates."""

from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import all_contracts
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
    NonFiniteValueError,
)
from the_nothingness_effect.foundational_architecture.the_spectrum_of_infinities.canonical_contracts import (
    A2,
    DFIInput,
)


def _contract():
    return {item.complex_id: item for item in all_contracts()}[A2]


def test_spectrum_dfi_uses_exact_normalized_baseline_scaling():
    omega = 6.0
    multipliers = np.asarray((1.0, 2.0, 4.0))
    evaluation = evaluate_contract(_contract(), DFIInput(multipliers, omega))
    output = evaluation.output

    baseline = omega / multipliers.size
    centered = multipliers - 1.0
    fluctuations = baseline * centered
    assert output.values[1][0] == pytest.approx(baseline)
    assert np.allclose(output.values[2], baseline * multipliers)
    assert np.allclose(output.values[3], fluctuations)
    assert output.values[5] == pytest.approx(np.exp(fluctuations))
    assert output.values[4][1] == pytest.approx(
        baseline * np.linalg.norm(centered, ord=2)
    )
    assert all(item == pytest.approx(0.0) for item in output.residuals)


def test_spectrum_dfi_fails_closed_outside_finite_regular_sector():
    with pytest.raises(DomainViolationError):
        evaluate_contract(_contract(), DFIInput(np.asarray((1.0, 2.0)), 0.0))
    with pytest.raises(NonFiniteValueError):
        evaluate_contract(
            _contract(),
            DFIInput(np.asarray((1.0, float("inf"))), 2.0),
        )
    with pytest.raises(NonFiniteValueError):
        evaluate_contract(
            _contract(),
            DFIInput(np.asarray((1.0, 1.0e308)), 2.0),
        )
