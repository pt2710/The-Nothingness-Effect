"""Fail-closed numerical and domain validation helpers."""

from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Number
from typing import Any, Iterable

import numpy as np

from .types import NonFiniteValueError


def ensure_finite(value: Any, *, name: str = "value") -> Any:
    """Return *value* if finite, otherwise raise without coercion."""

    if isinstance(value, Number):
        if isinstance(value, complex):
            finite = math.isfinite(value.real) and math.isfinite(value.imag)
        else:
            finite = math.isfinite(float(value))
        if not finite:
            raise NonFiniteValueError(f"{name} contains NaN or infinity")
        return value
    array = np.asarray(value)
    if not np.all(np.isfinite(array)):
        raise NonFiniteValueError(f"{name} contains NaN or infinity")
    return value


def finite_vector(values: Iterable[float], *, name: str = "residual") -> tuple[float, ...]:
    result = tuple(float(item) for item in values)
    ensure_finite(result, name=name)
    return result


@dataclass(frozen=True)
class ExponentialEvaluation:
    value: float
    exact_exponent: float
    evaluated_exponent: float
    clipped: bool
    approximation_metadata: dict[str, float | bool]


def evaluate_exponential(exponent: float, *, clip: float | None = None) -> ExponentialEvaluation:
    """Evaluate an exponential and report clipping as approximation metadata."""

    ensure_finite(exponent, name="exponent")
    evaluated = float(exponent)
    clipped = False
    if clip is not None:
        if not math.isfinite(clip) or clip <= 0:
            raise ValueError("clip must be finite and positive")
        bounded = min(max(evaluated, -clip), clip)
        clipped = bounded != evaluated
        evaluated = bounded
    try:
        value = math.exp(evaluated)
    except OverflowError as exc:
        raise NonFiniteValueError("exponential overflow") from exc
    ensure_finite(value, name="exponential result")
    return ExponentialEvaluation(
        value=value,
        exact_exponent=float(exponent),
        evaluated_exponent=evaluated,
        clipped=clipped,
        approximation_metadata={
            "clipped": clipped,
            "exact_exponent": float(exponent),
            "evaluated_exponent": evaluated,
        },
    )
