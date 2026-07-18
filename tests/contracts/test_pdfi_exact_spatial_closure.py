from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    ClosureStatus,
    DomainViolationError,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.closure_contracts import (
    ExactSpatialParityInput,
    SOURCE_IDS,
    contracts,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.contracts import (
    ParityDFIInput,
)


def _contract():
    return {
        str(item.complex_id): item for item in contracts()
    }["spatial_parity_elastic_calibration_closure"]


def _zero_input() -> ExactSpatialParityInput:
    fields = {source: np.zeros(6, dtype=float) for source in SOURCE_IDS}
    weights = {source: float(index + 1) for index, source in enumerate(SOURCE_IDS)}
    return ExactSpatialParityInput(
        source_energy_fields_1b=fields,
        source_energy_fields_2b={source: field.copy() for source, field in fields.items()},
        source_weights_1b=weights,
        source_weights_2b=dict(weights),
        spatial_reflection=(5, 4, 3, 2, 1, 0),
        source_exchange=(1, 0, 2),
        grid_spacing=0.2,
        tolerance=1e-12,
    )


def test_exact_pdfi_zero_set_closes():
    contract = _contract()
    evaluation = evaluate_contract(contract, _zero_input())

    assert contract.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.residual is not None and evaluation.residual.passed
    assert evaluation.output.joint_energy == pytest.approx(0.0)
    assert evaluation.output.closure_status == "closed"


def test_legacy_pdfi_fixture_closes_when_all_three_b_residuals_vanish():
    value = ParityDFIInput(
        np.array([7, 22, 11, 34, 17, 52]),
        response_seed=2.5,
        K_D=100.0,
        tolerance=1e-10,
    )
    evaluation = evaluate_contract(_contract(), value)

    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.output.joint_energy <= value.tolerance
    assert evaluation.output.exchange_involution_residual == pytest.approx(0.0)


def test_nonzero_pdfi_source_defect_cannot_cancel_spatially():
    value = _zero_input()
    fields = {
        source: field.copy() for source, field in value.source_energy_fields_2b.items()
    }
    fields[SOURCE_IDS[2]] = np.array([0.0, 1.0, 0.0, 1.0, 0.0, 1.0])
    perturbed = ExactSpatialParityInput(
        source_energy_fields_1b=value.source_energy_fields_1b,
        source_energy_fields_2b=fields,
        source_weights_1b=value.source_weights_1b,
        source_weights_2b=value.source_weights_2b,
        spatial_reflection=value.spatial_reflection,
        source_exchange=value.source_exchange,
        grid_spacing=value.grid_spacing,
        tolerance=value.tolerance,
    )
    evaluation = evaluate_contract(_contract(), perturbed)

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.residual is not None and evaluation.residual.passed
    assert evaluation.output.volume_energy_2b > 0.0
    assert evaluation.output.gradient_energy_2b > 0.0
    assert evaluation.output.boundary_energy_2b > 0.0
    assert evaluation.output.joint_energy > 0.0


def test_each_pdfi_b_source_is_individually_necessary():
    contract = _contract()
    removals = tuple(check(_zero_input()) for check in contract.source_removal_checks)

    assert len(removals) == 3
    assert {str(item.source_id) for item in removals} == set(SOURCE_IDS)
    assert all(item.necessary for item in removals)
    assert all(item.baseline_response > item.removed_response for item in removals)


def test_pdfi_requires_positive_source_weights():
    value = _zero_input()
    invalid_weights = dict(value.source_weights_2b)
    invalid_weights[SOURCE_IDS[1]] = -1.0
    invalid = ExactSpatialParityInput(
        source_energy_fields_1b=value.source_energy_fields_1b,
        source_energy_fields_2b=value.source_energy_fields_2b,
        source_weights_1b=value.source_weights_1b,
        source_weights_2b=invalid_weights,
        spatial_reflection=value.spatial_reflection,
        source_exchange=value.source_exchange,
    )

    with pytest.raises(DomainViolationError, match="strictly positive"):
        evaluate_contract(_contract(), invalid)


def test_pdfi_rejects_noninvolutive_source_exchange():
    value = _zero_input()
    invalid = ExactSpatialParityInput(
        source_energy_fields_1b=value.source_energy_fields_1b,
        source_energy_fields_2b=value.source_energy_fields_2b,
        source_weights_1b=value.source_weights_1b,
        source_weights_2b=value.source_weights_2b,
        spatial_reflection=value.spatial_reflection,
        source_exchange=(1, 2, 0),
    )

    with pytest.raises(DomainViolationError, match="involutive"):
        evaluate_contract(_contract(), invalid)
