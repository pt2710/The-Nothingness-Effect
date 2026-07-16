"""Contract gates for recertified DFI A05--A07 and validation B03."""

from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ClosureStatus,
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import (
    AdditiveDerivationInput,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.derived_contracts import (
    contracts,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.dfi import (
    normalized_dfi,
    require_finite_dfi,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.extended_contracts import (
    DFIDecompositionCertificate,
    DFIDecompositionInput,
    DFIFlowpointInterfaceCertificate,
    DFIFlowpointInterfaceInput,
    DFISimulationCertificate,
    DFISimulationInput,
)


DATA = np.array(
    [
        [1.0, 2.0, 4.0],
        [2.0, 5.0, 3.0],
        [4.0, 3.0, 6.0],
        [3.0, 7.0, 5.0],
    ]
)
SCALE = 12.0
SWAP = np.array(
    [
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0],
    ]
)


def _canonical_entropy() -> np.ndarray:
    result = require_finite_dfi(normalized_dfi(DATA, spectrum_scale=SCALE))
    return np.asarray(result.normalized_entropy, dtype=float)


def test_dfi_a05_decomposition_and_mapping_covariance():
    contract = contracts()[0]
    evaluation = evaluate_contract(
        contract,
        DFIDecompositionInput(DATA, SCALE, (2, 0, 1)),
    )

    assert evaluation.status is ClosureStatus.SATISFIED
    assert isinstance(evaluation.output, DFIDecompositionCertificate)
    assert evaluation.output.component_assignment_residual <= 1e-10
    assert evaluation.output.additive_total_residual <= 1e-10
    assert evaluation.output.permutation_covariance_residual <= 1e-10
    assert evaluation.output.reproducibility_residual <= 1e-10


def test_dfi_a05_rejects_nonpermutation_mapping():
    with pytest.raises(DomainViolationError, match="each feature index"):
        evaluate_contract(
            contracts()[0],
            DFIDecompositionInput(DATA, SCALE, (0, 0, 2)),
        )


def test_dfi_a06_flowpoint_interface_commutes_for_involutive_swap():
    contract = contracts()[1]
    evaluation = evaluate_contract(
        contract,
        DFIFlowpointInterfaceInput(DATA, SCALE, SWAP),
    )

    assert evaluation.status is ClosureStatus.SATISFIED
    assert isinstance(evaluation.output, DFIFlowpointInterfaceCertificate)
    assert evaluation.output.involution_residual <= 1e-10
    assert evaluation.output.component_consistency_residual <= 1e-10
    assert evaluation.output.total_consistency_residual <= 1e-10
    assert evaluation.output.commuting_diagram_residual <= 1e-10


def test_dfi_a06_noninvolutive_interface_fails_closed():
    cycle = np.array(
        [
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0],
        ]
    )
    evaluation = evaluate_contract(
        contracts()[1],
        DFIFlowpointInterfaceInput(DATA, SCALE, cycle),
    )

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.involution_residual > 0.0


def test_dfi_a07_exact_simulation_record_is_satisfied():
    expected = _canonical_entropy()
    evaluation = evaluate_contract(
        contracts()[2],
        DFISimulationInput(DATA, SCALE, expected),
    )

    assert evaluation.status is ClosureStatus.SATISFIED
    assert isinstance(evaluation.output, DFISimulationCertificate)
    assert not evaluation.output.breakdown_detected
    assert evaluation.output.component_residual <= 1e-10
    assert evaluation.output.total_residual <= 1e-10


def test_dfi_a07_perturbed_simulation_exposes_breakdown():
    perturbed = _canonical_entropy().copy()
    perturbed[0, 0] += 0.05
    evaluation = evaluate_contract(
        contracts()[2],
        DFISimulationInput(DATA, SCALE, perturbed),
    )

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.breakdown_detected
    assert evaluation.output.maximum_absolute_error == pytest.approx(0.05)


def test_dfi_b03_requires_all_three_recertified_sources():
    contract = contracts()[3]
    source = AdditiveDerivationInput(
        {
            "dfi_uniqueness_of_decomposition_and_mapping_ambiguity": np.array(
                [1.0, 0.5, 0.25]
            ),
            "dfi_flowpoint_consistency_and_interface_inconsistency": np.array(
                [0.2, 0.4, 0.8]
            ),
            "dfi_simulation_consistency_and_simulation_breakdown": np.array(
                [0.3, 0.6, 0.9]
            ),
        }
    )
    evaluation = evaluate_contract(contract, source)
    removals = tuple(check(source) for check in contract.source_removal_checks)

    assert evaluation.status is ClosureStatus.SATISFIED
    assert evaluation.output.non_cancellation_margin > 0.0
    assert len(removals) == 3
    assert all(item.necessary for item in removals)
    assert {
        str(item.source_id) for item in removals
    } == {
        "dfi_uniqueness_of_decomposition_and_mapping_ambiguity",
        "dfi_flowpoint_consistency_and_interface_inconsistency",
        "dfi_simulation_consistency_and_simulation_breakdown",
    }
