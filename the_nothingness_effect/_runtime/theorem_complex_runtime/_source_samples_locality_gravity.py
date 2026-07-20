"""Deterministic provenance samples for Locality-Driven Gravity contracts."""
from __future__ import annotations

import numpy as np

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.canonical_contracts import (
    A_IDS,
    B_SPECS,
    C_SPECS,
    LocalityGravityInput,
)


def locality_gravity_sample() -> LocalityGravityInput:
    radius = np.linspace(1.0, 2.0, 9)
    step = float(radius[1] - radius[0])
    entropy = 0.15 + 0.2 * radius
    potential = np.log(radius)
    grad_s = np.gradient(entropy, step, edge_order=2)
    grad_phi = np.gradient(potential, step, edge_order=2)
    velocity = np.sqrt(np.maximum(radius * grad_phi, 0.0))
    pitch = np.arctan(np.abs(grad_s) / (1.0 + np.abs(grad_phi)))
    return LocalityGravityInput(
        radius=radius,
        entropy=entropy,
        potential=potential,
        density=1.0 + 0.15 * radius,
        rotation_velocity=velocity,
        pitch_angle=pitch,
        halo_density=1.2 + 0.1 * radius,
        filament=1.1 + 0.05 * np.sin(np.pi * radius),
        confinement=1.0 + 0.05 * np.cos(np.pi * radius),
        cluster=1.1 + 0.08 * radius,
        information=1.0 + 0.12 * radius,
        cosmic_web=1.2 + 0.1 * np.sin(2.0 * np.pi * radius),
        screening_mass=0.5,
        elasticity=2.0,
        tolerance=1e-10,
    )


def sample_inputs() -> dict[str, object]:
    sample = locality_gravity_sample()
    identifiers = (
        *A_IDS,
        *(item[0] for item in B_SPECS),
        *(item[0] for item in C_SPECS),
    )
    return {identifier: sample for identifier in identifiers}
