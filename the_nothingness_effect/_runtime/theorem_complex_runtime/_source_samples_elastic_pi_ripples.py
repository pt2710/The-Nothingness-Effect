"""Deterministic provenance samples for Elastic-pi Ripple contracts."""
from __future__ import annotations

import numpy as np

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts.canonical_contracts import (
    A_IDS,
    B_SPECS,
    C_ID,
    RippleInput,
)


def elastic_pi_ripple_sample() -> RippleInput:
    coordinate = np.linspace(0.0, 1.0, 9)
    step = float(coordinate[1] - coordinate[0])
    waveform = np.sin(2.0 * np.pi * coordinate)
    memory_kernel = np.exp(-2.0 * coordinate)
    normalized_kernel = memory_kernel / float(np.sum(memory_kernel))
    memory_imprint = np.convolve(waveform, normalized_kernel, mode="same") * step
    parity = np.mod(np.arange(coordinate.size), 2)
    boundary_mode = np.cos(np.pi * coordinate)
    conversion_gain = 0.8 + 0.1 * coordinate
    converted_mode = (1.0 - 2.0 * parity) * conversion_gain * boundary_mode
    amplitude = 0.4 + 0.05 * np.sin(2.0 * np.pi * coordinate)
    shock_threshold = 0.2
    shock_indicator = np.maximum(np.abs(np.gradient(amplitude, step, edge_order=2)) - shock_threshold, 0.0)
    frequency = np.linspace(1.0, 3.0, coordinate.size)
    stochastic_spectrum = frequency ** (-2.0 / 3.0)
    stochastic_tilt = np.gradient(np.log(stochastic_spectrum), np.log(frequency), edge_order=2)
    environment = 0.2 + 0.05 * np.sin(2.0 * np.pi * coordinate)
    base_velocity = 1.0
    group_velocity = base_velocity / (1.0 + environment)
    source = 0.5 + 0.1 * np.cos(np.pi * coordinate)
    transport = np.eye(coordinate.size)
    transport += 0.05 * np.diag(np.ones(coordinate.size - 1), 1)
    detected = transport @ source
    return RippleInput(
        coordinate=coordinate,
        waveform=waveform,
        memory_kernel=memory_kernel,
        memory_imprint=memory_imprint,
        flowpoint_parity=parity,
        boundary_mode=boundary_mode,
        conversion_gain=conversion_gain,
        converted_mode=converted_mode,
        amplitude=amplitude,
        shock_indicator=shock_indicator,
        frequency=frequency,
        stochastic_spectrum=stochastic_spectrum,
        stochastic_tilt=stochastic_tilt,
        environment=environment,
        base_velocity=base_velocity,
        group_velocity=group_velocity,
        source=source,
        transport_matrix=transport,
        detected=detected,
        shock_threshold=shock_threshold,
        tolerance=1e-10,
    )


def sample_inputs() -> dict[str, object]:
    sample = elastic_pi_ripple_sample()
    identifiers = (*A_IDS, *(item[0] for item in B_SPECS), C_ID)
    return {identifier: sample for identifier in identifiers}
