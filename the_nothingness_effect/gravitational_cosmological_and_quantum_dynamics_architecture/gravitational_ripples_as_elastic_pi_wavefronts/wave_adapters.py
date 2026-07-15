"""Lightweight wave helpers adapted from development-only wave prototypes.

These helpers are reused as deterministic signal adapters for ringdown and
spectral toy projections. They remain illustrative utilities, not empirical
validation tools.
"""

from __future__ import annotations

import numpy as np


def fp_pi_wave(
    values: np.ndarray | float,
    *,
    scale: float = 1.0,
    frequency: float = 1.0,
    time: float = 0.0,
) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    return scale * np.sin(frequency * data + time * np.pi)


def fp_sine_wave(
    values: np.ndarray | float,
    *,
    scale: float = 1.0,
    frequency: float = 1.0,
    time: float = 0.0,
) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    return scale * np.sin(frequency * data + time)


def radial_wave_interference(
    radius: np.ndarray | float,
    *,
    time: float = 0.0,
    amplitude_1: float = 1.0,
    frequency_1: float = 1.0,
    amplitude_2: float = 0.35,
    frequency_2: float = 1.6,
    phase_2: float = np.pi / 2.0,
) -> np.ndarray:
    radial_coordinate = np.asarray(radius, dtype=float)
    wave_1 = fp_pi_wave(radial_coordinate, scale=amplitude_1, frequency=frequency_1, time=time)
    wave_2 = fp_pi_wave(
        radial_coordinate,
        scale=amplitude_2,
        frequency=frequency_2,
        time=time + phase_2 / np.pi,
    )
    return wave_1 + wave_2
