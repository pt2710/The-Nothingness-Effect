from pathlib import Path

import numpy as np

from equations.elastic_pi_ripples import (
    RippleParams,
    elastic_pi_wave_step,
    laplacian_1d,
    simulate_elastic_pi_ripple,
)
from simulations.run_elastic_pi_ripple_figure7 import run


def test_laplacian_constant_zero():
    assert np.allclose(laplacian_1d(np.ones(8), dx=0.5), 0.0)


def test_wave_step_shape():
    u_prev = np.zeros(10)
    u = np.zeros(10)
    assert elastic_pi_wave_step(u_prev, u, 0.01, 0.1, 1.0, 0.1, -0.01).shape == u.shape


def test_damping_reduces_energy_for_xi_zero():
    damped = simulate_elastic_pi_ripple(RippleParams(n=80, steps=80, xi=0.0, gamma=0.2))
    metrics = damped["metrics"]
    assert metrics["final_energy"] < metrics["initial_energy"]


def test_nonlinear_xi_changes_late_waveform():
    base = simulate_elastic_pi_ripple(RippleParams(n=80, steps=60, xi=0.0))["history"][-1]
    nonlinear = simulate_elastic_pi_ripple(RippleParams(n=80, steps=60, xi=-0.2))["history"][-1]
    assert not np.allclose(base, nonlinear)


def test_simulation_no_nan():
    result = simulate_elastic_pi_ripple(RippleParams(n=80, steps=30))
    assert result["metrics"]["nan_count"] == 0


def test_figure7_outputs_exist_after_runner(tmp_path: Path):
    result = run(tmp_path, quick=True)
    for key in ("figure", "data", "metrics", "metadata"):
        assert result[key].exists()
