from __future__ import annotations

import math

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime import NonFiniteValueError, ResidualResult, ClosureStatus
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import ensure_finite, evaluate_exponential


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, np.array([1.0, np.nan])])
def test_nonfinite_values_raise_instead_of_becoming_neutral(value):
    with pytest.raises(NonFiniteValueError):
        ensure_finite(value)


def test_nonfinite_residual_is_rejected():
    with pytest.raises(NonFiniteValueError):
        ResidualResult(
            name="bad",
            vector=(math.inf,),
            tolerance=1e-8,
            passed=False,
            status=ClosureStatus.SINGULAR,
        )


def test_clipped_exponential_records_approximation_metadata():
    result = evaluate_exponential(-1000.0, clip=50.0)
    assert result.clipped is True
    assert result.exact_exponent == -1000.0
    assert result.evaluated_exponent == -50.0
    assert result.approximation_metadata["clipped"] is True
