"""Observable mapping for fixture-backed spiral rotation comparisons."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from empirical.io import fixture_path, read_csv_rows
from empirical.metrics import metric_bundle, rmse
from empirical.visualization.plot_empirical_comparisons import plot_scalar_diagnostics, plot_series_comparison
from equations.locality_driven_gravity.locality_driven_gravity import LocalityGravityParams, compute_spiral_metrics, simulate_locality_spiral


@lru_cache(maxsize=4)
def _model_profiles(seed: int = 2710) -> dict[str, Any]:
    params = LocalityGravityParams(n_particles=240, steps=220, shear=0.18, damping=0.995)
    result = simulate_locality_spiral(params=params, seed=seed)
    final_pos = np.asarray(result["positions"], dtype=float)
    final_vel = np.asarray(result["velocities"], dtype=float)
    radii = np.linalg.norm(final_pos, axis=1)
    tangent = np.column_stack([-final_pos[:, 1], final_pos[:, 0]])
    tangent /= (np.linalg.norm(tangent, axis=1, keepdims=True) + 1e-12)
    tangential_velocity = np.abs(np.sum(final_vel * tangent, axis=1))
    bins = np.linspace(max(1e-6, radii.min()), radii.max(), 9)
    bin_ids = np.digitize(radii, bins) - 1
    radial_centers = []
    velocity_profile = []
    density_profile = []
    for bin_index in range(len(bins) - 1):
        mask = bin_ids == bin_index
        if not np.any(mask):
            continue
        radial_centers.append(float(np.mean(radii[mask])))
        velocity_profile.append(float(np.mean(tangential_velocity[mask])))
        density_profile.append(float(np.sum(mask)))
    return {
        "params": params.__dict__,
        "radial_centers": np.asarray(radial_centers, dtype=float),
        "velocity_profile": np.asarray(velocity_profile, dtype=float),
        "density_profile": np.asarray(density_profile, dtype=float),
        "spiral_metrics": compute_spiral_metrics(result["history"]),
    }


def prepare_empirical_observable(path: str | Path | None = None) -> dict[str, Any]:
    rows = read_csv_rows(path or fixture_path("galaxy_rotation_fixture.csv"))
    return {
        "radius": np.asarray([float(row["radius"]) for row in rows], dtype=float),
        "velocity": np.asarray([float(row["velocity"]) for row in rows], dtype=float),
        "velocity_uncertainty": np.asarray([float(row["velocity_uncertainty"]) for row in rows], dtype=float),
        "galaxy_id": [row["galaxy_id"] for row in rows],
        "source_status": [row["source_status"] for row in rows],
    }


def fit_parameters(empirical: dict[str, Any], seed: int = 2710) -> dict[str, Any]:
    profile = _model_profiles(seed=seed)
    model_r = profile["radial_centers"]
    model_v = profile["velocity_profile"]
    observed_r = np.asarray(empirical["radius"], dtype=float)
    observed_v = np.asarray(empirical["velocity"], dtype=float)
    base_scale = float(np.max(observed_r) / (np.max(model_r) + 1e-12))
    best = {
        "radius_scale": base_scale,
        "velocity_scale": 1.0,
        "score": float("inf"),
        "profile": profile,
    }
    for radius_scale in np.linspace(0.7 * base_scale, 1.3 * base_scale, 41):
        scaled_r = model_r * radius_scale
        interp = np.interp(observed_r, scaled_r, model_v, left=model_v[0], right=model_v[-1])
        velocity_scale = float(np.dot(observed_v, interp) / (np.dot(interp, interp) + 1e-12))
        predicted = velocity_scale * interp
        score = rmse(observed_v, predicted)
        if score < best["score"]:
            best = {
                "radius_scale": float(radius_scale),
                "velocity_scale": float(velocity_scale),
                "score": float(score),
                "profile": profile,
            }
    return best


def prepare_model_prediction(empirical: dict[str, Any], fitted_parameters: dict[str, Any] | None = None) -> dict[str, Any]:
    fit = fitted_parameters or fit_parameters(empirical)
    profile = fit["profile"]
    scaled_r = profile["radial_centers"] * fit["radius_scale"]
    model_velocity = profile["velocity_profile"] * fit["velocity_scale"]
    observed_r = np.asarray(empirical["radius"], dtype=float)
    predicted_velocity = np.interp(observed_r, scaled_r, model_velocity, left=model_velocity[0], right=model_velocity[-1])
    coeffs = np.polyfit(observed_r, np.asarray(empirical["velocity"], dtype=float), deg=1)
    baseline = coeffs[0] * observed_r + coeffs[1]
    velocity_smoothness_proxy = float(1.0 / (1.0 + np.std(np.diff(np.asarray(empirical["velocity"], dtype=float)))))
    return {
        "tne_prediction": predicted_velocity,
        "baseline_prediction": baseline,
        "scaled_radius_profile": scaled_r,
        "scaled_velocity_profile": model_velocity,
        "density_profile": np.asarray(profile["density_profile"], dtype=float),
        "spiral_order_parameter": float(profile["spiral_metrics"]["spiral_order_parameter"]),
        "velocity_smoothness_proxy": velocity_smoothness_proxy,
        "fitted_parameters": {
            "radius_scale": float(fit["radius_scale"]),
            "velocity_scale": float(fit["velocity_scale"]),
        },
    }


def compute_residuals(empirical: dict[str, Any], prediction: dict[str, Any]) -> dict[str, np.ndarray]:
    observed = np.asarray(empirical["velocity"], dtype=float)
    return {
        "tne_residual": np.asarray(prediction["tne_prediction"], dtype=float) - observed,
        "baseline_residual": np.asarray(prediction["baseline_prediction"], dtype=float) - observed,
    }


def compute_metrics(empirical: dict[str, Any], prediction: dict[str, Any], residuals: dict[str, np.ndarray]) -> dict[str, Any]:
    metrics = metric_bundle(
        observed=np.asarray(empirical["velocity"], dtype=float),
        predicted=np.asarray(prediction["tne_prediction"], dtype=float),
        uncertainty=np.asarray(empirical["velocity_uncertainty"], dtype=float),
        n_params=2,
        baseline=np.asarray(prediction["baseline_prediction"], dtype=float),
        baseline_params=2,
    )
    source_status = sorted(set(empirical.get("source_status", ["fixture_only"])))
    metrics["data_status"] = source_status[0] if len(source_status) == 1 else "mixed"
    metrics["baseline_model"] = "linear_rotation_baseline"
    metrics["spiral_order_parameter"] = float(prediction["spiral_order_parameter"])
    metrics["velocity_smoothness_proxy"] = float(prediction["velocity_smoothness_proxy"])
    return metrics


def plot_comparison(empirical: dict[str, Any], prediction: dict[str, Any], output_path: str | Path | dict[str, str | Path]):
    if isinstance(output_path, dict):
        curve_path = output_path["curve"]
        morphology_path = output_path["morphology"]
    else:
        curve_path = output_path
        morphology_path = Path(output_path).with_name("spiral_morphology_comparison.png")
    curve = plot_series_comparison(
        x=np.asarray(empirical["radius"], dtype=float),
        observed=np.asarray(empirical["velocity"], dtype=float),
        predicted=np.asarray(prediction["tne_prediction"], dtype=float),
        baseline=np.asarray(prediction["baseline_prediction"], dtype=float),
        uncertainty=np.asarray(empirical["velocity_uncertainty"], dtype=float),
        output_path=curve_path,
        title="Spiral rotation comparison",
        xlabel="radius",
        ylabel="velocity",
        baseline_label="linear baseline",
    )
    morphology = plot_scalar_diagnostics(
        labels=["model spiral order", "fixture velocity smoothness"],
        values=[float(prediction["spiral_order_parameter"]), float(prediction["velocity_smoothness_proxy"])],
        output_path=morphology_path,
        title="Spiral morphology diagnostic",
        ylabel="derived comparison metric",
    )
    return [curve, morphology]
