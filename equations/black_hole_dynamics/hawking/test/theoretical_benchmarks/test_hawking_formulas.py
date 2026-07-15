from __future__ import annotations

import numpy as np
import pytest

from equations.black_hole_dynamics.hawking.hawking_formulas import (
    hawking_evaporation_timescale,
    hawking_mass_loss_rate,
    hawking_power,
    hawking_temperature,
)


def test_positive_mass_gives_finite_hawking_values():
    masses = np.geomspace(1.0e11, 1.0e13, 4)
    assert np.all(np.isfinite(hawking_temperature(masses)))
    assert np.all(np.isfinite(hawking_power(masses)))
    assert np.all(np.isfinite(hawking_evaporation_timescale(masses)))
    assert np.all(np.isfinite(hawking_mass_loss_rate(masses)))


@pytest.mark.parametrize("mass", [0.0, -1.0])
def test_non_positive_mass_raises_value_error(mass: float):
    with pytest.raises(ValueError):
        hawking_temperature(mass)


def test_hawking_scalings_match_standard_exponents():
    masses = np.geomspace(1.0e11, 1.0e15, 8)
    slope_temperature, _ = np.polyfit(np.log(masses), np.log(hawking_temperature(masses)), deg=1)
    slope_power, _ = np.polyfit(np.log(masses), np.log(hawking_power(masses)), deg=1)
    slope_evaporation, _ = np.polyfit(np.log(masses), np.log(hawking_evaporation_timescale(masses)), deg=1)
    assert slope_temperature == pytest.approx(-1.0, abs=1e-9)
    assert slope_power == pytest.approx(-2.0, abs=1e-9)
    assert slope_evaporation == pytest.approx(3.0, abs=1e-9)


def test_mass_loss_rate_is_negative():
    masses = np.geomspace(1.0e11, 1.0e13, 5)
    assert np.all(hawking_mass_loss_rate(masses) < 0.0)
