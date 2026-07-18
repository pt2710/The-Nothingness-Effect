"""Shared exact kernel for positive B-energy spatial C functionals.

For source energies e_m >= 0, the appendix laws use raw energies in the
coercive volume term and normalized defects theta_m=e_m/(1+e_m) in the
spatial potential.  Gradient and boundary penalties act on that potential.
"""

from __future__ import annotations

import numpy as np

from .types import DomainViolationError
from .validation import ensure_finite


def involutive_permutation(values: tuple[int, ...], size: int, *, label: str) -> np.ndarray:
    permutation = np.asarray(tuple(int(item) for item in values), dtype=int)
    if permutation.shape != (size,) or sorted(permutation.tolist()) != list(range(size)):
        raise DomainViolationError(f"{label} must be a complete permutation")
    if not np.array_equal(permutation[permutation], np.arange(size)):
        raise DomainViolationError(f"{label} must be involutive")
    return permutation


def positive_spatial_functional(
    fields: np.ndarray,
    weights: np.ndarray,
    *,
    spacing: float,
    gradient_weight: float,
    boundary_weight: float,
) -> tuple[np.ndarray, np.ndarray, float, float, float, float]:
    energies = np.asarray(fields, dtype=float)
    source_weights = np.asarray(weights, dtype=float)
    ensure_finite(energies, name="spatial source energies")
    ensure_finite(source_weights, name="spatial source weights")
    if energies.ndim != 2 or source_weights.shape != (energies.shape[0],):
        raise DomainViolationError("spatial functional requires source-by-space fields and one weight per source")
    if np.any(energies < 0.0):
        raise DomainViolationError("spatial source energies must be nonnegative")
    if np.any(source_weights < 0.0):
        raise DomainViolationError("spatial source weights must be nonnegative")

    normalized_defects = energies / (1.0 + energies)
    potential = source_weights @ normalized_defects
    volume = float(spacing * np.sum(source_weights[:, None] * energies))
    gradient = np.diff(potential) / spacing
    gradient_energy = float(gradient_weight * spacing * np.sum(gradient * gradient))
    boundary = float(boundary_weight * (potential[0] ** 2 + potential[-1] ** 2))
    total = volume + gradient_energy + boundary
    ensure_finite(
        (normalized_defects, potential, volume, gradient_energy, boundary, total),
        name="positive spatial functional",
    )
    return normalized_defects, potential, volume, gradient_energy, boundary, total


def positive_spatial_functional_reference(
    fields: np.ndarray,
    weights: np.ndarray,
    *,
    spacing: float,
    gradient_weight: float,
    boundary_weight: float,
) -> float:
    energies = np.asarray(fields, dtype=float)
    source_weights = np.asarray(weights, dtype=float)
    source_count, sample_count = energies.shape
    potential = [
        sum(
            float(source_weights[source])
            * (float(energies[source, point]) / (1.0 + float(energies[source, point])))
            for source in range(source_count)
        )
        for point in range(sample_count)
    ]
    volume = spacing * sum(
        float(source_weights[source]) * float(energies[source, point])
        for source in range(source_count)
        for point in range(sample_count)
    )
    gradient = gradient_weight * spacing * sum(
        ((potential[point + 1] - potential[point]) / spacing) ** 2
        for point in range(sample_count - 1)
    )
    boundary = boundary_weight * (potential[0] ** 2 + potential[-1] ** 2)
    return float(volume + gradient + boundary)
