"""Standard Hawking benchmark formulas with conservative claim boundaries."""

from __future__ import annotations

import numpy as np


HBAR = 1.054_571_817e-34
C = 299_792_458.0
G = 6.674_30e-11
K_B = 1.380_649e-23


def _positive_mass_array(mass_kg: np.ndarray | float) -> np.ndarray:
    values = np.asarray(mass_kg, dtype=float)
    if np.any(values <= 0.0):
        raise ValueError("mass_kg must be strictly positive.")
    return values


def hawking_temperature(mass_kg: np.ndarray | float) -> np.ndarray:
    mass = _positive_mass_array(mass_kg)
    return HBAR * C**3 / (8.0 * np.pi * G * mass * K_B)


def hawking_power(mass_kg: np.ndarray | float) -> np.ndarray:
    mass = _positive_mass_array(mass_kg)
    return HBAR * C**6 / (15_360.0 * np.pi * G**2 * mass**2)


def hawking_mass_loss_rate(mass_kg: np.ndarray | float) -> np.ndarray:
    return -hawking_power(mass_kg) / C**2


def hawking_evaporation_timescale(mass_kg: np.ndarray | float) -> np.ndarray:
    mass = _positive_mass_array(mass_kg)
    return 5_120.0 * np.pi * G**2 * mass**3 / (HBAR * C**4)


def normalized_planck_spectrum(x: np.ndarray | float) -> np.ndarray:
    values = np.asarray(x, dtype=float)
    clipped = np.clip(values, 1e-9, 64.0)
    spectrum = clipped**3 / (np.exp(clipped) - 1.0)
    return spectrum / (float(np.max(spectrum)) + 1e-12)
