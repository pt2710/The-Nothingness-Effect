"""Contract tests for the canonical DFI source and derived laws."""

from __future__ import annotations

import numpy as np

from equations.dynamic_fluctuation_index.contracts import (
    ApplicabilityInput,
    DFIInput,
    DFIRescalingInput,
    SpatialDFIInput,
    contracts,
)
from equations.dynamic_fluctuation_index.dfi import DFIStatus
from tne_runtime.theorem_complex_runtime.contracts import evaluate_contract
from tne_runtime.theorem_complex_runtime.types import ClosureStatus, ComplexLevel


DATA = np.array(
    [
        [1.0, 2.0, 4.0],
        [2.0, 3.0, 5.0],
        [3.0, 5.0, 8.0],
        [5.0, 8.0, 13.0],
    ]
)


def _input_for(contract_id: str):
    if contract_id == "dfi_spectrum_normalized_existence_and_normalization_breakdown":
        return DFIInput(DATA, 7.0)
    if contract_id == "dfi_invariance_under_soi_rescaling_and_spurious_scale_dependence":
        return DFIRescalingInput(DATA, 7.0, 19.0)
    if contract_id == "dfi_entropic_fluctuation_encoding_and_fluctuation_divergence":
        return DFIInput(DATA, 7.0)
    if contract_id == "scale_normalized_dfi_homogeneity_invariant":
        return DFIRescalingInput(DATA, 7.0, 19.0)
    if contract_id == "entropic_applicability_response_operator":
        return ApplicabilityInput(DATA, 7.0, threshold=0.01)
    return SpatialDFIInput(DATA, spectrum_scale=7.0)


def test_all_six_dfi_contracts_evaluate_with_typed_outputs():
    evaluations = {
        str(contract.complex_id): evaluate_contract(contract, _input_for(str(contract.complex_id)))
        for contract in contracts()
    }

    assert len(evaluations) == 6
    assert evaluations["dfi_spectrum_normalized_existence_and_normalization_breakdown"].output.status is DFIStatus.FINITE
    assert evaluations["dfi_invariance_under_soi_rescaling_and_spurious_scale_dependence"].output.rescaling_residual <= 1e-12
    assert evaluations["spatially_localized_dfi_consistency_closure"].status is ClosureStatus.NUMERICAL_CANDIDATE


def test_b_and_c_contracts_require_every_complete_source():
    for contract in contracts():
        if contract.level is ComplexLevel.A:
            continue
        value = _input_for(str(contract.complex_id))
        removals = tuple(check(value) for check in contract.source_removal_checks)
        assert len(removals) == len(contract.source_ids)
        assert {str(item.source_id) for item in removals} == {str(item) for item in contract.source_ids}
        assert all(item.necessary for item in removals)
        assert all(item.necessity_residual > 0.0 for item in removals)


def test_scale_normalized_law_is_not_a_product_carrier():
    contract = next(item for item in contracts() if str(item.complex_id) == "scale_normalized_dfi_homogeneity_invariant")
    output = contract.operator(DFIRescalingInput(DATA, 3.0, 41.0))

    assert output.first is not output.second
    assert output.rescaling_residual <= 1e-12
    assert output.interaction_energy > 0.0
