"""Semantic carrier audit for newly completed appendix B/C laws."""

from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import (
    AdditiveDerivationInput,
    AdditiveDerivationResult,
    SpatialClosureInput,
    SpatialClosureResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus, ComplexLevel
from the_nothingness_effect.artificial_intelligence.pgqenn.derived_contracts import contracts as pgqenn_contracts
from the_nothingness_effect.artificial_intelligence.qenn.derived_contracts import contracts as qenn_contracts
from the_nothingness_effect.artificial_intelligence.soinets.derived_contracts import contracts as soinet_contracts
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.derived_contracts import (
    contracts as dfi_contracts,
)


CONTRACTS = dfi_contracts() + qenn_contracts() + pgqenn_contracts() + soinet_contracts()


def _source_fields(contract):
    return {
        str(source_id): np.full((6, 4), float(index + 1))
        for index, source_id in enumerate(contract.source_ids)
    }


@pytest.mark.parametrize("contract", CONTRACTS, ids=lambda item: str(item.complex_id))
def test_derived_law_uses_every_source_and_is_not_a_passive_carrier(contract):
    fields = _source_fields(contract)
    if contract.level is ComplexLevel.B:
        value = AdditiveDerivationInput(fields)
        evaluation = evaluate_contract(contract, value)
        assert isinstance(evaluation.output, AdditiveDerivationResult)
        expected = np.add.reduce(tuple(fields.values()))
        assert np.array_equal(evaluation.output.derived_operator, expected)
        assert evaluation.output.additive_residual == 0.0
        assert evaluation.output.non_cancellation_margin > 0.0
        assert evaluation.status is ClosureStatus.SATISFIED
    else:
        value = SpatialClosureInput(fields)
        evaluation = evaluate_contract(contract, value)
        assert isinstance(evaluation.output, SpatialClosureResult)
        assert evaluation.output.local_operator.shape == next(iter(fields.values())).shape
        assert evaluation.output.boundary_trace_residual == 0.0
        assert evaluation.output.reconstruction_residual == 0.0
        assert evaluation.output.coercivity_ratio > 0.0
        assert evaluation.status is ClosureStatus.NUMERICAL_CANDIDATE

    removals = tuple(check(value) for check in contract.source_removal_checks)
    assert len(removals) == len(contract.source_ids)
    assert {str(result.source_id) for result in removals} == {
        str(source_id) for source_id in contract.source_ids
    }
    assert all(result.necessary and result.necessity_residual > 0.0 for result in removals)


def test_all_affected_generated_contracts_are_unique_and_source_complete():
    identifiers = [str(contract.complex_id) for contract in CONTRACTS]
    assert len(identifiers) == 23
    assert len(identifiers) == len(set(identifiers))
    assert all(len(contract.source_ids) >= 2 for contract in CONTRACTS)
    assert all(contract.residual is not None for contract in CONTRACTS)
    assert all(len(contract.source_removal_checks) == len(contract.source_ids) for contract in CONTRACTS)
    assert all(
        contract.closure_predicate is not None
        for contract in CONTRACTS
        if contract.level is ComplexLevel.C
    )
