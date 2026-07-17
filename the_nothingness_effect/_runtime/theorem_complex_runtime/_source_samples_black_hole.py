"""Deterministic provenance samples for Black-Hole Dynamics contracts."""
from __future__ import annotations

import numpy as np

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.canonical_contracts import (
    A_IDS,
    B_SPECS,
    C_ID,
    BlackHoleInput,
)


def black_hole_sample() -> BlackHoleInput:
    coordinate = np.linspace(0.0, 1.0, 9)
    step = float(coordinate[1] - coordinate[0])
    elasticity = 2.0
    entropy = 1.0 - 0.2 * coordinate
    mass = 2.0 + 0.25 * coordinate
    hawking_flux = np.exp(-entropy / elasticity) / mass**2
    relaxation_flux = np.maximum(-np.gradient(entropy, step, edge_order=2), 0.0)
    observer_signal = coordinate
    threshold = 0.5
    visibility = 1.0 / (1.0 + np.exp(-(observer_signal - threshold) / elasticity))
    deformation = 0.1 + 0.04 * np.sin(2.0 * np.pi * coordinate)
    decay = np.exp(-(coordinate - coordinate[0]) / elasticity)
    gravitational_memory = np.cumsum(np.abs(deformation) * decay) * step
    residual_memory = np.abs(deformation) * decay
    reference = 0.5 + 0.1 * coordinate
    consistency_witness = 0.02 * np.cos(np.pi * coordinate)
    simulation = reference + consistency_witness
    return BlackHoleInput(
        coordinate=coordinate,
        entropy=entropy,
        mass=mass,
        hawking_flux=hawking_flux,
        relaxation_flux=relaxation_flux,
        observer_signal=observer_signal,
        visibility=visibility,
        deformation=deformation,
        gravitational_memory=gravitational_memory,
        residual_memory=residual_memory,
        simulation=simulation,
        reference=reference,
        consistency_witness=consistency_witness,
        elasticity=elasticity,
        observer_threshold=threshold,
        tolerance=1e-10,
    )


def sample_inputs() -> dict[str, object]:
    sample = black_hole_sample()
    identifiers = (*A_IDS, *(item[0] for item in B_SPECS), C_ID)
    return {identifier: sample for identifier in identifiers}
