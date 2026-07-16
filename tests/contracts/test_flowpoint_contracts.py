from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.a_level import contracts as a_contracts
from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.b_level import (
    PhaseTransportInput,
    ScheduledHistoryInput,
    contracts as b_contracts,
)
from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.c_level import AffineHistoryInput, contracts as c_contracts
from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.contracts import registered_flowpoint_registry
from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.flowpoint import BalanceFiber, PhaseClock
from the_nothingness_effect._runtime.theorem_complex_runtime import ClosureStatus, evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.types import DomainViolationError


ROOT = Path(__file__).resolve().parents[2]


def test_all_seven_flowpoint_complexes_register_against_inventory():
    registry = registered_flowpoint_registry(
        ROOT / "docs/data/theorem_complex_implementation_matrix.csv"
    )
    assert len(registry.contracts()) == 7
    assert {contract.level.value for contract in registry.contracts()} == {"A", "B", "C"}


def test_a_level_contracts_have_typed_domain_codomains_and_invariants():
    involution, schedule, fiber, phase = a_contracts()
    assert evaluate_contract(involution, 3.0).status is ClosureStatus.SATISFIED
    assert evaluate_contract(schedule, (0, 1, 1, 0)).status is ClosureStatus.SATISFIED
    assert evaluate_contract(fiber, BalanceFiber(3.0, -1.0)).status is ClosureStatus.SATISFIED
    assert evaluate_contract(phase, PhaseClock(0)).status is ClosureStatus.SATISFIED


def test_flowpoint_domains_fail_closed():
    involution, schedule, _, phase = a_contracts()
    with pytest.raises(DomainViolationError):
        evaluate_contract(involution, True)
    with pytest.raises(DomainViolationError):
        evaluate_contract(schedule, (0, 2))
    with pytest.raises(DomainViolationError):
        PhaseClock(3)


def test_b_level_contracts_use_both_complete_sources():
    history_contract, transport_contract = b_contracts()
    history_input = ScheduledHistoryInput((0, 0, 1, 1), 2.0)
    history_evaluation = evaluate_contract(history_contract, history_input)
    assert history_evaluation.status is ClosureStatus.SATISFIED
    assert all(check(history_input).necessary for check in history_contract.source_removal_checks)

    transport_input = PhaseTransportInput(
        BalanceFiber(3.0, -1.0), PhaseClock(0), PhaseClock(1), 0.5
    )
    transport_evaluation = evaluate_contract(transport_contract, transport_input)
    assert transport_evaluation.status is ClosureStatus.SATISFIED
    assert all(check(transport_input).necessary for check in transport_contract.source_removal_checks)
    assert np.isclose(transport_evaluation.output.transported.balance, 2.0)


def test_c_level_contract_is_explicitly_spatial_and_closed():
    contract = c_contracts()[0]
    value = AffineHistoryInput((0, 1, 1, 0), 2.0, 0.25, 1.0)
    evaluation = evaluate_contract(contract, value)
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.output.spatial_points == (0, 1, 2, 3)
    assert evaluation.output.local_internal_gradient
    assert evaluation.output.boundary_trace_residual == 0.0
    assert all(check(value).necessary for check in contract.source_removal_checks)
