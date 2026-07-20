"""Spatial reconstruction and multi-axis regression guards for DTQC Elastic-pi fields."""

from __future__ import annotations

import math
from typing import Any, Sequence

import numpy as np


INTRINSIC_AXIS_NAMES = ("x", "y", "z", "w", "u")


def intrinsic_axis_names(axis_count: int) -> tuple[str, ...]:
    """Return stable names for the intrinsic DTQC axes."""

    count = int(axis_count)
    if count < 1:
        raise ValueError("axis_count must be positive")
    if count <= len(INTRINSIC_AXIS_NAMES):
        return INTRINSIC_AXIS_NAMES[:count]
    return (*INTRINSIC_AXIS_NAMES, *(f"a{index}" for index in range(5, count)))


def projected_intrinsic_axes(axis_count: int) -> tuple[np.ndarray, np.ndarray]:
    r"""Return the undirected intrinsic axes and their two-dimensional projections.

    The canonical DTQC carrier has five undirected quasiperiodic axes. They are
    represented in the rendered plane at

    .. math::

       \theta_k = \frac{k\pi}{M},\qquad
       d_k=(\cos\theta_k,\sin\theta_k),\quad 0\leq k<M.

    The axis labels ``x, y, z, w, u`` refer to intrinsic carrier coordinates;
    the plotted surface height remains the scalar Elastic-pi response.
    """

    count = int(axis_count)
    if count < 2:
        raise ValueError("at least two intrinsic axes are required")
    angles = math.pi * np.arange(count, dtype=np.float64) / float(count)
    directions = np.column_stack((np.cos(angles), np.sin(angles)))
    return angles, directions


def _normalize_nonnegative(value: np.ndarray, *, label: str) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if not np.isfinite(array).all():
        raise ValueError(f"{label} contains NaN or infinity")
    array = array - float(np.min(array))
    span = float(np.max(array))
    if span <= np.finfo(np.float64).eps:
        raise ValueError(f"{label} is degenerate")
    return array / span


