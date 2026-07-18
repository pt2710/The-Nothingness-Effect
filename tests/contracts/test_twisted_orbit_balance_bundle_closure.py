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
from the_nothingness_effect.foundational_architecture.spatiality.derived_contracts import (
    CHORD_SOURCE,
    C_ID,
    PHASE_SOURCE,
    TwistedOrbitBalanceInput,
    contracts,
)


def _contract():
    return {str(item.complex_id): item for item in contracts()}[C_ID]


def _value() -> TwistedOrbitBalanceInput:
    representatives = np.array(((2.0, 1.0), (4.0, -2.0), (1.0, 3.0)))
    opposite = np.array(((-2.0, 3.0), (0.0, 2.0), (5.0, -1.0)))
    displacement = np.array(((0.5, -1.0), (2.0, 0.25), (-0.75, 1.5)))
    return TwistedOrbitBalanceInput(
        representatives=representatives,
        opposite_representatives=opposite,
        displacements=displacement,
        opposite_displacements=-displacement,
        center=np.array((3.0, -2.0)),
        linear_map=np.array(((2.0, 0.5), (-1.0, 3.0), (0.25, -0.5))),
        tolerance=1e-12,
    )


def test_twisted_bundle_descent_and_reconstruction_are_mutual_inverses():
    contract = _contract()
    evaluation = evaluate_contract(contract, _value())

    assert contract.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.residual is not None and evaluation.residual.passed
    assert evaluation.output.closure_status == "closed"
    assert evaluation.output.anti_invariance_residual == pytest.approx(0.0)
    assert evaluation.output.gluing_residual == pytest.approx(0.0)
    assert evaluation.output.balance_fiber_residual == pytest.approx(0.0)
    assert evaluation.output.descent_reconstruction_residual == pytest.approx(0.0)
    assert evaluation.output.reconstruction_descent_residual == pytest.approx(0.0)
    assert evaluation.output.fiber_coordinate_uniqueness_residual == pytest.approx(0.0)
    assert evaluation.output.swap_naturality_residual == pytest.approx(0.0)
    assert evaluation.output.compensation_naturality_residual == pytest.approx(0.0)
    np.testing.assert_allclose(
        evaluation.output.reconstructed_displacements,
        _value().displacements,
    )


def test_broken_anti_invariance_prevents_false_closure():
    value = _value()
    broken = TwistedOrbitBalanceInput(
        representatives=value.representatives,
        opposite_representatives=value.opposite_representatives,
        displacements=value.displacements,
        opposite_displacements=value.opposite_displacements + 0.1,
        center=value.center,
        linear_map=value.linear_map,
        tolerance=value.tolerance,
    )
    evaluation = evaluate_contract(_contract(), broken)

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.anti_invariance_residual > 0.0
    assert evaluation.output.gluing_residual > 0.0
    assert evaluation.residual is not None and not evaluation.residual.passed


def test_provenance_spatial_input_adapts_to_exact_bundle_law():
    phase = np.arange(24.0).reshape(6, 4) + 1.0
    chord = np.arange(24.0).reshape(6, 4) + 2.0
    value = SpatialClosureInput(
        {
            PHASE_SOURCE: phase,
            CHORD_SOURCE: chord,
        },
        tolerance=1e-12,
    )
    evaluation = evaluate_contract(_contract(), value)

    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.output.closure_status == "closed"
    np.testing.assert_allclose(
        evaluation.output.reconstructed_displacements,
        phase,
    )


def test_both_foundational_b_sources_are_necessary():
    contract = _contract()
    removals = tuple(check(_value()) for check in contract.source_removal_checks)

    assert len(removals) == 2
    assert {str(item.source_id) for item in removals} == {
        PHASE_SOURCE,
        CHORD_SOURCE,
    }
    assert all(item.necessary for item in removals)
    assert all(item.necessity_residual > 0.0 for item in removals)
