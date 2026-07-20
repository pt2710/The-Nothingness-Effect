from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import (
    SpatialClosureInput,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature.derived_contracts import (
    BARRIER_ID,
    C_ID,
    STABILITY_ID,
    RegularizedGeometryInput,
    contracts,
    regularized_geometry_operator,
)


def _contract():
    return {str(item.complex_id): item for item in contracts()}[C_ID]


def _value(candidate=None, *, stability_identifiable=True):
    geometry = np.array(
        (
            (1.0, 0.2, 0.0),
            (0.0, 1.0, 0.3),
            (0.1, 0.0, 1.0),
        )
    )
    observation = np.array(
        (
            (1.0, 0.0, 0.2),
            (0.1, 1.0, 0.0),
            (0.0, 0.2, 1.0),
        )
    )
    return RegularizedGeometryInput(
        observation_matrix=observation,
        geometry_matrix=geometry,
        observed_data=np.array((1.5, -0.25, 0.8)),
        barrier_matrix=np.diag((0.5, 0.75, 1.0)),
        dynamic_matrix=np.array(
            (
                (1.0, -1.0, 0.0),
                (0.0, 1.0, -1.0),
                (0.25, 0.0, 0.5),
            )
        ),
        barrier_weight=0.6,
        dynamic_weight=0.4,
        candidate=candidate,
        stability_identifiable=stability_identifiable,
        tolerance=1e-10,
    )


def test_regularized_geometry_minimum_is_attained_unique_and_stable():
    theorem = _contract()
    evaluation = evaluate_contract(theorem, _value())

    assert theorem.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.residual is not None and evaluation.residual.passed
    assert evaluation.output.closure_status == "closed"
    assert evaluation.output.stationarity_residual < 1e-10
    assert evaluation.output.attainment_residual < 1e-10
    assert evaluation.output.coercivity_margin > 0.0
    assert evaluation.output.convexity_margin > 0.0
    assert evaluation.output.identifying_singular_value > 0.0
    assert evaluation.output.stability_constant > 0.0
    assert evaluation.output.geometry_perturbation_norm <= (
        evaluation.output.stability_constant
        * evaluation.output.perturbation_norm
        + 1e-12
    )


def test_nonoptimal_supplied_candidate_is_not_falsely_closed():
    candidate = np.array((10.0, -4.0, 3.0))
    evaluation = evaluate_contract(_contract(), _value(candidate=candidate))

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.candidate_optimality_residual > 0.0
    assert evaluation.residual is not None and not evaluation.residual.passed


def test_nonidentifying_b_status_keeps_variational_status_defective():
    evaluation = evaluate_contract(
        _contract(),
        _value(stability_identifiable=False),
    )

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.nonidentifying_defect == pytest.approx(1.0)
    assert evaluation.output.stability_source_residual == pytest.approx(1.0)
    assert evaluation.output.closure_status == "open"


def test_provenance_spatial_input_adapts_to_attained_quadratic_inverse():
    barrier = np.arange(24.0).reshape(6, 4) + 1.0
    stability = np.arange(24.0).reshape(6, 4) + 2.0
    evaluation = evaluate_contract(
        _contract(),
        SpatialClosureInput(
            {
                BARRIER_ID: barrier,
                STABILITY_ID: stability,
            },
            tolerance=1e-10,
        ),
    )

    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.output.stationarity_residual < 1e-10
    assert evaluation.output.coercivity_margin > 0.0


def test_exact_minimizer_can_be_recertified_as_supplied_candidate():
    minimizer = regularized_geometry_operator(_value()).minimizer
    evaluation = evaluate_contract(_contract(), _value(candidate=minimizer))

    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.output.candidate_optimality_residual < 1e-10


def test_both_edi_regularization_sources_are_necessary():
    theorem = _contract()
    removals = tuple(check(_value()) for check in theorem.source_removal_checks)

    assert len(removals) == 2
    assert {str(item.source_id) for item in removals} == {
        BARRIER_ID,
        STABILITY_ID,
    }
    assert all(item.necessary for item in removals)
    assert all(item.necessity_residual > 0.0 for item in removals)
