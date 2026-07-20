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
from the_nothingness_effect.foundational_architecture.spatiality.derived_contracts import contracts as spatiality_contracts
from the_nothingness_effect.foundational_architecture.symmetry.derived_contracts import contracts as symmetry_contracts
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.derived_contracts import (
    contracts as dtqc_contracts,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature.derived_contracts import (
    contracts as edi_contracts,
)


_ALL_CONTRACTS = (
    dfi_contracts()
    + qenn_contracts()
    + pgqenn_contracts()
    + soinet_contracts()
    + symmetry_contracts()
    + spatiality_contracts()
    + edi_contracts()
    + dtqc_contracts()
)
CONTRACTS = tuple(
    contract
    for contract in _ALL_CONTRACTS
    if contract.level in {ComplexLevel.B, ComplexLevel.C}
)


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
        if isinstance(evaluation.output, SpatialClosureResult):
            assert evaluation.output.local_operator.shape == next(iter(fields.values())).shape
            assert evaluation.output.boundary_trace_residual == 0.0
            assert evaluation.output.reconstruction_residual == 0.0
            assert evaluation.output.coercivity_ratio > 0.0
            assert evaluation.status is ClosureStatus.NUMERICAL_CANDIDATE
        else:
            # Specialized C implementations may retain SpatialClosureInput as a
            # provenance-compatible adapter while returning their own typed exact
            # certificate.  They must then pass their independent residual and
            # exact closure predicate rather than masquerade as the generic
            # numerical spatial carrier.
            assert contract.exact_semantics is True
            assert evaluation.residual is not None and evaluation.residual.passed
            assert getattr(evaluation.output, "closure_status", None) == "closed"
            assert evaluation.status is ClosureStatus.CLOSED

    removals = tuple(check(value) for check in contract.source_removal_checks)
    assert len(removals) == len(contract.source_ids)
    assert {str(result.source_id) for result in removals} == {
        str(source_id) for source_id in contract.source_ids
    }
    assert all(result.necessary and result.necessity_residual > 0.0 for result in removals)


def test_all_affected_generated_contracts_are_unique_and_source_complete():
    identifiers = [str(contract.complex_id) for contract in CONTRACTS]
    assert len(identifiers) == 36
    assert len(identifiers) == len(set(identifiers))
    assert all(len(contract.source_ids) >= 2 for contract in CONTRACTS)
    assert all(contract.residual is not None for contract in CONTRACTS)
    assert all(len(contract.source_removal_checks) == len(contract.source_ids) for contract in CONTRACTS)
    assert all(
        contract.closure_predicate is not None
        for contract in CONTRACTS
        if contract.level is ComplexLevel.C
    )
