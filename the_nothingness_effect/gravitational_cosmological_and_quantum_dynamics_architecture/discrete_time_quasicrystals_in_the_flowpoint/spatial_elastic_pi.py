"""Spatial reconstruction and regression guards for DTQC Elastic-pi fields."""

from __future__ import annotations

import math

import numpy as np


def backproject_directional_profiles(
    profiles: np.ndarray,
    *,
    grid_size: int | None = None,
) -> np.ndarray:
    r"""Backproject directional one-dimensional profiles into a two-dimensional field.

    For directional samples :math:`S_i(r)` at angles
    :math:`\theta_i=2\pi i/M`, reconstruct

    .. math::

       S_{2D}(x,y)=\frac1M\sum_{i=0}^{M-1}
       S_i\!\left(\frac{x\cos\theta_i+y\sin\theta_i}{\sqrt2}\right).

    The normalized projection keeps every grid point inside the sampled radial
    interval and, unlike row tiling, preserves all directional channels.
    """

    values = np.asarray(profiles, dtype=np.float64)
    if values.ndim != 2 or min(values.shape) < 3:
        raise ValueError("directional profiles must be a finite MxN array with M,N >= 3")
    if not np.isfinite(values).all():
        raise ValueError("directional profiles contain NaN or infinity")

    channel_count, sample_count = values.shape
    size = sample_count if grid_size is None else int(grid_size)
    if size < 3:
        raise ValueError("grid_size must be at least 3")

    axis = np.linspace(-1.0, 1.0, size, dtype=np.float64)
    radial_axis = np.linspace(-1.0, 1.0, sample_count, dtype=np.float64)
    x_grid, y_grid = np.meshgrid(axis, axis, indexing="xy")
    angles = 2.0 * math.pi * np.arange(channel_count, dtype=np.float64) / channel_count

    field = np.zeros((size, size), dtype=np.float64)
    for angle, profile in zip(angles, values, strict=True):
        projection = (
            x_grid * math.cos(float(angle)) + y_grid * math.sin(float(angle))
        ) / math.sqrt(2.0)
        field += np.interp(projection.ravel(), radial_axis, profile).reshape(size, size)
    field /= float(channel_count)

    if not np.isfinite(field).all() or float(np.ptp(field)) <= np.finfo(np.float64).eps:
        raise ValueError("directional backprojection produced a degenerate field")
    return field


def spatial_2d_diagnostics(field: np.ndarray) -> dict[str, float]:
    """Quantify whether a sampled surface has genuine variation on both axes."""

    value = np.asarray(field, dtype=np.float64)
    if value.ndim != 2 or min(value.shape) < 3:
        raise ValueError("spatial regression requires a two-dimensional field")
    if not np.isfinite(value).all():
        raise ValueError("spatial regression field contains NaN or infinity")

    centered = value - float(np.mean(value))
    norm = float(np.linalg.norm(centered))
    if norm <= np.finfo(np.float64).eps:
        raise ValueError("spatial regression field is constant")

    row_broadcast = np.broadcast_to(
        np.mean(value, axis=0, keepdims=True),
        value.shape,
    )
    column_broadcast = np.broadcast_to(
        np.mean(value, axis=1, keepdims=True),
        value.shape,
    )
    row_residual = float(np.linalg.norm(value - row_broadcast) / norm)
    column_residual = float(np.linalg.norm(value - column_broadcast) / norm)

    gradient_y, gradient_x = np.gradient(value)
    x_energy = float(np.mean(np.square(gradient_x)))
    y_energy = float(np.mean(np.square(gradient_y)))
    total_energy = x_energy + y_energy
    if total_energy <= np.finfo(np.float64).eps:
        raise ValueError("spatial regression gradient energy is degenerate")
    x_fraction = x_energy / total_energy
    y_fraction = y_energy / total_energy
    axis_balance = min(x_energy, y_energy) / max(x_energy, y_energy)

    singular_values = np.linalg.svd(centered, compute_uv=False)
    singular_energy = float(np.dot(singular_values, singular_values))
    effective_rank = (
        float(np.square(np.sum(singular_values)) / singular_energy)
        if singular_energy > np.finfo(np.float64).eps
        else 0.0
    )
    return {
        "row_broadcast_residual": row_residual,
        "column_broadcast_residual": column_residual,
        "x_gradient_fraction": x_fraction,
        "y_gradient_fraction": y_fraction,
        "axis_gradient_balance": axis_balance,
        "effective_rank": effective_rank,
    }


def require_true_2d(
    field: np.ndarray,
    *,
    label: str,
    minimum_broadcast_residual: float = 1e-3,
    minimum_axis_balance: float = 5e-2,
    minimum_effective_rank: float = 1.25,
) -> dict[str, float]:
    """Reject row/column broadcasts, one-axis degeneracy, and rank-one surfaces."""

    diagnostics = spatial_2d_diagnostics(field)
    if diagnostics["row_broadcast_residual"] <= minimum_broadcast_residual:
        raise RuntimeError(f"{label} is a broadcasted one-dimensional row profile")
    if diagnostics["column_broadcast_residual"] <= minimum_broadcast_residual:
        raise RuntimeError(f"{label} is a broadcasted one-dimensional column profile")
    if diagnostics["axis_gradient_balance"] <= minimum_axis_balance:
        raise RuntimeError(f"{label} is spatially degenerate along one axis")
    if diagnostics["effective_rank"] <= minimum_effective_rank:
        raise RuntimeError(f"{label} is numerically rank-one-like")
    return diagnostics
