from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from equations.artifact_io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz
from equations.locality_driven_gravity.locality_driven_gravity import (
    LocalityGravityParams,
    compute_spiral_metrics,
    density_field,
    entropic_elastic_field,
    gravity_acceleration,
    initialize_spiral_bodies,
    locality_force,
    locality_kernel,
    simulate_locality_spiral,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def _write_test_artifacts() -> dict[str, Path]:
    params = LocalityGravityParams(n_particles=48, steps=18, grid_size=28)
    result = simulate_locality_spiral(params, seed=123)
    metrics = compute_spiral_metrics(
        result["history"],
        velocity_history=result["velocity_history"],
        masses=result["masses"],
        body_types=result["body_types"],
        tension_field=result["tension_history"][-1],
    )
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
    save_npz(
        data,
        history=result["history"],
        velocity_history=result["velocity_history"],
        density_history=result["density_history"],
        tension_history=result["tension_history"],
        masses=result["masses"],
    )
    save_csv(results, [{**metrics, "claim_boundary": CLAIM_BOUNDARY}])
    return {"figure": figure, "data": data, "results": results}


def test_locality_kernel_bounds():
    values = locality_kernel(np.array([0.0, 1.0, 5.0]), sigma=2.0)
    assert np.all(values >= 0.0)
    assert np.all(values <= 1.0)
    assert values[0] == 1.0


def test_body_initialization_is_deterministic():
    params = LocalityGravityParams(n_particles=32)
    first = initialize_spiral_bodies(params, seed=99)
    second = initialize_spiral_bodies(params, seed=99)
    assert np.allclose(first["positions"], second["positions"])
    assert np.allclose(first["velocities"], second["velocities"])
    assert np.allclose(first["masses"], second["masses"])


def test_all_bodies_have_positive_mass():
    initialized = initialize_spiral_bodies(LocalityGravityParams(n_particles=32), seed=17)
    assert np.all(np.asarray(initialized["masses"], dtype=float) > 0.0)


def test_density_field_shape_and_finiteness():
    params = LocalityGravityParams(n_particles=24, grid_size=24)
    initialized = initialize_spiral_bodies(params, seed=3)
    field = density_field(initialized["positions"], initialized["masses"], params)
    assert field["density"].shape == (params.grid_size, params.grid_size)
    assert np.all(np.isfinite(field["density"]))


def test_gravity_acceleration_finite():
    params = LocalityGravityParams(n_particles=24)
    initialized = initialize_spiral_bodies(params, seed=5)
    accel = gravity_acceleration(initialized["positions"], initialized["masses"], initialized["softening"], params.G_eff, params.eps)
    assert accel.shape == initialized["positions"].shape
    assert np.all(np.isfinite(accel))


def test_locality_force_shape_and_finiteness():
    params = LocalityGravityParams(n_particles=24)
    initialized = initialize_spiral_bodies(params, seed=7)
    force = locality_force(
        initialized["positions"],
        masses=initialized["masses"],
        G_eff=params.G_eff,
        sigma=params.sigma,
        eps=params.eps,
        shear=params.shear,
        softening=initialized["softening"],
    )
    assert force.shape == initialized["positions"].shape
    assert np.all(np.isfinite(force))


def test_entropic_elastic_field_finite():
    params = LocalityGravityParams(n_particles=24, grid_size=24)
    initialized = initialize_spiral_bodies(params, seed=11)
    field = entropic_elastic_field(initialized["positions"], initialized["velocities"], initialized["masses"], None, params)
    assert np.all(np.isfinite(field["entropy"]))
    assert np.all(np.isfinite(field["tension"]))
    assert np.all(np.isfinite(field["shear"]))


def test_high_mass_density_increases_local_tension():
    params = LocalityGravityParams(n_particles=12, grid_size=20)
    initialized = initialize_spiral_bodies(params, seed=13)
    positions = np.asarray(initialized["positions"], dtype=float)
    masses = np.asarray(initialized["masses"], dtype=float)
    velocities = np.asarray(initialized["velocities"], dtype=float)
    base_field = entropic_elastic_field(positions, velocities, masses, None, params)
    boosted_masses = masses.copy()
    boosted_masses[1:5] *= 2.5
    boosted_field = entropic_elastic_field(positions, velocities, boosted_masses, None, params)
    focus = np.linalg.norm(positions[:, :], axis=1).argsort()[:4]
    axis = np.asarray(base_field["axis"], dtype=float)

    def sample_local_mean(field: dict[str, np.ndarray]) -> float:
        samples = []
        tension = np.asarray(field["tension"], dtype=float)
        for body_index in focus:
            x = positions[body_index, 0]
            y = positions[body_index, 1]
            x_idx = int(np.argmin(np.abs(axis - x)))
            y_idx = int(np.argmin(np.abs(axis - y)))
            x0 = max(0, x_idx - 1)
            x1 = min(len(axis), x_idx + 2)
            y0 = max(0, y_idx - 1)
            y1 = min(len(axis), y_idx + 2)
            samples.append(float(np.mean(tension[y0:y1, x0:x1])))
        return float(np.mean(samples))

    assert sample_local_mean(boosted_field) > sample_local_mean(base_field)


def test_total_mass_is_conserved():
    params = LocalityGravityParams(n_particles=30, steps=14, grid_size=24)
    result = simulate_locality_spiral(params, seed=21)
    initial_mass = float(np.sum(result["masses"]))
    final_mass = float(np.sum(result["masses"]))
    assert np.isclose(initial_mass, final_mass)


def test_angular_momentum_drift_reported():
    params = LocalityGravityParams(n_particles=30, steps=14, grid_size=24)
    result = simulate_locality_spiral(params, seed=23)
    metrics = compute_spiral_metrics(
        result["history"],
        velocity_history=result["velocity_history"],
        masses=result["masses"],
        body_types=result["body_types"],
        tension_field=result["tension_history"][-1],
    )
    assert np.isfinite(metrics["angular_momentum_drift"])
    assert abs(metrics["angular_momentum_drift"]) < 5.0


def test_spiral_metrics_are_finite_and_modes_nonzero():
    params = LocalityGravityParams(n_particles=36, steps=16, grid_size=26)
    result = simulate_locality_spiral(params, seed=29)
    metrics = compute_spiral_metrics(
        result["history"],
        velocity_history=result["velocity_history"],
        masses=result["masses"],
        body_types=result["body_types"],
        tension_field=result["tension_history"][-1],
    )
    assert np.isfinite(metrics["spiral_order_parameter"])
    assert np.isfinite(metrics["mode_2_amplitude"])
    assert np.isfinite(metrics["mode_3_amplitude"])
    assert metrics["mode_2_amplitude"] > 0.0 or metrics["mode_3_amplitude"] > 0.0
    assert metrics["nan_count"] == 0


def test_simulation_no_nan():
    result = simulate_locality_spiral(LocalityGravityParams(n_particles=30, steps=10, grid_size=20), seed=4)
    assert np.isnan(result["history"]).sum() == 0
    assert np.isnan(result["density_history"]).sum() == 0
    assert np.isnan(result["tension_history"]).sum() == 0


def test_test_script_outputs_are_generated_locally():
    paths = _write_test_artifacts()
    for path in paths.values():
        assert path.exists()
        assert path.stat().st_size > 0
