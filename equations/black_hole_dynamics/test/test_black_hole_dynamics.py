from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from equations.artifact_io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz
from equations.black_hole_dynamics.black_hole_dynamics import (
    BlackHoleParams,
    elastic_pi_profile,
    gravitational_memory_kernel,
    hawking_like_flux,
    hawking_like_temperature,
    horizon_indicator,
    simulate_black_hole_dynamics,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def _write_test_artifacts() -> dict[str, Path]:
    result = simulate_black_hole_dynamics(BlackHoleParams(grid_size=64, steps=16))
    fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)
    ax.plot(result["r"], result["pi_E_time"][0], label="initial")
    ax.plot(result["r"], result["pi_E_time"][-1], label="final")
    ax.set_title("Black-hole dynamics test visualization")
    ax.set_xlabel("r")
    ax.set_ylabel("normalized pi_E")
    ax.grid(True, alpha=0.25)
    ax.legend()
    figure = SCRIPT_DIR / "black_hole_dynamics_test_visualization.png"
    data = SCRIPT_DIR / "black_hole_dynamics_test_data.npz"
    results = SCRIPT_DIR / "black_hole_dynamics_test_results.csv"
    save_figure(fig, figure)
    plt.close(fig)
    save_npz(data, r=result["r"], pi_E_time=result["pi_E_time"], memory=result["memory"])
    save_csv(results, [{**result["metrics"], "claim_boundary": CLAIM_BOUNDARY}])
    return {"figure": figure, "data": data, "results": results}


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


def test_test_script_outputs_are_generated_locally():
    paths = _write_test_artifacts()
    for path in paths.values():
        assert path.exists()
        assert path.stat().st_size > 0
