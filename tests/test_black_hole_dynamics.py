from pathlib import Path

import numpy as np

from equations.black_hole_dynamics import (
    BlackHoleParams,
    elastic_pi_profile,
    gravitational_memory_kernel,
    hawking_like_flux,
    hawking_like_temperature,
    horizon_indicator,
    simulate_black_hole_dynamics,
)
from simulations.run_black_hole_dynamics_section18 import run


def test_elastic_pi_positive():
    profile = elastic_pi_profile(np.array([0.0, 1.0, 2.0]), K_D=2.0)
    assert np.all(profile > 0.0)


def test_horizon_indicator_detects_threshold():
    r = np.array([1.0, 2.0, 3.0])
    pi_E = np.array([0.8, 0.3, 0.2])
    assert horizon_indicator(r, pi_E, threshold=0.5) == 2.0


def test_hawking_temperature_nonnegative():
    temperature = hawking_like_temperature(np.array([-1.0, 0.0, 2.0]), K_D=2.0)
    assert np.all(temperature >= 0.0)


def test_flux_monotone_with_temperature():
    flux = hawking_like_flux(np.array([0.1, 0.2, 0.3]))
    assert np.all(np.diff(flux) > 0.0)


def test_memory_kernel_finite():
    memory = gravitational_memory_kernel(np.array([1.0, 0.5, 0.25]), decay=0.9)
    assert np.all(np.isfinite(memory))


def test_simulation_outputs_shapes():
    result = simulate_black_hole_dynamics(BlackHoleParams(grid_size=48, steps=12))
    assert result["pi_E_time"].shape == (12, 48)
    assert result["memory"].shape == (12,)
    assert result["metrics"]["stable"]


def test_section18_outputs_exist_after_runner(tmp_path: Path):
    result = run(tmp_path, quick=True)
    for path in result["figures"].values():
        assert path.exists()
    for key in ("data", "metrics", "feasibility_metrics", "metadata"):
        assert result[key].exists()
