from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    ClosureStatus,
    DomainViolationError,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_artifacts import fixture
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature.memory_tomography_contract import (
    MemoryTomographyInput,
    contract,
    memory_tomography_operator,
)


def test_gauge_fixed_memory_tomography_is_injective_and_closed():
    theorem = contract()
    evaluation = evaluate_contract(theorem, fixture())

    assert theorem.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.residual is not None and evaluation.residual.passed
    assert evaluation.output.closure_status == "closed"
    assert evaluation.output.phase_lower_bound > 0.0
    assert evaluation.output.memory_lower_bound > 0.0
    assert evaluation.output.composite_lower_bound + 1e-12 >= evaluation.output.product_lower_bound
    assert evaluation.output.fibre_dimension == 0
    assert evaluation.output.field_reconstruction_residual < 1e-10
    assert evaluation.output.curvature_reconstruction_residual < 1e-10
    assert evaluation.output.horizon_reconstruction_residual < 1e-10


def test_corrupted_tomography_output_remains_open():
    base = fixture()
    exact = memory_tomography_operator(base)
    corrupted = exact.tomography.copy()
    corrupted[corrupted.size // 2] += 0.5
    value = MemoryTomographyInput(
        coordinates=base.coordinates,
        elastic_field=base.source,
        elliptic_strength=1.0 / base.scale,
        memory_decay=base.scale,
        tomography=corrupted,
        tolerance=1e-10,
    )
    evaluation = evaluate_contract(contract(), value)

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.field_reconstruction_residual > 0.0
    assert evaluation.residual is not None and not evaluation.residual.passed


def test_unfixed_gauge_or_initial_mode_is_rejected():
    base = fixture()
    with pytest.raises(DomainViolationError, match="fixed elliptic gauge"):
        evaluate_contract(
            contract(),
            MemoryTomographyInput(
                coordinates=base.coordinates,
                elastic_field=base.source,
                gauge_fixed=False,
            ),
        )
    with pytest.raises(DomainViolationError, match="temporal initial mode"):
        evaluate_contract(
            contract(),
            MemoryTomographyInput(
                coordinates=base.coordinates,
                elastic_field=base.source,
                initial_mode_fixed=False,
            ),
        )


def test_both_edi_b_sources_are_necessary():
    theorem = contract()
    removals = tuple(check(fixture()) for check in theorem.source_removal_checks)

    assert len(removals) == 2
    assert all(item.necessary for item in removals)
    assert all(item.necessity_residual > 0.0 for item in removals)


def test_composite_matrix_equals_ordered_derivative_product():
    output = memory_tomography_operator(fixture())
    np.testing.assert_allclose(
        output.composite_matrix,
        output.memory_horizon_matrix @ output.phase_elliptic_matrix,
        atol=1e-12,
    )
    assert output.chain_rule_residual == pytest.approx(0.0)
