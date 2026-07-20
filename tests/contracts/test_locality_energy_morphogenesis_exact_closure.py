from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_artifacts import fixture
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.morphogenesis_contract import (
    LocalityEnergyInput,
    contract,
    morphogenesis_operator,
)


def _value(morphogenesis=None, *, locality_residual=0.0):
    coordinates = np.linspace(0.0, 1.0, 9)
    locality = 1.0 + 0.25 * np.sin(2.0 * np.pi * coordinates)
    current = 0.8 + coordinates**2
    return LocalityEnergyInput(
        coordinates=coordinates,
        locality_field=locality,
        energy_current=current,
        morphogenesis=morphogenesis,
        locality_source_residual=locality_residual,
        tolerance=1e-10,
    )


def test_staggered_product_rule_closes_exactly():
    theorem = contract()
    evaluation = evaluate_contract(theorem, _value())

    assert theorem.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.residual is not None and evaluation.residual.passed
    assert evaluation.output.closure_status == "closed"
    assert evaluation.output.interaction_identity_residual < 1e-12
    assert evaluation.output.supplied_channel_residual == pytest.approx(0.0)
    assert evaluation.output.stability_bound_residual == pytest.approx(0.0)
    np.testing.assert_allclose(
        evaluation.output.flux_divergence,
        evaluation.output.product_rule_expansion,
        atol=1e-12,
    )


def test_corrupted_morphogenesis_channel_remains_open():
    exact = morphogenesis_operator(_value())
    corrupted = exact.local_operator.copy()
    corrupted[corrupted.size // 2] += 0.4
    evaluation = evaluate_contract(
        contract(),
        _value(morphogenesis=corrupted),
    )

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.supplied_channel_residual > 0.0
    assert evaluation.residual is not None and not evaluation.residual.passed


def test_upstream_locality_defect_is_not_hidden_by_exact_terminal_fit():
    exact = morphogenesis_operator(_value())
    evaluation = evaluate_contract(
        contract(),
        _value(
            morphogenesis=exact.local_operator,
            locality_residual=1e-3,
        ),
    )

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.interaction_identity_residual < 1e-12
    assert evaluation.output.locality_source_residual == pytest.approx(1e-3)


def test_generic_physical_fixture_adapts_to_exact_morphogenesis_law():
    evaluation = evaluate_contract(contract(), fixture())

    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.output.interaction_identity_residual < 1e-10
    assert evaluation.output.locality_source_residual < 1e-10
    assert evaluation.output.energy_source_residual < 1e-10


def test_both_locality_energy_sources_are_necessary():
    theorem = contract()
    removals = tuple(check(_value()) for check in theorem.source_removal_checks)

    assert len(removals) == 2
    assert all(item.necessary for item in removals)
    assert all(item.necessity_residual > 0.0 for item in removals)
