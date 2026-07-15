from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from tne_runtime.artifacts.io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz
from equations.elastic_pi_ripples.elastic_pi_ripples import (
    RippleParams,
    elastic_pi_wave_step,
    laplacian_1d,
    simulate_elastic_pi_ripple,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def _write_test_artifacts() -> dict[str, Path]:
    result = simulate_elastic_pi_ripple(RippleParams(n=96, steps=40))
    fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)
    ax.plot(result["x"], result["history"][0], label="initial")
    ax.plot(result["x"], result["history"][-1], label="final")
    ax.set_title("Elastic-pi ripple test visualization")
    ax.set_xlabel("x")
    ax.set_ylabel("amplitude")
    ax.grid(True, alpha=0.25)
    ax.legend()
    figure = SCRIPT_DIR / "elastic_pi_ripples_test_visualization.png"
    data = SCRIPT_DIR / "elastic_pi_ripples_test_data.npz"
    results = SCRIPT_DIR / "elastic_pi_ripples_test_results.csv"
    save_figure(fig, figure)
    plt.close(fig)
    save_npz(data, x=result["x"], history=result["history"])
    save_csv(results, [{**result["metrics"], "claim_boundary": CLAIM_BOUNDARY}])
    return {"figure": figure, "data": data, "results": results}


def test_laplacian_constant_zero():
    assert np.allclose(laplacian_1d(np.ones(8), dx=0.5), 0.0)


def test_wave_step_shape():
    u_prev = np.zeros(10)
    u = np.zeros(10)
    assert elastic_pi_wave_step(u_prev, u, 0.01, 0.1, 1.0, 0.1, -0.01).shape == u.shape


def test_damping_reduces_energy_for_xi_zero():
    damped = simulate_elastic_pi_ripple(RippleParams(n=80, steps=80, xi=0.0, gamma=0.2))
    assert damped["metrics"]["final_energy"] < damped["metrics"]["initial_energy"]


def test_nonlinear_xi_changes_late_waveform():
    base = simulate_elastic_pi_ripple(RippleParams(n=80, steps=60, xi=0.0))["history"][-1]
    nonlinear = simulate_elastic_pi_ripple(RippleParams(n=80, steps=60, xi=-0.2))["history"][-1]
    assert not np.allclose(base, nonlinear)


def test_simulation_no_nan():
    result = simulate_elastic_pi_ripple(RippleParams(n=80, steps=30))
    assert result["metrics"]["nan_count"] == 0


def test_test_script_outputs_are_generated_locally():
    paths = _write_test_artifacts()
    for path in paths.values():
        assert path.exists()
        assert path.stat().st_size > 0
