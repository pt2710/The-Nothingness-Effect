from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from equations.mathematical_closure.a_level import (
    OperationCovarianceInput,
    OrientationInput,
    PhaseCoordinateInput,
    PiApproximationInput,
    contracts as a_contracts,
)
from equations.mathematical_closure.b_level import (
    ApproximationHarmonicInput,
    ArithmeticOrientationInput,
    contracts as b_contracts,
)
from equations.mathematical_closure.c_level import SignedPolarFieldInput, contracts as c_contracts
from equations.mathematical_closure.contracts import registered_mathematical_closure_registry
from equations.theorem_complex_runtime import ClosureStatus, evaluate_contract
from equations.theorem_complex_runtime.types import DomainViolationError


ROOT = Path(__file__).resolve().parents[2]


def test_all_seven_mathematical_closure_complexes_register():
    registry = registered_mathematical_closure_registry(
        ROOT / "docs/data/theorem_complex_implementation_matrix.csv"
    )
    assert len(registry.contracts()) == 7


def test_four_a_sources_are_typed_and_residual_checked():
    orientation, covariance, approximation, phase = a_contracts()
    assert evaluate_contract(orientation, OrientationInput(3.0)).status is ClosureStatus.SATISFIED
    cov = OperationCovarianceInput(lambda x, y: x * y, (2.0, 3.0), 0)
    assert evaluate_contract(covariance, cov).status is ClosureStatus.SATISFIED
    approx = evaluate_contract(approximation, PiApproximationInput(12))
    assert approx.status is ClosureStatus.SATISFIED
    phase_input = PhaseCoordinateInput(2.0 + 0j, 0.3, (1.0, 1j, -1.0, -1j))
    assert evaluate_contract(phase, phase_input).status is ClosureStatus.SATISFIED


def test_zero_is_explicit_orientation_boundary():
    with pytest.raises(DomainViolationError, match="boundary"):
        evaluate_contract(a_contracts()[0], OrientationInput(0.0))


def test_b_laws_are_new_interactions_with_both_source_removals():
    arithmetic, harmonic = b_contracts()
    arithmetic_input = ArithmeticOrientationInput(
        lambda x, y: x * y, (2.0, 3.0), (1, 0), 0
    )
    arithmetic_result = evaluate_contract(arithmetic, arithmetic_input)
    assert arithmetic_result.status is ClosureStatus.SATISFIED
    assert arithmetic_result.output.transported_value == -6
    assert all(check(arithmetic_input).necessary for check in arithmetic.source_removal_checks)

    harmonic_input = ApproximationHarmonicInput(
        8,
        (),
        (0.0, 0.25, 0.5, 0.75, 1.0),
        (1.0 + 0j, 0.25 - 0.1j),
        1.0,
    )
    harmonic_result = evaluate_contract(harmonic, harmonic_input)
    assert harmonic_result.status is ClosureStatus.SATISFIED
    assert all(check(harmonic_input).necessary for check in harmonic.source_removal_checks)


def test_c_field_is_a_numerical_candidate_not_a_claimed_minimizer():
    contract = c_contracts()[0]
    value = SignedPolarFieldInput(2.0, 1.0 + 0j, 10, (), (0.0, 0.5, 1.0), 1.0)
    evaluation = evaluate_contract(contract, value)
    assert evaluation.status is ClosureStatus.NUMERICAL_CANDIDATE
    assert evaluation.output.times == (0.0, 0.5, 1.0)
    assert evaluation.residual.metadata["candidate_not_minimizer"] is True
    assert all(check(value).necessary for check in contract.source_removal_checks)


def test_fourier_source_obeys_parseval_and_reconstruction():
    phase = a_contracts()[3]
    sample = tuple(np.exp(2j * np.pi * np.arange(8) / 8))
    result = evaluate_contract(phase, PhaseCoordinateInput(1.0 + 0j, 0.0, sample))
    assert result.output.parseval_residual <= 1e-10
    assert result.output.reconstruction_residual <= 1e-10
