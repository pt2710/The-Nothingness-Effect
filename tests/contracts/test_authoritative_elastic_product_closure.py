from __future__ import annotations

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.exact_product_carrier import (
    ExactProductInput,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus
from the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.authoritative_product_contracts import (
    SOURCE_IDS as ELASTIC_SOURCES,
    contracts as elastic_contracts,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.contracts import (
    ElasticPiInput,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi_norm.authoritative_product_contracts import (
    SOURCE_IDS as NORM_SOURCES,
    contracts as norm_contracts,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi_norm.contracts import (
    ElasticPiNormInput,
)


def _contract(factory, identifier):
    return {str(item.complex_id): item for item in factory()}[identifier]


def _elastic_value():
    return ElasticPiInput(
        entropy=np.array([0.2, 0.7, 1.8, 3.4, 5.5]),
        K_D=2.5,
        coordinates=np.linspace(0.0, 1.0, 5),
        tolerance=1e-10,
    )


def _norm_value():
    return ElasticPiNormInput(
        trajectory=np.array([1, 3, 8, 5, 12]),
        entropy=np.array([0.2, 0.7, 1.6, 2.1, 3.4]),
        K_D=4.0,
        anchored=False,
        tolerance=1e-10,
    )


def test_elastic_pi_c01_is_exactly_closed():
    contract = _contract(elastic_contracts, "spatial_reciprocal_curvature_validation_closure")
    evaluation = evaluate_contract(contract, _elastic_value())

    assert contract.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.output.source_ids == ELASTIC_SOURCES
    assert evaluation.output.first_projection_residuals == (0.0, 0.0)
    assert evaluation.output.second_projection_residuals == (0.0, 0.0)
    assert evaluation.output.exchange_square_residual == 0.0


def test_elastic_pi_norm_c01_is_exactly_closed():
    contract = _contract(norm_contracts, "spatial_weighted_calibration_closure")
    evaluation = evaluate_contract(contract, _norm_value())

    assert contract.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.output.source_ids == NORM_SOURCES
    assert evaluation.output.first_product_residual == 0.0
    assert evaluation.output.second_product_residual == 0.0
    assert evaluation.output.exchange_square_residual == 0.0


def test_elastic_product_nonzero_source_residual_remains_open():
    value = ExactProductInput(
        first_states={
            ELASTIC_SOURCES[0]: np.array([1.0]),
            ELASTIC_SOURCES[1]: np.array([2.0]),
        },
        second_states={
            ELASTIC_SOURCES[0]: np.array([3.0]),
            ELASTIC_SOURCES[1]: np.array([4.0]),
        },
        first_residuals={
            ELASTIC_SOURCES[0]: 0.0,
            ELASTIC_SOURCES[1]: 1e-4,
        },
        second_residuals={source_id: 0.0 for source_id in ELASTIC_SOURCES},
        tolerance=1e-10,
    )
    evaluation = evaluate_contract(
        _contract(elastic_contracts, "spatial_reciprocal_curvature_validation_closure"),
        value,
    )

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.first_product_residual == 1e-4
    assert evaluation.output.exchange_square_residual == 0.0


def test_elastic_product_sources_are_individually_necessary():
    elastic = _contract(elastic_contracts, "spatial_reciprocal_curvature_validation_closure")
    norm = _contract(norm_contracts, "spatial_weighted_calibration_closure")
    removals = [
        *(check(_elastic_value()) for check in elastic.source_removal_checks),
        *(check(_norm_value()) for check in norm.source_removal_checks),
    ]

    assert len(removals) == 4
    assert all(item.necessary for item in removals)
    assert all(item.necessity_residual > 0.0 for item in removals)
