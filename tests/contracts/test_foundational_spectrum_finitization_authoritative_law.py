"""Authoritative finite checks for relative/absolute SOI finitization."""

from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import all_contracts
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
)
from the_nothingness_effect.foundational_architecture.the_spectrum_of_infinities.authoritative_finitization import (
    ScaledFinitizationInput,
)
from the_nothingness_effect.foundational_architecture.the_spectrum_of_infinities.canonical_contracts import (
    A6,
    FinitizationInput,
)


def _contract():
    return {item.complex_id: item for item in all_contracts()}[A6]


def test_finitization_preserves_exact_absolute_l1_scaling():
    contract = _contract()
    assert contract.implementation_path.endswith(
        "the_spectrum_of_infinities/authoritative_finitization.py"
    )

    target = np.asarray((1.0, 2.0))
    approximants = np.asarray(((0.0, 0.0), (0.5, 1.0), (1.0, 2.0)))
    omega = 7.0
    output = evaluate_contract(
        contract,
        ScaledFinitizationInput(target, approximants, magnitude=omega),
    ).output

    relative_errors = np.sum(np.abs(approximants - target[None, :]), axis=1)
    assert np.allclose(output.values[2], relative_errors)
    assert np.allclose(output.values[3], omega * relative_errors)
    assert output.values[4][0] == pytest.approx(omega)
    assert all(item == pytest.approx(0.0) for item in output.residuals)


def test_finitization_preserves_backward_compatible_unit_scale():
    target = np.asarray((1.0,))
    approximants = np.asarray(((0.0,), (1.0,)))
    output = evaluate_contract(
        _contract(),
        FinitizationInput(target, approximants),
    ).output
    assert output.values[4][0] == pytest.approx(1.0)
    assert np.allclose(output.values[2], output.values[3])


def test_finitization_fails_closed_on_invalid_scale_or_shape():
    with pytest.raises(DomainViolationError):
        evaluate_contract(
            _contract(),
            ScaledFinitizationInput(
                np.asarray((1.0,)),
                np.asarray(((1.0,),)),
                magnitude=0.0,
            ),
        )
    with pytest.raises(DomainViolationError):
        evaluate_contract(
            _contract(),
            ScaledFinitizationInput(
                np.asarray((1.0, 2.0)),
                np.asarray(((1.0,),)),
                magnitude=1.0,
            ),
        )
