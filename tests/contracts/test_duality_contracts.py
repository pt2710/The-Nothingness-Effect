from __future__ import annotations

from pathlib import Path

import pytest

from the_nothingness_effect.foundational_architecture.duality.a_level import contracts as a_contracts
from the_nothingness_effect.foundational_architecture.duality.b_level import contracts as b_contracts
from the_nothingness_effect.foundational_architecture.duality.c_level import contracts as c_contracts
from the_nothingness_effect.foundational_architecture.duality.contracts import registered_duality_registry
from the_nothingness_effect.foundational_architecture.duality.duality import FiniteInvolution, FreeCofreeInput, TwoStateInput
from the_nothingness_effect._runtime.theorem_complex_runtime import ClosureStatus, evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.types import DomainViolationError


ROOT = Path(__file__).resolve().parents[2]


def free_involution() -> FiniteInvolution:
    return FiniteInvolution((1.0, 3.0, -2.0, 4.0), (1, 0, 3, 2))


def test_six_duality_complexes_register():
    registry = registered_duality_registry(
        ROOT / "docs/data/theorem_complex_implementation_matrix.csv"
    )
    assert len(registry.contracts()) == 6


def test_a_duality_sources_are_exact_and_typed():
    relation, minimal, action = a_contracts()
    assert evaluate_contract(relation, free_involution()).status is ClosureStatus.SATISFIED
    assert evaluate_contract(minimal, TwoStateInput(2.0)).status is ClosureStatus.SATISFIED
    assert evaluate_contract(action, free_involution()).status is ClosureStatus.SATISFIED


def test_invalid_permutation_or_zero_minimal_state_fails():
    with pytest.raises(DomainViolationError):
        FiniteInvolution((1.0, 2.0), (0, 0))
    with pytest.raises(DomainViolationError):
        evaluate_contract(a_contracts()[1], TwoStateInput(0.0))


def test_b_duality_laws_need_each_a_source():
    cover, free_cofree = b_contracts()
    involution = free_involution()
    assert evaluate_contract(cover, involution).status is ClosureStatus.SATISFIED
    assert all(check(involution).necessary for check in cover.source_removal_checks)
    generators = FreeCofreeInput((1.0, 2.0 + 1j))
    assert evaluate_contract(free_cofree, generators).status is ClosureStatus.SATISFIED
    assert all(check(generators).necessary for check in free_cofree.source_removal_checks)


def test_c_orbit_field_has_spatial_boundary_and_b_source_ablation():
    contract = c_contracts()[0]
    involution = free_involution()
    evaluation = evaluate_contract(contract, involution)
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.output.spatial_domain == (0, 1, 2, 3)
    assert evaluation.output.boundary_trace_residual == 0.0
    assert all(check(involution).necessary for check in contract.source_removal_checks)
