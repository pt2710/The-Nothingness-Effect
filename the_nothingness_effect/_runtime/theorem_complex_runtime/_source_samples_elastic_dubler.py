"""Deterministic provenance samples for explicit Elastic Dubler contracts."""
from __future__ import annotations

import numpy as np

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.canonical_contracts import (
    A_IDS,
    B_SPECS,
    C_SPECS,
    ElasticDublerInput,
)


def elastic_dubler_sample() -> ElasticDublerInput:
    coordinates = np.linspace(0.0, 1.0, 9)
    entropy = -0.2 * coordinates
    return ElasticDublerInput(
        coordinates=coordinates,
        entropy=entropy,
        pdfi=1.0 + 0.15 * np.sin(2.0 * np.pi * coordinates),
        parity=np.mod(np.arange(coordinates.size), 2),
        observable=0.6 + coordinates + 0.05 * np.cos(2.0 * np.pi * coordinates),
        current=-entropy,
        information=1.0 + coordinates,
        quantum_correlation=0.8 + 0.1 * np.cos(np.pi * coordinates),
        elasticity=2.0,
        domain_elasticity=2.0 + 0.25 * coordinates,
        tolerance=1e-10,
    )


def sample_inputs() -> dict[str, object]:
    sample = elastic_dubler_sample()
    identifiers = (
        *A_IDS,
        *(item[0] for item in B_SPECS),
        *(item[0] for item in C_SPECS),
    )
    return {identifier: sample for identifier in identifiers}
