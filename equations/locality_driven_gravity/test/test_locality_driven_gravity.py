from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from equations.artifact_io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz
from equations.locality_driven_gravity.locality_driven_gravity import (
    LocalityGravityParams,
    compute_spiral_metrics,
    locality_force,
    locality_kernel,
    simulate_locality_spiral,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def _write_test_artifacts() -> dict[str, Path]:
    result = simulate_locality_spiral(LocalityGravityParams(n_particles=40, steps=12), seed=123)
    metrics = compute_spiral_metrics(result["history"])
    final = result["history"][-1]
    fig, ax = plt.subplots(figsize=(5, 5), constrained_layout=True)
    ax.scatter(final[:, 0], final[:, 1], s=12, color="#f58518")
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Locality-driven gravity test visualization")
    ax.grid(True, alpha=0.25)
    figure = SCRIPT_DIR / "locality_driven_gravity_test_visualization.png"
    data = SCRIPT_DIR / "locality_driven_gravity_test_data.npz"
    results = SCRIPT_DIR / "locality_driven_gravity_test_results.csv"
    save_figure(fig, figure)
    plt.close(fig)
    save_npz(data, history=result["history"])
    save_csv(results, [{**metrics, "claim_boundary": CLAIM_BOUNDARY}])
    return {"figure": figure, "data": data, "results": results}


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


def test_test_script_outputs_are_generated_locally():
    paths = _write_test_artifacts()
    for path in paths.values():
        assert path.exists()
        assert path.stat().st_size > 0
