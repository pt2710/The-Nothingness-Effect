from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_artifacts import fixture
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.horizon_geometry_contract import (
    HorizonGeometryInput,
    contract,
    horizon_geometry_operator,
)


def _value(mapped_normals=None):
    angles = np.linspace(0.0, 2.0 * np.pi, 12, endpoint=False)
    points = np.column_stack((np.cos(angles), np.sin(angles)))
    normals = points.copy()
    angle = 0.35
    matrix = np.array(
        (
            (np.cos(angle), -np.sin(angle)),
            (np.sin(angle), np.cos(angle)),
        )
    )
    mapped = points @ matrix.T
    entropy = np.sum(points * points, axis=1)
    mapped_entropy = np.sum(mapped * mapped, axis=1)
    return HorizonGeometryInput(
        horizon_points=points,
        horizon_normals=normals,
        translation_matrix=matrix,
        translation_vector=np.zeros(2),
        entropy_values=entropy,
        mapped_entropy_values=mapped_entropy,
        horizon_level_values=entropy - 1.0,
        mapped_horizon_level_values=mapped_entropy - 1.0,
        mapped_normals=mapped_normals,
        tolerance=1e-10,
    )


def test_regular_horizon_restriction_and_normal_transport_close():
    theorem = contract()
    evaluation = evaluate_contract(theorem, _value())

    assert theorem.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.residual is not None and evaluation.residual.passed
    assert evaluation.output.closure_status == "closed"
    assert evaluation.output.map_residual == pytest.approx(0.0)
    assert evaluation.output.inverse_map_residual < 1e-12
    assert evaluation.output.entropy_invariance_residual < 1e-12
    assert evaluation.output.horizon_invariance_residual < 1e-12
    assert evaluation.output.normal_transport_residual == pytest.approx(0.0)
    assert evaluation.output.normal_unit_residual < 1e-12
    assert evaluation.output.invertibility_margin > 0.0
    assert evaluation.output.transversality_margin > 0.0
    assert evaluation.output.lip_bound_residual < 1e-12


def test_corrupted_normal_transport_remains_open():
    exact = horizon_geometry_operator(_value())
    corrupted = exact.mapped_normals.copy()
    corrupted[0] = np.array((1.0, 0.0))
    evaluation = evaluate_contract(contract(), _value(mapped_normals=corrupted))

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.normal_transport_residual > 0.0
    assert evaluation.residual is not None and not evaluation.residual.passed


def test_generic_physical_fixture_adapts_to_regular_horizon_geometry():
    evaluation = evaluate_contract(contract(), fixture())

    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.output.translation_source_residual < 1e-10
    assert evaluation.output.horizon_source_residual < 1e-10
    assert evaluation.output.invertibility_margin > 0.0


def test_both_horizon_sources_are_necessary():
    theorem = contract()
    removals = tuple(check(_value()) for check in theorem.source_removal_checks)

    assert len(removals) == 2
    assert all(item.necessary for item in removals)
    assert all(item.necessity_residual > 0.0 for item in removals)


def test_expected_normal_uses_inverse_transpose_transport():
    output = horizon_geometry_operator(_value())
    matrix = _value().translation_matrix
    expected = output.horizon_normals @ np.linalg.inv(matrix)
    expected /= np.linalg.norm(expected, axis=1)[:, None]
    np.testing.assert_allclose(output.expected_mapped_normals, expected, atol=1e-12)
