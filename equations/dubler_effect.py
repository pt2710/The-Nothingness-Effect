"""Finite Dubler-effect helpers for manuscript Figure 31.

The functions implement a deterministic numerical support figure for the
Dubler shift as an Elastic-pi ratio. This is a repository-linked computational
artifact, not a formal proof substitute.
"""

from __future__ import annotations

import numpy as np

from equations.elastic_pi.elastic_pi import ElasticPi


def _validate_kd(k_d: float | np.ndarray) -> np.ndarray:
    values = np.asarray(k_d, dtype=float)
    if np.any(values <= 0):
        raise ValueError("K_D must be positive for the finite Dubler-effect model.")
    return values


def elastic_pi_ratio(delta_s: float | np.ndarray, K_D: float | np.ndarray) -> np.ndarray:
    """Return exp(-delta_s / K_D) for the finite Elastic-pi ratio model."""

    kd = _validate_kd(K_D)
    values = np.asarray(delta_s, dtype=float)
    if kd.ndim == 0:
        values_1d = np.atleast_1d(values)
        _, pi_e, _ = ElasticPi(float(kd)).compute_piE_and_laplacian(values_1d, K_D=float(kd))
        ratio = pi_e / np.pi
        return ratio[0] if values.ndim == 0 else ratio.reshape(values.shape)
    exponent = np.clip(-values / kd, -700, 700)
    return np.exp(exponent)


def dubler_frequency_ratio(delta_s: float | np.ndarray, K_D: float | np.ndarray) -> np.ndarray:
    """Return the finite illustrative Dubler frequency ratio."""

    return elastic_pi_ratio(delta_s, K_D)


def dubler_shift(delta_s: float | np.ndarray, K_D: float | np.ndarray) -> np.ndarray:
    """Return ratio - 1 for the deterministic numerical support figure."""

    return dubler_frequency_ratio(delta_s, K_D) - 1.0


def entropy_gradient_path_integral(
    gradient_values: np.ndarray,
    path_spacing: float,
) -> float:
    """Integrate an entropy-gradient path with the trapezoidal rule."""

    if path_spacing <= 0:
        raise ValueError("path_spacing must be positive.")
    return float(np.trapezoid(np.asarray(gradient_values, dtype=float), dx=path_spacing))


def compute_dubler_grid(
    delta_s_values: np.ndarray,
    K_D_values: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute Figure 31 curves and a delta_s by K_D grid."""

    delta_s = np.asarray(delta_s_values, dtype=float)
    kd_values = _validate_kd(K_D_values)
    ratios = np.vstack([dubler_frequency_ratio(delta_s, kd) for kd in kd_values])
    shifts = ratios - 1.0
    return {
        "delta_s": delta_s,
        "K_D": kd_values,
        "frequency_ratio": ratios,
        "dubler_shift": shifts,
    }
