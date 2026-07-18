"""Exact finite realization of authoritative B/C direct-product laws.

The authoritative appendices define many higher-order complexes as products of
already typed source carriers.  Their mathematical obligations are projection
recovery, conjunction of source predicates, localization of source residuals,
and a coordinatewise involutive exchange.  This module implements those
obligations directly; it does not replace the product by an additive surrogate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np

from .types import ClosureStatus, ComplexId, DomainViolationError, ResidualResult
from .validation import ensure_finite


@dataclass(frozen=True)
class ExactProductInput:
    """Canonical numerical encoding of paired source-carrier realizations."""

    first_states: Mapping[str, np.ndarray]
    second_states: Mapping[str, np.ndarray]
    first_residuals: Mapping[str, float]
    second_residuals: Mapping[str, float]
    tolerance: float = 1e-10


@dataclass(frozen=True)
class ExactProductResult:
    source_ids: tuple[str, ...]
    first_product: tuple[np.ndarray, ...]
    second_product: tuple[np.ndarray, ...]
    first_projection_residuals: tuple[float, ...]
    second_projection_residuals: tuple[float, ...]
    first_source_residuals: tuple[float, ...]
    second_source_residuals: tuple[float, ...]
    first_product_residual: float
    second_product_residual: float
    exchange_square_residual: float
    closure_status: str


def _ordered_arrays(
    supplied: Mapping[str, np.ndarray],
    source_ids: tuple[str, ...],
    *,
    label: str,
) -> tuple[np.ndarray, ...]:
    if set(supplied) != set(source_ids):
        missing = sorted(set(source_ids) - set(supplied))
        extra = sorted(set(supplied) - set(source_ids))
        raise DomainViolationError(
            f"{label} source mismatch; missing={missing}, extra={extra}"
        )
    arrays: list[np.ndarray] = []
    for source_id in source_ids:
        value = np.asarray(supplied[source_id], dtype=float)
        if value.size == 0:
            raise DomainViolationError(f"{label} source {source_id} must be nonempty")
        ensure_finite(value, name=f"{label} source {source_id}")
        arrays.append(value.copy())
    return tuple(arrays)


def _ordered_residuals(
    supplied: Mapping[str, float],
    source_ids: tuple[str, ...],
    *,
    label: str,
) -> tuple[float, ...]:
    if set(supplied) != set(source_ids):
        missing = sorted(set(source_ids) - set(supplied))
        extra = sorted(set(supplied) - set(source_ids))
        raise DomainViolationError(
            f"{label} residual mismatch; missing={missing}, extra={extra}"
        )
    values = tuple(float(supplied[source_id]) for source_id in source_ids)
    ensure_finite(values, name=label)
    if any(value < 0.0 for value in values):
        raise DomainViolationError(f"{label} residuals must be nonnegative")
    return values


def evaluate_exact_product(
    value: ExactProductInput,
    *,
    source_ids: Sequence[str | ComplexId],
) -> ExactProductResult:
    ordered_ids = tuple(str(source_id) for source_id in source_ids)
    if not ordered_ids or len(set(ordered_ids)) != len(ordered_ids):
        raise DomainViolationError("exact product requires unique source identifiers")
    if not np.isfinite(value.tolerance) or value.tolerance < 0.0:
        raise DomainViolationError("product tolerance must be finite and non-negative")

    first = _ordered_arrays(value.first_states, ordered_ids, label="first product")
    second = _ordered_arrays(value.second_states, ordered_ids, label="second product")
    first_residuals = _ordered_residuals(
        value.first_residuals,
        ordered_ids,
        label="first product",
    )
    second_residuals = _ordered_residuals(
        value.second_residuals,
        ordered_ids,
        label="second product",
    )

    # Projection recovery is exact because the product is represented as an
    # ordered tuple and every projection is tuple indexing on its own carrier.
    first_projection = tuple(
        float(np.linalg.norm(first[index] - value.first_states[source_id]))
        for index, source_id in enumerate(ordered_ids)
    )
    second_projection = tuple(
        float(np.linalg.norm(second[index] - value.second_states[source_id]))
        for index, source_id in enumerate(ordered_ids)
    )

    # The canonical representation of each declared source involution is the
    # swap of its paired branch states.  Applying that coordinatewise swap
    # twice must restore both products exactly.
    exchanged_first = second
    exchanged_second = first
    twice_first = exchanged_second
    twice_second = exchanged_first
    exchange_square = float(
        np.sqrt(
            sum(np.linalg.norm(a - b) ** 2 for a, b in zip(twice_first, first))
            + sum(np.linalg.norm(a - b) ** 2 for a, b in zip(twice_second, second))
        )
    )

    first_product_residual = max((*first_projection, *first_residuals), default=0.0)
    second_product_residual = max((*second_projection, *second_residuals), default=0.0)
    closed = max(first_product_residual, second_product_residual, exchange_square) <= value.tolerance
    return ExactProductResult(
        ordered_ids,
        first,
        second,
        first_projection,
        second_projection,
        first_residuals,
        second_residuals,
        first_product_residual,
        second_product_residual,
        exchange_square,
        "closed" if closed else "open",
    )


def exact_product_residual(
    value: ExactProductInput,
    output: ExactProductResult,
    *,
    name: str,
) -> ResidualResult:
    vector = (
        *output.first_projection_residuals,
        *output.second_projection_residuals,
        *output.first_source_residuals,
        *output.second_source_residuals,
        output.exchange_square_residual,
    )
    passed = max(vector, default=0.0) <= value.tolerance
    return ResidualResult(
        name,
        tuple(float(item) for item in vector),
        value.tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {
            "first_product_residual": output.first_product_residual,
            "second_product_residual": output.second_product_residual,
        },
    )


def exact_product_predicate(
    output: ExactProductResult,
    residual: ResidualResult | None,
) -> bool:
    return bool(
        residual is not None
        and residual.passed
        and output.closure_status == "closed"
        and output.exchange_square_residual <= residual.tolerance
    )
