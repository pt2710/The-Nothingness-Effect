from pathlib import Path

import numpy as np

from equations.locality_driven_gravity import (
    LocalityGravityParams,
    compute_spiral_metrics,
    locality_force,
    locality_kernel,
    simulate_locality_spiral,
)
from simulations.run_locality_spiral_figure6 import run


def test_locality_kernel_bounds():
    values = locality_kernel(np.array([0.0, 1.0, 5.0]), sigma=2.0)
    assert np.all(values >= 0.0)
    assert np.all(values <= 1.0)
    assert values[0] == 1.0


def test_force_shape_and_finiteness():
    positions = np.array([[1.0, 0.0], [0.0, 2.0]])
    force = locality_force(positions, G_eff=0.2, sigma=2.0, eps=0.1, shear=0.05)
    assert force.shape == positions.shape
    assert np.all(np.isfinite(force))


def test_simulation_no_nan():
    result = simulate_locality_spiral(LocalityGravityParams(n_particles=30, steps=10), seed=4)
    assert np.isnan(result["history"]).sum() == 0


def test_spiral_metric_finite():
    result = simulate_locality_spiral(LocalityGravityParams(n_particles=30, steps=10), seed=4)
    metrics = compute_spiral_metrics(result["history"])
    assert np.isfinite(metrics["spiral_order_parameter"])
    assert metrics["nan_count"] == 0


def test_reproducible_seed():
    params = LocalityGravityParams(n_particles=30, steps=8)
    first = simulate_locality_spiral(params, seed=99)["history"]
    second = simulate_locality_spiral(params, seed=99)["history"]
    assert np.allclose(first, second)


def test_figure6_outputs_exist_after_runner(tmp_path: Path):
    result = run(tmp_path, quick=True)
    for key in ("figure", "data", "metrics", "metadata"):
        assert result[key].exists()
