from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_artifacts import (
    fixture,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.potential_current_contract import (
    PotentialCurrentInput,
    contract,
    potential_current_operator,
)


def test_common_potential_closes_all_three_channels_exactly():
    theorem = contract()
    evaluation = evaluate_contract(theorem, fixture())

    assert theorem.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.residual is not None and evaluation.residual.passed
    assert evaluation.output.closure_status == "closed"
    assert evaluation.output.endpoint_residual == pytest.approx(0.0)
    assert evaluation.output.current_residual == pytest.approx(0.0)
    assert evaluation.output.production_residual == pytest.approx(0.0)
    assert evaluation.output.potential_reconstruction_residual < 1e-12
    assert evaluation.output.circulation_residual < 1e-12
    assert evaluation.output.gauge_ratio_residual < 1e-12
    assert evaluation.output.gauge_current_residual < 1e-12
    assert evaluation.output.gauge_production_residual < 1e-10


def test_perturbed_current_channel_keeps_closure_open():
    base = fixture()
    exact = potential_current_operator(base)
    corrupted = exact.edge_current.copy()
    corrupted[len(corrupted) // 2] += 0.25
    value = PotentialCurrentInput(
        coordinates=base.coordinates,
        entropy_source=base.source,
        elasticity=base.scale,
        alpha=base.frequency,
        endpoint_ratio=exact.endpoint_ratio,
        edge_current=corrupted,
        production=exact.production,
        tolerance=1e-10,
    )
    evaluation = evaluate_contract(contract(), value)

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.current_residual > 0.0
    assert evaluation.output.potential_reconstruction_residual > 0.0
    assert evaluation.residual is not None and not evaluation.residual.passed


def test_potential_additive_gauge_does_not_change_retained_channels():
    output = potential_current_operator(fixture())

    assert output.gauge_ratio_residual < 1e-12
    assert output.gauge_current_residual < 1e-12
    assert output.gauge_production_residual < 1e-10
    np.testing.assert_allclose(
        np.log(output.endpoint_ratio),
        output.potential - output.potential[0],
        atol=1e-12,
    )


def test_both_dubler_b_sources_are_necessary():
    theorem = contract()
    removals = tuple(check(fixture()) for check in theorem.source_removal_checks)

    assert len(removals) == 2
    assert all(item.necessary for item in removals)
    assert all(item.necessity_residual > 0.0 for item in removals)