def _validated_axis_inputs(
    axis_components: np.ndarray,
    directions: np.ndarray,
    weights: np.ndarray | Sequence[float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    components = np.asarray(axis_components, dtype=np.float64)
    vectors = np.asarray(directions, dtype=np.float64)
    axis_weights = np.asarray(weights, dtype=np.float64)

    if components.ndim != 3 or min(components.shape[1:]) < 3:
        raise ValueError("axis_components must have shape (M,H,W) with H,W >= 3")
    if vectors.shape != (components.shape[0], 2):
        raise ValueError("directions must have shape (M,2)")
    if axis_weights.shape != (components.shape[0],):
        raise ValueError("weights must contain one positive value per intrinsic axis")
    if not np.isfinite(components).all() or not np.isfinite(vectors).all():
        raise ValueError("axis inputs contain NaN or infinity")
    if not np.isfinite(axis_weights).all() or np.any(axis_weights <= 0.0):
        raise ValueError("all intrinsic-axis weights must be finite and positive")

    vector_norms = np.linalg.norm(vectors, axis=1)
    if np.any(vector_norms <= np.finfo(np.float64).eps):
        raise ValueError("intrinsic-axis directions must be non-zero")
    vectors = vectors / vector_norms[:, None]
    axis_weights = axis_weights / float(np.sum(axis_weights))
    return components, vectors, axis_weights


def axis_complete_dfi(
    axis_components: np.ndarray,
    directions: np.ndarray,
    weights: np.ndarray | Sequence[float],
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    r"""Construct DFI from directional derivatives on every intrinsic axis.

    For component :math:`\phi_k` and projected intrinsic direction :math:`d_k`,

    .. math::

       D_k = |d_k\cdot\nabla\phi_k|,\qquad
       D = \left(\sum_k w_kD_k^2\right)^{1/2}.
    """

    components, vectors, axis_weights = _validated_axis_inputs(
        axis_components,
        directions,
        weights,
    )
    axis_dfi: list[np.ndarray] = []
    for index, (component, direction) in enumerate(zip(components, vectors, strict=True)):
        gradient_y, gradient_x = np.gradient(component)
        directional = direction[0] * gradient_x + direction[1] * gradient_y
        magnitude = np.abs(directional)
        if float(np.ptp(magnitude)) <= np.finfo(np.float64).eps:
            raise ValueError(f"intrinsic axis {index} has degenerate DFI response")
        axis_dfi.append(magnitude)

    stack = np.asarray(axis_dfi, dtype=np.float64)
    aggregate = np.sqrt(np.tensordot(axis_weights, np.square(stack), axes=1))
    aggregate = _normalize_nonnegative(aggregate, label="axis-complete DTQC DFI")
    axis_norms = np.linalg.norm(stack.reshape(stack.shape[0], -1), axis=1)
    diagnostics: dict[str, Any] = {
        "axis_count": int(stack.shape[0]),
        "axis_names": list(intrinsic_axis_names(stack.shape[0])),
        "axis_weights": [float(value) for value in axis_weights],
        "axis_dfi_norms": [float(value) for value in axis_norms],
        "minimum_axis_dfi_norm": float(np.min(axis_norms)),
    }
    return aggregate, stack, diagnostics


def axis_complete_entropy(
    axis_components: np.ndarray,
    directions: np.ndarray,
    weights: np.ndarray | Sequence[float],
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    r"""Build one entropy channel per intrinsic axis before aggregation.

    Each channel contains its own projected carrier energy, directional DFI,
    and directional Hessian curvature. The aggregate is a positive weighted
    sum, so no axis can cancel another axis.
    """

    components, vectors, axis_weights = _validated_axis_inputs(
        axis_components,
        directions,
        weights,
    )
    channels: list[np.ndarray] = []
    for index, (component, direction) in enumerate(zip(components, vectors, strict=True)):
        gradient_y, gradient_x = np.gradient(component)
        gradient_yy, gradient_yx = np.gradient(gradient_y)
        gradient_xy, gradient_xx = np.gradient(gradient_x)
        mixed = 0.5 * (gradient_xy + gradient_yx)
        dx, dy = float(direction[0]), float(direction[1])
        directional_gradient = dx * gradient_x + dy * gradient_y
        directional_curvature = (
            dx * dx * gradient_xx
            + 2.0 * dx * dy * mixed
            + dy * dy * gradient_yy
        )
        channel = (
            0.45
            * _normalize_nonnegative(
                np.square(component),
                label=f"intrinsic axis {index} field energy",
            )
            + 0.35
            * _normalize_nonnegative(
                np.square(directional_gradient),
                label=f"intrinsic axis {index} directional DFI",
            )
            + 0.20
            * _normalize_nonnegative(
                np.square(directional_curvature),
                label=f"intrinsic axis {index} directional curvature",
            )
        )
        channels.append(channel)

    stack = np.asarray(channels, dtype=np.float64)
    aggregate = np.tensordot(axis_weights, stack, axes=1)
    if not np.isfinite(aggregate).all() or float(np.ptp(aggregate)) <= np.finfo(np.float64).eps:
        raise ValueError("axis-complete DTQC entropy is degenerate")

    axis_norms = np.linalg.norm(stack.reshape(stack.shape[0], -1), axis=1)
    diagnostics: dict[str, Any] = {
        "axis_count": int(stack.shape[0]),
        "axis_names": list(intrinsic_axis_names(stack.shape[0])),
        "axis_weights": [float(value) for value in axis_weights],
        "axis_entropy_norms": [float(value) for value in axis_norms],
        "minimum_axis_entropy_norm": float(np.min(axis_norms)),
    }
    return aggregate, stack, diagnostics


def apply_elastic_pi_on_all_axes(
    axis_entropy: np.ndarray,
    weights: np.ndarray | Sequence[float],
    *,
    K_D: float,
    sign: float = -1.0,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    r"""Apply Elastic-pi independently on every intrinsic axis and aggregate.

    .. math::

       \pi_{\mathcal E,k}=\pi\exp(sS_k/\mathcal K_{\mathcal D}),
       \qquad
       \pi_{\mathcal E}=\pi\prod_k
       \left(\frac{\pi_{\mathcal E,k}}{\pi}\right)^{w_k}.

    With positive weights this is exactly the canonical law evaluated on
    :math:`S=\sum_kw_kS_k`, while preserving an auditable per-axis response.
    """

    channels = np.asarray(axis_entropy, dtype=np.float64)
    axis_weights = np.asarray(weights, dtype=np.float64)
    if channels.ndim != 3 or min(channels.shape[1:]) < 3:
        raise ValueError("axis_entropy must have shape (M,H,W)")
    if axis_weights.shape != (channels.shape[0],):
        raise ValueError("weights must contain one value per entropy channel")
    if not np.isfinite(channels).all() or not np.isfinite(axis_weights).all():
        raise ValueError("Elastic-pi axis inputs contain NaN or infinity")
    if np.any(axis_weights <= 0.0):
        raise ValueError("Elastic-pi axis weights must be strictly positive")
    if not math.isfinite(K_D) or K_D <= 0.0:
        raise ValueError("K_D must be finite and strictly positive")
    if not math.isfinite(sign) or sign == 0.0:
        raise ValueError("Elastic-pi sign must be finite and non-zero")

    axis_weights = axis_weights / float(np.sum(axis_weights))
    exponent = np.clip(sign * channels / K_D, -100.0, math.log(100.0))
    axis_surfaces = math.pi * np.exp(exponent)
    aggregate_entropy = np.tensordot(axis_weights, channels, axes=1)
    aggregate = math.pi * np.exp(
        np.tensordot(axis_weights, np.log(axis_surfaces / math.pi), axes=1)
    )
    direct = math.pi * np.exp(
        np.clip(sign * aggregate_entropy / K_D, -100.0, math.log(100.0))
    )
    application_residual = float(np.linalg.norm(aggregate - direct) / np.linalg.norm(direct))
    if application_residual > 1e-12:
        raise RuntimeError("per-axis Elastic-pi aggregation does not reproduce the direct law")

    removal_residuals: list[float] = []
    aggregate_norm = float(np.linalg.norm(aggregate))
    for index in range(channels.shape[0]):
        removed_entropy = aggregate_entropy - axis_weights[index] * channels[index]
        removed = math.pi * np.exp(
            np.clip(sign * removed_entropy / K_D, -100.0, math.log(100.0))
        )
        residual = float(np.linalg.norm(aggregate - removed) / aggregate_norm)
        if residual <= 1e-8:
            raise RuntimeError(f"intrinsic axis {index} does not affect the Elastic-pi field")
        removal_residuals.append(residual)

    axis_spans = [float(np.ptp(surface)) for surface in axis_surfaces]
    if any(span <= np.finfo(np.float64).eps for span in axis_spans):
        raise RuntimeError("an intrinsic Elastic-pi axis response is degenerate")

    diagnostics: dict[str, Any] = {
        "axis_count": int(channels.shape[0]),
        "axis_names": list(intrinsic_axis_names(channels.shape[0])),
        "axis_weights": [float(value) for value in axis_weights],
        "axis_elastic_pi_spans": axis_spans,
        "axis_source_removal_residuals": removal_residuals,
        "minimum_axis_source_removal_residual": float(np.min(removal_residuals)),
        "axis_application_residual": application_residual,
        "K_D": float(K_D),
        "sign": float(sign),
    }
    return aggregate, axis_surfaces, diagnostics


def backproject_directional_profiles(
    profiles: np.ndarray,
    *,
    grid_size: int | None = None,
    angles: np.ndarray | Sequence[float] | None = None,
) -> np.ndarray:
    r"""Backproject directional one-dimensional profiles into a two-dimensional field.

    For directional samples :math:`S_i(r)` at angles :math:`\theta_i`, reconstruct

    .. math::

       S_{2D}(x,y)=\frac1M\sum_{i=0}^{M-1}
       S_i\!\left(\frac{x\cos\theta_i+y\sin\theta_i}{\sqrt2}\right).

    The normalized projection keeps every grid point inside the sampled radial
    interval and, unlike row tiling, preserves every supplied directional channel.
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
    if angles is None:
        angle_values = 2.0 * math.pi * np.arange(channel_count, dtype=np.float64) / channel_count
    else:
        angle_values = np.asarray(angles, dtype=np.float64)
        if angle_values.shape != (channel_count,) or not np.isfinite(angle_values).all():
            raise ValueError("angles must contain one finite angle per directional profile")

    field = np.zeros((size, size), dtype=np.float64)
    for angle, profile in zip(angle_values, values, strict=True):
        projection = (
            x_grid * math.cos(float(angle)) + y_grid * math.sin(float(angle))
        ) / math.sqrt(2.0)
        field += np.interp(projection.ravel(), radial_axis, profile).reshape(size, size)
    field /= float(channel_count)

    if not np.isfinite(field).all() or float(np.ptp(field)) <= np.finfo(np.float64).eps:
        raise ValueError("directional backprojection produced a degenerate field")
    return field


def spatial_2d_diagnostics(field: np.ndarray) -> dict[str, float]:
    """Quantify whether a sampled surface has genuine variation on both rendered axes."""

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
    """Reject row/column broadcasts, rendered-axis degeneracy, and rank-one surfaces."""

    diagnostics = spatial_2d_diagnostics(field)
    if diagnostics["row_broadcast_residual"] <= minimum_broadcast_residual:
        raise RuntimeError(f"{label} is a broadcasted one-dimensional row profile")
    if diagnostics["column_broadcast_residual"] <= minimum_broadcast_residual:
        raise RuntimeError(f"{label} is a broadcasted one-dimensional column profile")
    if diagnostics["axis_gradient_balance"] <= minimum_axis_balance:
        raise RuntimeError(f"{label} is spatially degenerate along one rendered axis")
    if diagnostics["effective_rank"] <= minimum_effective_rank:
        raise RuntimeError(f"{label} is numerically rank-one-like")
    return diagnostics
