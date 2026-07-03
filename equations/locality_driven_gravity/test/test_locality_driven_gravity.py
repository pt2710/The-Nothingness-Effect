from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from equations.artifact_io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz
from equations.locality_driven_gravity.locality_driven_gravity import (
    arm_phase_offsets,
    LocalityGravityParams,
    compare_spiral_arm_modes,
    compute_spiral_metrics,
    density_field,
    entropic_elastic_field,
    gravity_acceleration,
    initialize_spiral_bodies,
    locality_force,
    locality_kernel,
    simulate_spiral_arm_mode,
    simulate_locality_spiral,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def _write_test_artifacts() -> dict[str, Path]:
    params = LocalityGravityParams(n_particles=48, steps=18, grid_size=28, arm_mode=2)
    result = simulate_spiral_arm_mode(2, params=params, seed=123)
    metrics = compute_spiral_metrics(
        result["history"],
        velocity_history=result["velocity_history"],
        masses=result["masses"],
        body_types=result["body_types"],
        tension_field=result["tension_history"][-1],
        arm_mode=2,
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


def test_arm_mode_accepts_only_supported_values():
    for arm_mode in (2, 3, 4, "mixed"):
        result = initialize_spiral_bodies(LocalityGravityParams(n_particles=24, arm_mode=arm_mode), seed=31)
        assert "arm_mode_assignment" in result


def test_invalid_arm_mode_raises_value_error():
    try:
        initialize_spiral_bodies(LocalityGravityParams(n_particles=24, arm_mode="five"), seed=31)  # type: ignore[arg-type]
    except ValueError:
        pass
    else:
        raise AssertionError("Expected invalid arm_mode to raise ValueError.")


def test_arm_phase_offsets_produce_valid_two_arm_families():
    rng = np.random.default_rng(2710)
    bundle = arm_phase_offsets(rng, 200, 2)
    phase = np.mod(bundle["phase_offsets"], 2.0 * np.pi)
    allowed = np.array([0.0, np.pi])
    assert np.all(np.isclose(phase[:, None], allowed[None, :], atol=1e-8).any(axis=1))


def test_arm_phase_offsets_produce_valid_three_arm_families():
    rng = np.random.default_rng(2710)
    bundle = arm_phase_offsets(rng, 300, 3)
    phase = np.mod(bundle["phase_offsets"], 2.0 * np.pi)
    allowed = np.array([0.0, 2.0 * np.pi / 3.0, 4.0 * np.pi / 3.0])
    assert np.all(np.isclose(phase[:, None], allowed[None, :], atol=1e-8).any(axis=1))


def test_arm_phase_offsets_produce_valid_four_arm_families():
    rng = np.random.default_rng(2710)
    bundle = arm_phase_offsets(rng, 400, 4)
    phase = np.mod(bundle["phase_offsets"], 2.0 * np.pi)
    allowed = np.array([0.0, 0.5 * np.pi, np.pi, 1.5 * np.pi])
    assert np.all(np.isclose(phase[:, None], allowed[None, :], atol=1e-8).any(axis=1))


def test_mixed_arm_phase_offsets_include_multiple_modes_deterministically():
    rng = np.random.default_rng(2710)
    bundle = arm_phase_offsets(rng, 240, "mixed")
    assigned = np.asarray(bundle["assigned_modes"], dtype=int)
    assert len(np.unique(assigned)) >= 2


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
        arm_mode=2,
    )
    assert np.isfinite(metrics["spiral_order_parameter"])
    assert np.isfinite(metrics["mode_1_amplitude"])
    assert np.isfinite(metrics["mode_2_amplitude"])
    assert np.isfinite(metrics["mode_3_amplitude"])
    assert np.isfinite(metrics["mode_4_amplitude"])
    assert np.isfinite(metrics["dominant_mode"])
    assert np.isfinite(metrics["target_mode_amplitude"])
    assert np.isfinite(metrics["target_mode_ratio"])
    assert metrics["mode_2_amplitude"] > 0.0 or metrics["mode_3_amplitude"] > 0.0 or metrics["mode_4_amplitude"] > 0.0
    assert metrics["nan_count"] == 0


def test_simulation_no_nan():
    result = simulate_locality_spiral(LocalityGravityParams(n_particles=30, steps=10, grid_size=20), seed=4)
    assert np.isnan(result["history"]).sum() == 0
    assert np.isnan(result["density_history"]).sum() == 0
    assert np.isnan(result["tension_history"]).sum() == 0


def test_each_supported_arm_mode_simulation_returns_finite_outputs():
    for arm_mode in (2, 3, 4, "mixed"):
        result = simulate_spiral_arm_mode(arm_mode, params=LocalityGravityParams(n_particles=36, steps=16, grid_size=24, arm_mode=arm_mode), seed=41)
        assert np.all(np.isfinite(result["history"]))
        assert np.all(np.isfinite(result["velocity_history"]))
        assert np.all(np.isfinite(result["density_history"]))
        assert np.all(np.isfinite(result["tension_history"]))
        assert np.all(np.isfinite(result["entropy_history"]))
        for key in [
            "mode_1_amplitude",
            "mode_2_amplitude",
            "mode_3_amplitude",
            "mode_4_amplitude",
            "dominant_mode",
            "target_mode_amplitude",
            "target_mode_ratio",
        ]:
            assert np.isfinite(result["metrics"][key])


def test_compare_spiral_arm_modes_returns_all_requested_modes():
    results = compare_spiral_arm_modes(seed=2710, quick=True)
    assert set(results) == {"2", "3", "4", "mixed"}


def test_test_script_outputs_are_generated_locally():
    paths = _write_test_artifacts()
    for path in paths.values():
        assert path.exists()
        assert path.stat().st_size > 0
