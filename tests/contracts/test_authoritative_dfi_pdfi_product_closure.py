from __future__ import annotations

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.exact_product_carrier import (
    ExactProductInput,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.authoritative_product_contracts import (
    A03,
    A04,
    B01,
    B02,
    B03,
    C01,
    contracts as dfi_contracts,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.contracts import (
    ApplicabilityInput,
    SpatialDFIInput,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.authoritative_product_contracts import (
    SOURCE_IDS as PDFI_SOURCES,
    contracts as pdfi_contracts,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.contracts import (
    ParityDFIInput,
)


def _contract(factory, identifier):
    return {str(item.complex_id): item for item in factory()}[identifier]


def _dfi_data():
    return np.array(
        [
            [1.0, 2.0, 4.0],
            [2.0, 3.0, 5.0],
            [3.0, 5.0, 8.0],
            [5.0, 8.0, 13.0],
        ]
    )


def test_dfi_b02_legacy_realization_satisfies_product_projections():
    evaluation = evaluate_contract(
        _contract(dfi_contracts, B02),
        ApplicabilityInput(_dfi_data(), 7.0, 1e-10),
    )

    assert evaluation.status is ClosureStatus.SATISFIED
    assert evaluation.residual is not None and evaluation.residual.passed
    assert evaluation.output.source_ids == (A03, A04)
    assert evaluation.output.first_projection_residuals == (0.0, 0.0)
    assert evaluation.output.second_projection_residuals == (0.0, 0.0)
    assert evaluation.output.exchange_square_residual == 0.0


def test_dfi_c01_legacy_realization_is_exactly_closed():
    contract = _contract(dfi_contracts, C01)
    evaluation = evaluate_contract(
        contract,
        SpatialDFIInput(_dfi_data(), 7.0, tolerance=1e-10, validation_weight=1.0),
    )

    assert contract.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.output.source_ids == (B01, B02, B03)
    assert evaluation.output.first_product_residual == 0.0
    assert evaluation.output.second_product_residual == 0.0
    assert evaluation.output.exchange_square_residual == 0.0


def test_pdfi_c01_legacy_realization_is_exactly_closed():
    contract = _contract(pdfi_contracts, "spatial_parity_elastic_calibration_closure")
    evaluation = evaluate_contract(
        contract,
        ParityDFIInput(
            np.array([7, 22, 11, 34, 17, 52]),
            response_seed=2.5,
            K_D=100.0,
            tolerance=1e-10,
        ),
    )

    assert contract.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.output.source_ids == PDFI_SOURCES
    assert evaluation.output.exchange_square_residual == 0.0
    assert evaluation.residual is not None and evaluation.residual.passed


def test_product_source_residual_is_localized_and_keeps_contract_open():
    value = ExactProductInput(
        first_states={A03: np.array([1.0]), A04: np.array([2.0])},
        second_states={A03: np.array([3.0]), A04: np.array([4.0])},
        first_residuals={A03: 0.0, A04: 1e-3},
        second_residuals={A03: 0.0, A04: 0.0},
        tolerance=1e-10,
    )
    evaluation = evaluate_contract(_contract(dfi_contracts, B02), value)

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.residual is not None and not evaluation.residual.passed
    assert evaluation.output.first_product_residual == 1e-3
    assert evaluation.output.second_product_residual == 0.0
    assert evaluation.output.first_projection_residuals == (0.0, 0.0)


def test_dfi_and_pdfi_product_sources_are_individually_necessary():
    dfi_b02 = _contract(dfi_contracts, B02)
    dfi_c01 = _contract(dfi_contracts, C01)
    pdfi_c01 = _contract(pdfi_contracts, "spatial_parity_elastic_calibration_closure")

    dfi_value = ApplicabilityInput(_dfi_data(), 7.0, 1e-10)
    dfi_spatial = SpatialDFIInput(_dfi_data(), 7.0)
    pdfi_value = ParityDFIInput(np.array([7, 22, 11, 34, 17, 52]), 2.5, 100.0)

    removals = [
        *(check(dfi_value) for check in dfi_b02.source_removal_checks),
        *(check(dfi_spatial) for check in dfi_c01.source_removal_checks),
        *(check(pdfi_value) for check in pdfi_c01.source_removal_checks),
    ]
    assert len(removals) == 8
    assert all(item.necessary for item in removals)
    assert all(item.necessity_residual > 0.0 for item in removals)
