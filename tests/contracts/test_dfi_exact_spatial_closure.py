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
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.closure_contracts import (
    ExactSpatialDFIInput,
    SOURCE_IDS,
    contracts,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.contracts import (
    SpatialDFIInput,
)


def _contract():
    return {
        str(item.complex_id): item for item in contracts()
    }["spatially_localized_dfi_consistency_closure"]


def _zero_input() -> ExactSpatialDFIInput:
    fields = {source: np.zeros(5, dtype=float) for source in SOURCE_IDS}
    weights = {source: float(index + 1) for index, source in enumerate(SOURCE_IDS)}
    return ExactSpatialDFIInput(
        source_energy_fields_1b=fields,
        source_energy_fields_2b={source: field.copy() for source, field in fields.items()},
        source_weights_1b=weights,
        source_weights_2b=dict(weights),
        spatial_reflection=(4, 3, 2, 1, 0),
        source_exchange=(1, 0, 2),
        grid_spacing=0.25,
        tolerance=1e-12,
    )


def test_exact_c01_zero_set_closes():
    contract = _contract()
    evaluation = evaluate_contract(contract, _zero_input())

    assert contract.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.residual is not None and evaluation.residual.passed
    assert evaluation.output.closure_status == "closed"
    assert evaluation.output.joint_energy == pytest.approx(0.0)
    assert evaluation.output.reference_residual_1b == pytest.approx(0.0)
    assert evaluation.output.reference_residual_2b == pytest.approx(0.0)
    assert evaluation.output.reference_residual_joint == pytest.approx(0.0)


def test_legacy_dfi_fixture_is_promoted_only_after_all_source_defects_close():
    data = np.array(
        [
            [1.0, 2.0, 4.0],
            [2.0, 3.0, 5.0],
            [3.0, 5.0, 8.0],
            [5.0, 8.0, 13.0],
        ]
    )
    evaluation = evaluate_contract(
        _contract(),
        SpatialDFIInput(data, spectrum_scale=7.0, tolerance=1e-10, validation_weight=1.0),
    )

    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.output.joint_energy <= 1e-10
    assert evaluation.output.exchange_involution_residual == pytest.approx(0.0)


def test_nonzero_source_gradient_and_boundary_defect_remain_open():
    value = _zero_input()
    fields_1b = {
        source: field.copy() for source, field in value.source_energy_fields_1b.items()
    }
    fields_1b[SOURCE_IDS[1]] = np.array([1.0, 0.0, 1.0, 0.0, 1.0])
    perturbed = ExactSpatialDFIInput(
        source_energy_fields_1b=fields_1b,
        source_energy_fields_2b=value.source_energy_fields_2b,
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
    assert evaluation.output.volume_energy_1b > 0.0
    assert evaluation.output.gradient_energy_1b > 0.0
    assert evaluation.output.boundary_energy_1b > 0.0
    assert evaluation.output.joint_energy > 0.0


def test_each_b_source_is_necessary_for_the_spatial_zero_set():
    contract = _contract()
    removals = tuple(check(_zero_input()) for check in contract.source_removal_checks)

    assert len(removals) == 3
    assert {str(item.source_id) for item in removals} == set(SOURCE_IDS)
    assert all(item.necessary for item in removals)
    assert all(item.complete_response > item.removed_response for item in removals)
    assert all(item.necessity_residual > 0.0 for item in removals)


def test_nonpositive_source_weight_is_rejected():
    value = _zero_input()
    invalid_weights = dict(value.source_weights_1b)
    invalid_weights[SOURCE_IDS[0]] = 0.0
    invalid = ExactSpatialDFIInput(
        source_energy_fields_1b=value.source_energy_fields_1b,
        source_energy_fields_2b=value.source_energy_fields_2b,
        source_weights_1b=invalid_weights,
        source_weights_2b=value.source_weights_2b,
        spatial_reflection=value.spatial_reflection,
        source_exchange=value.source_exchange,
    )

    with pytest.raises(DomainViolationError, match="strictly positive"):
        evaluate_contract(_contract(), invalid)


def test_noninvolutive_spatial_exchange_is_rejected():
    value = _zero_input()
    invalid = ExactSpatialDFIInput(
        source_energy_fields_1b=value.source_energy_fields_1b,
        source_energy_fields_2b=value.source_energy_fields_2b,
        source_weights_1b=value.source_weights_1b,
        source_weights_2b=value.source_weights_2b,
        spatial_reflection=(1, 2, 3, 4, 0),
        source_exchange=value.source_exchange,
    )

    with pytest.raises(DomainViolationError, match="involutive"):
        evaluate_contract(_contract(), invalid)
