"""A/B/C gates for the fifteen completeness contracts."""

from __future__ import annotations

import numpy as np

from the_nothingness_effect.the_completeness_theorem.contracts import CompletenessInput, contracts, registered_completeness_registry
from the_nothingness_effect.the_completeness_theorem.simulation.godel_boundary import godel_boundary_system
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus, ComplexLevel


STATE = np.array([1.0, -0.5, 2.0, 0.75, -1.25, 0.4])
CLOSURE = np.diag([1.0, 1.0, 1.0, 1.0, 0.0, 0.0])
PARITY = np.diag([1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
INPUT = CompletenessInput(
    godel_boundary_system(),
    STATE,
    CLOSURE,
    PARITY,
    (1, 0, 1, 1, 0, 1),
    np.arange(STATE.size, dtype=float),
)


def test_all_fifteen_completeness_contracts_register_and_resolve_dependencies():
    registry = registered_completeness_registry()

    assert len(registry.contracts()) == 15
    assert registry.counts()["registered_contracts"] == 15
    assert not [source for contract in registry.contracts() for source in contract.source_ids if source not in {item.complex_id for item in registry.contracts()}]


def test_completeness_contracts_evaluate_without_promoting_finite_closure_to_proof():
    evaluations = tuple(evaluate_contract(contract, INPUT) for contract in contracts())

    assert all(item.residual is None or item.residual.passed for item in evaluations)
    assert evaluations[-2].status is ClosureStatus.NUMERICAL_CANDIDATE
    assert evaluations[-1].status is ClosureStatus.NUMERICAL_CANDIDATE
    assert evaluations[0].output.obstruction_count > 0
    assert "proof" not in evaluations[-1].detail.lower()


def test_all_b_and_c_sources_are_necessary():
    for contract in contracts():
        if contract.level is ComplexLevel.A:
            continue
        removals = tuple(check(INPUT) for check in contract.source_removal_checks)
        assert {str(item.source_id) for item in removals} == {str(item) for item in contract.source_ids}
        assert all(item.necessary for item in removals)
        assert all(item.necessity_residual > 0.0 for item in removals)


def test_every_b_law_has_non_cancellation_energy():
    for contract in contracts():
        if contract.level is ComplexLevel.B:
            assert contract.operator(INPUT).non_cancellation_energy > 0.0
