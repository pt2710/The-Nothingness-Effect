"""Cross-module contract gates for gravitational/cosmological/quantum laws."""

from __future__ import annotations

import numpy as np
import pytest

from equations.gravitational_contract_runtime import (
    FieldLawInput,
    SPECS,
    contracts_for,
    registered_module_registry,
)
from equations.theorem_complex_runtime.contracts import evaluate_contract
from equations.theorem_complex_runtime.types import ClosureStatus, ComplexLevel


X = np.linspace(0.0, 2.0 * np.pi, 64)
INPUT = FieldLawInput(X, 1.5 + 0.3 * np.sin(X) + 0.2 * np.cos(2.0 * X), scale=2.5, frequency=1.25)


@pytest.mark.parametrize("module", sorted(SPECS))
def test_each_physical_module_registers_four_a_two_b_one_c(module):
    registry = registered_module_registry(SPECS[module])
    contracts = registry.contracts()

    assert len(contracts) == 7
    assert [item.level for item in contracts].count(ComplexLevel.A) == 4
    assert [item.level for item in contracts].count(ComplexLevel.B) == 2
    assert [item.level for item in contracts].count(ComplexLevel.C) == 1
    assert not [source for contract in contracts for source in contract.source_ids if source not in {item.complex_id for item in contracts}]


@pytest.mark.parametrize("module", sorted(SPECS))
def test_physical_contract_chains_evaluate_without_proof_inflation(module):
    evaluations = tuple(evaluate_contract(contract, INPUT) for contract in contracts_for(SPECS[module]))

    assert all(item.residual is None or item.residual.passed for item in evaluations)
    assert evaluations[-1].status is ClosureStatus.NUMERICAL_CANDIDATE
    assert evaluations[-1].output.coercivity_ratio > 0.0
    assert evaluations[-1].output.boundary_trace_residual >= 0.0
    assert evaluations[-1].output.localization_residual >= 0.0


@pytest.mark.parametrize("module", sorted(SPECS))
def test_all_derived_sources_are_necessary(module):
    for contract in contracts_for(SPECS[module]):
        if contract.level is ComplexLevel.A:
            continue
        removals = tuple(check(INPUT) for check in contract.source_removal_checks)
        assert {str(item.source_id) for item in removals} == {str(item) for item in contract.source_ids}
        assert all(item.necessary for item in removals)
        assert all(item.necessity_residual > 0.0 for item in removals)


@pytest.mark.parametrize("module", sorted(SPECS))
def test_b_laws_are_interactions_not_product_carriers(module):
    for contract in contracts_for(SPECS[module]):
        if contract.level is not ComplexLevel.B:
            continue
        output = contract.operator(INPUT)
        assert output.combined_operator.shape == INPUT.source.shape
        assert output.interaction_energy > 0.0
        assert not np.array_equal(output.combined_operator, output.source_a)
        assert not np.array_equal(output.combined_operator, output.source_b)
