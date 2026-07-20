from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_artifacts import fixture
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts.harmonic_clock_contract import (
    _field_adapter,
    contract,
    harmonic_clock_operator,
)


def test_damping_and_lag_corrections_recover_source_clock():
    theorem = contract()
    evaluation = evaluate_contract(theorem, fixture())

    assert theorem.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.residual is not None and evaluation.residual.passed
    assert evaluation.output.closure_status == "closed"
    assert evaluation.output.correction_identity_residual == pytest.approx(0.0)
    assert evaluation.output.source_coupling_residual < 1e-10
    assert evaluation.output.time_invariance_residual < 1e-10
    assert evaluation.output.distance_invariance_residual < 1e-10
    assert evaluation.output.denominator_margin > 0.0
    assert evaluation.output.perturbation_bound_residual == pytest.approx(0.0)
    np.testing.assert_allclose(
        evaluation.output.corrected_clock,
        evaluation.output.expected_source_coupling,
        atol=1e-10,
    )


def test_corrupted_corrected_clock_is_localized_and_open():
    source = _field_adapter(fixture())
    exact = harmonic_clock_operator(source)
    corrupted = exact.corrected_clock.copy()
    corrupted[1, 1] += 0.2 + 0.1j
    evaluation = evaluate_contract(
        contract(),
        replace(source, corrected_clock=corrupted),
    )

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.correction_identity_residual > 0.0
    assert evaluation.output.time_invariance_residual > 0.0
    assert evaluation.residual is not None and not evaluation.residual.passed


def test_vanishing_fundamental_is_not_falsely_closed():
    source = _field_adapter(fixture())
    evaluation = evaluate_contract(
        contract(),
        replace(
            source,
            observed_fundamental=np.zeros_like(source.observed_fundamental),
        ),
    )

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.denominator_margin == pytest.approx(0.0)


def test_explicit_perturbation_bound_dominates_log_clock_change():
    output = harmonic_clock_operator(fixture())

    assert output.perturbation_log_norm <= output.perturbation_bound + 1e-15
    assert output.perturbation_bound_residual == pytest.approx(0.0)


def test_quality_and_lag_sources_are_both_necessary():
    theorem = contract()
    removals = tuple(check(fixture()) for check in theorem.source_removal_checks)

    assert len(removals) == 2
    assert all(item.necessary for item in removals)
    assert all(item.necessity_residual > 0.0 for item in removals)
