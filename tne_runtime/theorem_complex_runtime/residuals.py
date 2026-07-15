"""Constructors for finite, typed theorem residuals."""

from __future__ import annotations

from collections.abc import Iterable

from .types import ClosureStatus, ResidualResult
from .validation import finite_vector


def residual_result(
    name: str,
    values: Iterable[float],
    *,
    tolerance: float,
    closed_status: ClosureStatus = ClosureStatus.SATISFIED,
    open_status: ClosureStatus = ClosureStatus.OPEN,
) -> ResidualResult:
    vector = finite_vector(values, name=name)
    norm_squared = sum(value * value for value in vector)
    passed = norm_squared <= tolerance * tolerance
    return ResidualResult(
        name=name,
        vector=vector,
        tolerance=float(tolerance),
        passed=passed,
        status=closed_status if passed else open_status,
    )


def singular_residual(name: str, *, reason: str, tolerance: float = 0.0) -> ResidualResult:
    return ResidualResult(
        name=name,
        vector=(),
        tolerance=tolerance,
        passed=False,
        status=ClosureStatus.SINGULAR,
        metadata={"reason": reason},
    )
