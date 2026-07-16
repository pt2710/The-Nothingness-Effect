"""Canonical Elastic-pi source law with explicit approximation diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np

from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.dfi import NormalizedDFIResult, require_finite_dfi
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
    SingularEvaluationError,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import ensure_finite


class ElasticPiStatus(str, Enum):
    EXACTLY_EVALUATED = "exactly_evaluated"
    APPROXIMATED = "approximated"
    UNDERFLOW = "underflow"
    OVERFLOW = "overflow"


class ElasticPiEvaluationError(SingularEvaluationError):
    """Raised when a requested floating-point Elastic-pi value is unavailable."""


@dataclass(frozen=True)
class ElasticPiEvaluation:
    entropy: np.ndarray
    K_D: float
    coordinates: np.ndarray
    exact_exponent: np.ndarray
    evaluated_exponent: np.ndarray
    analytic_log_value: np.ndarray
    value: np.ndarray | None
    log_laplacian: np.ndarray
    status: ElasticPiStatus
    approximation_metadata: dict[str, Any]

    @property
    def exact_numerical_evaluation(self) -> bool:
        return self.status is ElasticPiStatus.EXACTLY_EVALUATED


def _coordinates(entropy: np.ndarray, x: Any | None) -> tuple[np.ndarray, float]:
    if entropy.ndim != 1 or entropy.size == 0:
        raise DomainViolationError("Elastic-pi entropy must be a non-empty one-dimensional array")
    coordinates = np.arange(entropy.size, dtype=float) if x is None else np.asarray(x, dtype=float)
    if coordinates.shape != entropy.shape:
        raise DomainViolationError("Elastic-pi coordinates must have the entropy shape")
    ensure_finite(coordinates, name="Elastic-pi coordinates")
    if coordinates.size < 2:
        return coordinates, 1.0
    spacing = np.diff(coordinates)
    if np.any(spacing <= 0):
        raise DomainViolationError("Elastic-pi coordinates must be strictly increasing")
    mean_spacing = float(np.mean(spacing))
    if not np.allclose(spacing, mean_spacing, rtol=1e-10, atol=1e-12):
        raise DomainViolationError("the canonical finite-difference Laplacian requires uniform coordinates")
    return coordinates, mean_spacing


def evaluate_elastic_pi(
    entropy: Any,
    *,
    K_D: float,
    x: Any | None = None,
    exponent_clip: float | None = None,
) -> ElasticPiEvaluation:
    r"""Evaluate pi_E = pi exp(-S/K_D), with K_D > 0.

    ``exponent_clip`` is an explicitly approximate evaluation policy.  The
    exact exponent and analytic logarithm are retained even when clipping is
    requested, so a clipped value cannot masquerade as the exact source law.
    """

    values = np.asarray(entropy, dtype=float)
    ensure_finite(values, name="Elastic-pi entropy")
    scale = float(K_D)
    if not np.isfinite(scale) or scale <= 0:
        raise DomainViolationError("Elastic-pi K_D must be finite and strictly positive")
    coordinates, spacing = _coordinates(values, x)
    exact_exponent = -values / scale
    ensure_finite(exact_exponent, name="Elastic-pi exact exponent")

    clipped = np.zeros(exact_exponent.shape, dtype=bool)
    evaluated_exponent = exact_exponent.copy()
    if exponent_clip is not None:
        limit = float(exponent_clip)
        if not np.isfinite(limit) or limit <= 0:
            raise DomainViolationError("exponent_clip must be finite and strictly positive")
        evaluated_exponent = np.clip(exact_exponent, -limit, limit)
        clipped = evaluated_exponent != exact_exponent

    analytic_log_value = np.log(np.pi) + exact_exponent
    laplacian = np.zeros_like(analytic_log_value)
    if analytic_log_value.size > 2:
        laplacian[1:-1] = (
            analytic_log_value[2:]
            - 2.0 * analytic_log_value[1:-1]
            + analytic_log_value[:-2]
        ) / (spacing**2)

    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        numerical_value = np.pi * np.exp(evaluated_exponent)
    has_overflow = bool(np.any(np.isinf(numerical_value)))
    has_underflow = bool(np.any(numerical_value == 0.0))
    if has_overflow or has_underflow:
        status = ElasticPiStatus.OVERFLOW if has_overflow else ElasticPiStatus.UNDERFLOW
        result_value = None
    else:
        ensure_finite(numerical_value, name="Elastic-pi numerical value")
        result_value = numerical_value
        status = ElasticPiStatus.APPROXIMATED if np.any(clipped) else ElasticPiStatus.EXACTLY_EVALUATED

    metadata: dict[str, Any] = {
        "clipped": bool(np.any(clipped)),
        "clipped_count": int(np.count_nonzero(clipped)),
        "exponent_clip": None if exponent_clip is None else float(exponent_clip),
        "exact_exponent_min": float(np.min(exact_exponent)),
        "exact_exponent_max": float(np.max(exact_exponent)),
        "evaluated_exponent_min": float(np.min(evaluated_exponent)),
        "evaluated_exponent_max": float(np.max(evaluated_exponent)),
        "source_law": "pi * exp(-S / K_D)",
        "exact_value_available": result_value is not None and not bool(np.any(clipped)),
    }
    return ElasticPiEvaluation(
        values,
        scale,
        coordinates,
        exact_exponent,
        evaluated_exponent,
        analytic_log_value,
        result_value,
        laplacian,
        status,
        metadata,
    )


def require_elastic_pi_value(result: ElasticPiEvaluation) -> np.ndarray:
    if result.value is None:
        raise ElasticPiEvaluationError(
            f"Elastic-pi numerical evaluation ended with {result.status.value}; "
            "request an explicit exponent_clip policy for an approximation"
        )
    return result.value


class ElasticPi:
    """Backward-compatible facade over the canonical typed Elastic-pi law."""

    def __init__(self, K_D: float = 1.0):
        scale = float(K_D)
        if not np.isfinite(scale) or scale <= 0:
            raise DomainViolationError("Elastic-pi K_D must be finite and strictly positive")
        self.K_D = scale

    def build_S_analytic(self, x, formula=None, **kwargs):
        coordinates = np.asarray(x)
        result = formula(coordinates, **kwargs) if formula is not None else np.zeros_like(coordinates)
        ensure_finite(result, name="analytic entropy")
        return result

    def evaluate(self, S, x=None, K_D=None, *, exponent_clip=None) -> ElasticPiEvaluation:
        scale = self.K_D if K_D is None else float(K_D)
        return evaluate_elastic_pi(S, K_D=scale, x=x, exponent_clip=exponent_clip)

    def compute_piE_and_laplacian(
        self,
        S,
        x=None,
        K_D=None,
        *,
        exponent_clip=None,
        return_diagnostics: bool = False,
    ):
        result = self.evaluate(S, x=x, K_D=K_D, exponent_clip=exponent_clip)
        if return_diagnostics:
            return result
        if exponent_clip is not None:
            raise DomainViolationError(
                "clipped Elastic-pi evaluation requires return_diagnostics=True so approximation metadata is preserved"
            )
        return result.coordinates, require_elastic_pi_value(result), result.log_laplacian

    def empirical_from_dfi(self, data, dfi_engine, soi=1.0, feature=None):
        entropic = dfi_engine.dfi(data, soi=soi)
        if isinstance(entropic, NormalizedDFIResult):
            require_finite_dfi(entropic)
            normalized = np.asarray(entropic.normalized_entropy)
            entropy = entropic.spectrum_scale * normalized
            if feature is not None:
                index = entropic.feature_names.index(feature)
                return entropy[:, index]
            return np.mean(entropy, axis=1)
        if feature is not None:
            return entropic[feature]["Relative_Entropy"]
        all_entropy = [item["Relative_Entropy"] for item in entropic.values()]
        return np.mean(np.vstack(all_entropy), axis=0)
