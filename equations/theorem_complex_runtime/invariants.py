"""Shared invariant, additive-derivation and spatial-closure helpers."""

from __future__ import annotations

from typing import Any, Callable

import numpy as np

from .types import ComplexId, SourceRemovalResult
from .validation import ensure_finite


def _array(value: Any) -> np.ndarray:
    ensure_finite(value)
    dtype = complex if np.iscomplexobj(value) else float
    return np.asarray(value, dtype=dtype)


def l2_norm(value: Any) -> float:
    result = float(np.linalg.norm(_array(value).ravel(), ord=2))
    ensure_finite(result, name="l2 norm")
    return result


def involution_residual(operator: Callable[[Any], Any], value: Any) -> float:
    original = _array(value)
    twice = _array(operator(operator(value)))
    if twice.shape != original.shape:
        raise ValueError("Involution result shape differs from the source shape")
    return l2_norm(twice - original)


def invariant_projector(operator: Callable[[Any], Any], value: Any) -> np.ndarray:
    source = _array(value)
    transformed = _array(operator(value))
    return 0.5 * (source + transformed)


def anti_invariant_projector(operator: Callable[[Any], Any], value: Any) -> np.ndarray:
    source = _array(value)
    transformed = _array(operator(value))
    return 0.5 * (source - transformed)


def additive_derivation(source_a: Any, source_b: Any, *, coupling: float = 1.0) -> np.ndarray:
    """Genuine two-source interaction, not a product carrier.

    The bilinear term ensures the result changes when either complete source is
    removed. Module-specific B laws may use a more specialized operator.
    """

    a = _array(source_a)
    b = _array(source_b)
    if a.shape != b.shape:
        raise ValueError("Additive sources must share a codomain shape")
    ensure_finite(coupling, name="coupling")
    result = a + b + float(coupling) * a * b
    ensure_finite(result, name="additive derivation")
    return result


def non_cancellation_energy(source_a: Any, source_b: Any, combined: Any) -> float:
    a = _array(source_a)
    b = _array(source_b)
    c = _array(combined)
    if a.shape != b.shape or a.shape != c.shape:
        raise ValueError("Sources and combined response must have equal shapes")
    interaction = c - a - b
    return float(np.vdot(interaction.ravel(), interaction.ravel()).real)


def source_removal_result(
    source_id: ComplexId,
    complete_response: Any,
    removed_response: Any,
    *,
    tolerance: float,
) -> SourceRemovalResult:
    baseline = l2_norm(complete_response)
    removed = l2_norm(removed_response)
    necessity = l2_norm(_array(complete_response) - _array(removed_response))
    return SourceRemovalResult(
        source_id=source_id,
        baseline_response=baseline,
        removed_response=removed,
        necessity_residual=necessity,
        necessary=necessity > tolerance,
    )


def boundary_leakage(field: Any) -> float:
    values = _array(field)
    if values.ndim == 0 or values.size < 2:
        raise ValueError("Boundary leakage requires a spatial field with at least two samples")
    boundary = np.concatenate((np.ravel(values[0]), np.ravel(values[-1])))
    return l2_norm(boundary)


def coercivity_ratio(operator_value: Any, source_value: Any) -> float:
    denominator = l2_norm(source_value)
    if denominator == 0:
        raise ValueError("Coercivity is undefined for the zero source")
    ratio = l2_norm(operator_value) / denominator
    ensure_finite(ratio, name="coercivity ratio")
    return ratio


def observability_residual(source: Any, reconstruction: Any) -> float:
    a = _array(source)
    b = _array(reconstruction)
    if a.shape != b.shape:
        raise ValueError("Reconstruction shape differs from the source shape")
    return l2_norm(a - b)
