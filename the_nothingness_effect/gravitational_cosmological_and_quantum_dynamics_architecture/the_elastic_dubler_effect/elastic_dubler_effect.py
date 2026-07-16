"""Elastic Dubler-effect helpers.

This module is the canonical Dubler-effect implementation in the repository.
It computes Dubler ratios from Elastic-pi profiles and keeps the numerical
artifact wording conservative: finite illustrative simulation, not a formal
proof substitute.
"""

from __future__ import annotations

import numpy as np

from the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.elastic_pi import ElasticPi, ElasticPiEvaluationError
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import ensure_finite


def validate_kd(k_d: float | np.ndarray) -> np.ndarray:
    values = np.asarray(k_d, dtype=float)
    ensure_finite(values, name="Elastic Dubler K_D")
    if np.any(values <= 0):
        raise ValueError("K_D must be positive for the Elastic Dubler-effect model.")
    return values


def normalize_zero_one(values: np.ndarray) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    span = float(np.max(data) - np.min(data))
    if span == 0.0:
        return np.zeros_like(data)
    return (data - np.min(data)) / span


def scale_entropy(values: np.ndarray, scale: float = 5.0) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    centered = data - np.mean(data)
    return centered / (np.max(np.abs(centered)) + 1e-12) * scale


def elastic_pi_ratio(delta_s: float | np.ndarray, K_D: float | np.ndarray) -> np.ndarray:
    """Return the normalized Elastic-pi ratio exp(-delta_s / K_D)."""

    kd = validate_kd(K_D)
    values = np.asarray(delta_s, dtype=float)
    ensure_finite(values, name="Elastic Dubler entropy difference")
    if kd.ndim == 0:
        values_1d = np.atleast_1d(values)
        _, pi_e, _ = ElasticPi(float(kd)).compute_piE_and_laplacian(values_1d, K_D=float(kd))
        ratio = pi_e / np.pi
        return ratio[0] if values.ndim == 0 else ratio.reshape(values.shape)
    exponent = -values / kd
    ensure_finite(exponent, name="Elastic Dubler exact exponent")
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        ratio = np.exp(exponent)
    if np.any(~np.isfinite(ratio)) or np.any(ratio == 0.0):
        raise ElasticPiEvaluationError(
            "Elastic Dubler ratio overflowed or underflowed; canonical evaluation does not clip the exponent"
        )
    return ratio


def dubler_frequency_ratio(delta_s: float | np.ndarray, K_D: float | np.ndarray) -> np.ndarray:
    return elastic_pi_ratio(delta_s, K_D)


def dubler_shift(delta_s: float | np.ndarray, K_D: float | np.ndarray) -> np.ndarray:
    return dubler_frequency_ratio(delta_s, K_D) - 1.0


def entropy_gradient_path_integral(gradient_values: np.ndarray, path_spacing: float) -> float:
    if path_spacing <= 0:
        raise ValueError("path_spacing must be positive.")
    return float(np.trapezoid(np.asarray(gradient_values, dtype=float), dx=path_spacing))


def compute_dubler_grid(
    delta_s_values: np.ndarray,
    K_D_values: np.ndarray,
) -> dict[str, np.ndarray]:
    delta_s = np.asarray(delta_s_values, dtype=float)
    kd_values = validate_kd(K_D_values)
    ratios = np.vstack([dubler_frequency_ratio(delta_s, kd) for kd in kd_values])
    shifts = ratios - 1.0
    return {
        "delta_s": delta_s,
        "K_D": kd_values,
        "frequency_ratio": ratios,
        "dubler_shift": shifts,
    }


def synthetic_entropy_pair(seed: int = 42, n_samples: int = 240) -> dict[str, np.ndarray]:
    """Return deterministic entropy-like paired features for Dubler artifacts."""

    rng = np.random.default_rng(seed)
    t = np.linspace(-2.0, 2.0, n_samples)
    feature_a = 1.0 / (1.0 + np.exp(-3.0 * t))
    feature_b = np.exp(-(t**2) / 1.5)
    feature_a = normalize_zero_one(feature_a + rng.normal(scale=1e-3, size=t.shape))
    feature_b = normalize_zero_one(feature_b + rng.normal(scale=1e-3, size=t.shape))
    entropy_a = scale_entropy(feature_a)
    entropy_b = scale_entropy(feature_b)
    return {
        "t": t,
        "entropy_a": entropy_a,
        "entropy_b": entropy_b,
        "entropy_gradient": entropy_a - entropy_b,
    }
