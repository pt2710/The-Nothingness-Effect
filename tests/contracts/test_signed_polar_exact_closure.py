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
from the_nothingness_effect.mathematical_architecture.c_level import (
    C_ID,
    SignedPolarFieldInput,
    contracts,
)


def _contract():
    return {str(item.complex_id): item for item in contracts()}[C_ID]


def _value(radius: float = 2.0) -> SignedPolarFieldInput:
    return SignedPolarFieldInput(
        radius=radius,
        phase_unit=np.exp(0.4j),
        order=32,
        damping=(),
        times=(0.0, 0.2, 0.5, 0.8, 1.0),
        horizon=1.0,
    )


def test_signed_polar_maps_are_exact_mutual_inverses():
    contract = _contract()
    evaluation = evaluate_contract(contract, _value())

    assert contract.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.residual is not None and evaluation.residual.passed
    assert evaluation.output.closure_status == "closed"
    assert evaluation.output.quotient_reconstruction_residual == pytest.approx(0.0)
    assert evaluation.output.field_inverse_residual == pytest.approx(0.0)
    assert evaluation.output.authority_certificate.gauge_residual == pytest.approx(0.0)
    assert evaluation.output.authority_certificate.norm_residual < 1e-12


def test_negative_radius_uses_the_signed_polar_gauge_without_loss():
    positive = evaluate_contract(_contract(), _value(2.0)).output
    negative = evaluate_contract(_contract(), _value(-2.0)).output

    assert negative.canonical_radius == pytest.approx(positive.canonical_radius)
    assert negative.canonical_phase_unit == pytest.approx(-positive.canonical_phase_unit)
    assert negative.closure_status == "closed"
    assert negative.quotient_reconstruction_residual == pytest.approx(0.0)


def test_zero_radius_has_one_canonical_phase_and_closes():
    evaluation = evaluate_contract(_contract(), _value(0.0))

    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.output.canonical_radius == pytest.approx(0.0)
    assert evaluation.output.canonical_phase_unit == pytest.approx(1.0 + 0.0j)
    np.testing.assert_allclose(evaluation.output.field, 0.0)


def test_missing_zero_time_anchor_is_rejected():
    value = SignedPolarFieldInput(
        radius=2.0,
        phase_unit=1.0 + 0.0j,
        order=16,
        damping=(),
        times=(0.1, 0.5, 1.0),
        horizon=1.0,
    )

    with pytest.raises(DomainViolationError, match="first sample at t=0"):
        evaluate_contract(_contract(), value)


def test_both_mathematical_b_sources_are_necessary():
    contract = _contract()
    removals = tuple(check(_value()) for check in contract.source_removal_checks)

    assert len(removals) == 2
    assert all(item.necessary for item in removals)
    assert all(item.necessity_residual > 0.0 for item in removals)
