"""Observable mapping for finite illustrative spiral rotation comparisons."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from empirical.io import fixture_path, read_csv_rows
from empirical.metrics import metric_bundle, rmse
from tne_runtime.artifacts.io import save_figure
from equations.locality_driven_gravity.locality_driven_gravity import (
    LocalityGravityParams,
    compute_spiral_metrics,
    radial_velocity_profile,
    simulate_locality_spiral,
)


SWEEP_LEVELS: dict[str, dict[str, list[float] | list[int]]] = {
    "quick": {
        "shear": [0.12, 0.2],
        "sigma": [2.4, 3.0],
        "damping": [0.992],
        "steps": [200],
        "G_eff": [0.24, 0.34],
        "radial_scale": [2.6, 3.2],
        "aggregation_mix": [0.3, 0.6],
        "radius_scale_factor": [0.9, 1.0, 1.1],
    },
    "standard": {
        "shear": [0.1, 0.2],
        "sigma": [2.2, 3.0],
        "damping": [0.988, 0.994],
        "steps": [180, 240],
        "G_eff": [0.22, 0.34],
        "radial_scale": [2.8, 3.6],
        "aggregation_mix": [0.0, 0.5, 1.0],
        "radius_scale_factor": [0.88, 1.0, 1.12],
    },
    "extended": {
        "shear": [0.08, 0.14, 0.2, 0.28],
        "sigma": [2.0, 2.6, 3.2],
        "damping": [0.986, 0.991, 0.996],
        "steps": [180, 220, 260],
        "G_eff": [0.18, 0.26, 0.34],
        "radial_scale": [2.6, 3.2, 3.8],
        "aggregation_mix": [0.0, 0.33, 0.66, 1.0],
        "radius_scale_factor": [0.82, 0.94, 1.06, 1.18],
    },
}


def _moving_average(values: np.ndarray, window: int = 3) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    weights = np.ones(window, dtype=float) / float(window)
    return np.convolve(data, weights, mode="same")


def _baseline_family(radius: np.ndarray, velocity: np.ndarray) -> dict[str, np.ndarray]:
    observed_r = np.asarray(radius, dtype=float)
    observed_v = np.asarray(velocity, dtype=float)
    coeffs = np.polyfit(observed_r, observed_v, deg=1)
    linear = coeffs[0] * observed_r + coeffs[1]
    flat = np.full_like(observed_r, float(np.mean(observed_v)))
    smoothed = _moving_average(observed_v, window=3)
    return {
        "linear": linear,
        "flat": flat,
        "smoothed_reference": smoothed,
    }


def _galaxy_slices(galaxy_ids: list[str]) -> list[tuple[str, np.ndarray]]:
    slices: list[tuple[str, np.ndarray]] = []
    for galaxy_id in dict.fromkeys(galaxy_ids):
        mask = np.asarray([item == galaxy_id for item in galaxy_ids], dtype=bool)
        slices.append((galaxy_id, mask))
    return slices


def subset_empirical(empirical: dict[str, Any], galaxy_ids: set[str]) -> dict[str, Any]:
    mask = np.asarray([galaxy_id in galaxy_ids for galaxy_id in empirical["galaxy_id"]], dtype=bool)
    subset: dict[str, Any] = {}
    for key, value in empirical.items():
        if isinstance(value, np.ndarray) and value.shape and value.shape[0] == mask.shape[0]:
            subset[key] = value[mask]
        elif isinstance(value, list) and len(value) == mask.shape[0]:
            subset[key] = [item for item, keep in zip(value, mask, strict=True) if keep]
        else:
            subset[key] = value
    return subset


@lru_cache(maxsize=256)
def _profile_for_params(
    shear: float,
    sigma: float,
    damping: float,
    steps: int,
    G_eff: float,
    radial_scale: float,
    arm_mode: int | str,
) -> dict[str, Any]:
    n_particles = 120 if steps <= 200 else 156
    grid_size = 28 if steps <= 200 else 34
    params = LocalityGravityParams(
        n_particles=n_particles,
        steps=steps,
        shear=shear,
        sigma=sigma,
        damping=damping,
        G_eff=G_eff,
        radial_scale=radial_scale,
        grid_size=grid_size,
        central_mass=205.0 if steps <= 200 else 220.0,
        arm_mode=arm_mode,  # type: ignore[arg-type]
    )
    result = simulate_locality_spiral(params=params, seed=2710)
    profile = radial_velocity_profile(result["positions"], result["velocities"], result["masses"], n_bins=10)
    return {
        "params": params.__dict__,
        "profile": profile,
        "spiral_metrics": result["metrics"],
        "masses": np.asarray(result["masses"], dtype=float),
    }


def prepare_empirical_observable(path: str | Path | None = None) -> dict[str, Any]:
    rows = read_csv_rows(path or fixture_path("galaxy_rotation_fixture.csv"))
    radius = np.asarray([float(row["radius"]) for row in rows], dtype=float)
    velocity = np.asarray([float(row["velocity"]) for row in rows], dtype=float)
    return {
        "radius": radius,
        "velocity": velocity,
        "velocity_uncertainty": np.asarray([float(row["velocity_uncertainty"]) for row in rows], dtype=float),
        "radius_kpc": np.asarray([float(row.get("radius_kpc", row["radius"])) for row in rows], dtype=float),
        "velocity_kms": np.asarray([float(row.get("velocity_kms", row["velocity"])) for row in rows], dtype=float),
        "velocity_uncertainty_kms": np.asarray(
            [float(row.get("velocity_uncertainty_kms", row["velocity_uncertainty"])) for row in rows],
            dtype=float,
        ),
        "galaxy_id": [row["galaxy_id"] for row in rows],
        "source_status": [row["source_status"] for row in rows],
    }


def _best_local_galaxy_fit(
    observed_r: np.ndarray,
    observed_v: np.ndarray,
    profile: dict[str, np.ndarray],
    grid: dict[str, list[float] | list[int]],
) -> dict[str, Any]:
    base_radius_scale = float(np.max(observed_r) / (np.max(profile["radial_centers"]) + 1e-12))
    best_local: dict[str, Any] | None = None
    for aggregation_mix in grid["aggregation_mix"]:
        combined_velocity = (
            float(aggregation_mix) * profile["mean_tangential_velocity"]
            + (1.0 - float(aggregation_mix)) * profile["median_tangential_velocity"]
        )
        for radius_factor in grid["radius_scale_factor"]:
            radius_scale_fit = base_radius_scale * float(radius_factor)
            scaled_radius = profile["radial_centers"] * radius_scale_fit
            interp = np.interp(observed_r, scaled_radius, combined_velocity, left=combined_velocity[0], right=combined_velocity[-1])
            velocity_scale = float(np.dot(observed_v, interp) / (np.dot(interp, interp) + 1e-12))
            predicted = velocity_scale * interp
            score = rmse(observed_v, predicted)
            candidate = {
                "radius_scale": float(radius_scale_fit),
                "velocity_scale": float(velocity_scale),
                "aggregation_mix": float(aggregation_mix),
                "predicted": predicted,
                "score": float(score),
            }
            if best_local is None or candidate["score"] < best_local["score"]:
                best_local = candidate
    assert best_local is not None
    return best_local


def fit_parameters(
    empirical: dict[str, Any],
    parameter_sweep_level: str = "standard",
    seed: int = 2710,
    arm_modes: tuple[int | str, ...] = (2, 3, 4, "mixed"),
) -> dict[str, Any]:
    del seed
    grid = SWEEP_LEVELS[parameter_sweep_level]
    observed_r = np.asarray(empirical["radius"], dtype=float)
    observed_v = np.asarray(empirical["velocity"], dtype=float)
    galaxy_slices = _galaxy_slices(empirical["galaxy_id"])
    baselines: dict[str, dict[str, np.ndarray]] = {}
    selected_baselines: dict[str, str] = {}
    baseline_prediction = np.zeros_like(observed_v)
    flat_prediction = np.zeros_like(observed_v)
    linear_prediction = np.zeros_like(observed_v)
    smoothed_prediction = np.zeros_like(observed_v)
    baseline_scores: dict[str, dict[str, float]] = {}
    for galaxy_id, mask in galaxy_slices:
        local_baselines = _baseline_family(observed_r[mask], observed_v[mask])
        baselines[galaxy_id] = local_baselines
        flat_score = rmse(observed_v[mask], local_baselines["flat"])
        linear_score = rmse(observed_v[mask], local_baselines["linear"])
        selected = "flat_rotation_baseline" if flat_score < linear_score else "linear_rotation_baseline"
        selected_baselines[galaxy_id] = selected
        baseline_scores[galaxy_id] = {"flat_RMSE": float(flat_score), "linear_RMSE": float(linear_score)}
        baseline_prediction[mask] = local_baselines["flat"] if selected.startswith("flat") else local_baselines["linear"]
        flat_prediction[mask] = local_baselines["flat"]
        linear_prediction[mask] = local_baselines["linear"]
        smoothed_prediction[mask] = local_baselines["smoothed_reference"]

    best: dict[str, Any] | None = None
    for shear in grid["shear"]:
        for sigma in grid["sigma"]:
            for damping in grid["damping"]:
                for steps in grid["steps"]:
                    for gravity in grid["G_eff"]:
                        for radial_scale in grid["radial_scale"]:
                            for arm_mode in arm_modes:
                                bundle = _profile_for_params(shear, sigma, damping, int(steps), gravity, radial_scale, arm_mode)
                                profile = bundle["profile"]
                                if len(profile["radial_centers"]) < 3:
                                    continue
                                combined_prediction = np.zeros_like(observed_v)
                                per_galaxy: dict[str, dict[str, float]] = {}
                                for galaxy_id, mask in galaxy_slices:
                                    local_fit = _best_local_galaxy_fit(observed_r[mask], observed_v[mask], profile, grid)
                                    combined_prediction[mask] = local_fit["predicted"]
                                    per_galaxy[galaxy_id] = {
                                        "radius_scale": float(local_fit["radius_scale"]),
                                        "velocity_scale": float(local_fit["velocity_scale"]),
                                        "aggregation_mix": float(local_fit["aggregation_mix"]),
                                        "score": float(local_fit["score"]),
                                    }
                                score = rmse(observed_v, combined_prediction)
                                candidate = {
                                    "score": float(score),
                                    "profile": bundle,
                                    "per_galaxy": per_galaxy,
                                    "arm_mode": arm_mode,
                                }
                                if best is None or candidate["score"] < best["score"]:
                                    best = candidate
    assert best is not None
    best["baselines"] = baselines
    best["selected_baselines"] = selected_baselines
    best["baseline_scores"] = baseline_scores
    best["baseline_prediction"] = baseline_prediction
    best["flat_prediction"] = flat_prediction
    best["linear_prediction"] = linear_prediction
    best["smoothed_prediction"] = smoothed_prediction
    best["parameter_sweep_level"] = parameter_sweep_level
    best["arm_modes_tested"] = [str(mode) for mode in arm_modes]
    return best


def holdout_diagnostics(empirical: dict[str, Any], parameter_sweep_level: str = "standard") -> dict[str, dict[str, float | str]]:
    galaxy_ids = list(dict.fromkeys(empirical["galaxy_id"]))
    if len(galaxy_ids) < 3:
        return {}
    diagnostics: dict[str, dict[str, float | str]] = {}
    for holdout_id in galaxy_ids:
        training_ids = {galaxy_id for galaxy_id in galaxy_ids if galaxy_id != holdout_id}
        train_empirical = subset_empirical(empirical, training_ids)
        holdout_empirical = subset_empirical(empirical, {holdout_id})
        fitted = fit_parameters(train_empirical, parameter_sweep_level=parameter_sweep_level)
        profile = fitted["profile"]["profile"]
        mean_radius_scale = float(np.mean([entry["radius_scale"] for entry in fitted["per_galaxy"].values()]))
        mean_velocity_scale = float(np.mean([entry["velocity_scale"] for entry in fitted["per_galaxy"].values()]))
        mean_aggregation_mix = float(np.mean([entry["aggregation_mix"] for entry in fitted["per_galaxy"].values()]))
        combined_velocity = mean_aggregation_mix * profile["mean_tangential_velocity"] + (1.0 - mean_aggregation_mix) * profile["median_tangential_velocity"]
        scaled_radius = profile["radial_centers"] * mean_radius_scale
        holdout_radius = np.asarray(holdout_empirical["radius"], dtype=float)
        holdout_observed = np.asarray(holdout_empirical["velocity"], dtype=float)
        holdout_prediction = np.interp(
            holdout_radius,
            scaled_radius,
            combined_velocity * mean_velocity_scale,
            left=combined_velocity[0] * mean_velocity_scale,
            right=combined_velocity[-1] * mean_velocity_scale,
        )
        local_baseline = _baseline_family(holdout_radius, holdout_observed)
        flat_rmse = rmse(holdout_observed, local_baseline["flat"])
        linear_rmse = rmse(holdout_observed, local_baseline["linear"])
        baseline_name = "flat_rotation_baseline" if flat_rmse < linear_rmse else "linear_rotation_baseline"
        baseline_prediction = local_baseline["flat"] if baseline_name.startswith("flat") else local_baseline["linear"]
        diagnostics[holdout_id] = {
            "holdout_rmse": float(rmse(holdout_observed, holdout_prediction)),
            "baseline_holdout_rmse": float(rmse(holdout_observed, baseline_prediction)),
            "best_arm_mode": str(fitted.get("arm_mode", fitted["profile"]["params"].get("arm_mode", 2))),
            "baseline_winner": baseline_name,
            "tne_winner_flag": float(rmse(holdout_observed, holdout_prediction) < rmse(holdout_observed, baseline_prediction)),
        }
    return diagnostics


def prepare_model_prediction(empirical: dict[str, Any], fitted_parameters: dict[str, Any] | None = None) -> dict[str, Any]:
    fit = fitted_parameters or fit_parameters(empirical)
    profile = fit["profile"]["profile"]
    galaxy_slices = _galaxy_slices(empirical["galaxy_id"])
    observed_r = np.asarray(empirical["radius"], dtype=float)
    predicted_velocity = np.zeros_like(observed_r)
    aggregation_mix_mean = 0.0
    radius_scale_mean = 0.0
    velocity_scale_mean = 0.0
    per_galaxy_prediction: dict[str, dict[str, Any]] = {}
    for galaxy_id, mask in galaxy_slices:
        local_fit = fit["per_galaxy"][galaxy_id]
        combined_velocity = (
            local_fit["aggregation_mix"] * profile["mean_tangential_velocity"]
            + (1.0 - local_fit["aggregation_mix"]) * profile["median_tangential_velocity"]
        )
        scaled_radius = profile["radial_centers"] * local_fit["radius_scale"]
        local_prediction = np.interp(
            observed_r[mask],
            scaled_radius,
            combined_velocity * local_fit["velocity_scale"],
            left=combined_velocity[0] * local_fit["velocity_scale"],
            right=combined_velocity[-1] * local_fit["velocity_scale"],
        )
        predicted_velocity[mask] = local_prediction
        aggregation_mix_mean += local_fit["aggregation_mix"]
        radius_scale_mean += local_fit["radius_scale"]
        velocity_scale_mean += local_fit["velocity_scale"]
        per_galaxy_prediction[galaxy_id] = {
            "scaled_radius_profile": np.asarray(scaled_radius, dtype=float),
            "scaled_velocity_profile": np.asarray(combined_velocity * local_fit["velocity_scale"], dtype=float),
            "prediction": np.asarray(local_prediction, dtype=float),
            "radius_scale": float(local_fit["radius_scale"]),
            "velocity_scale": float(local_fit["velocity_scale"]),
            "aggregation_mix": float(local_fit["aggregation_mix"]),
            "selected_baseline": fit["selected_baselines"][galaxy_id],
        }
    galaxy_count = max(len(galaxy_slices), 1)
    return {
        "tne_prediction": predicted_velocity,
        "baseline_prediction": np.asarray(fit["baseline_prediction"], dtype=float),
        "flat_baseline_prediction": np.asarray(fit["flat_prediction"], dtype=float),
        "linear_baseline_prediction": np.asarray(fit["linear_prediction"], dtype=float),
        "smoothed_empirical_reference": np.asarray(fit["smoothed_prediction"], dtype=float),
        "density_profile": np.asarray(profile["density_profile"], dtype=float),
        "profile_std": np.asarray(profile["tangential_velocity_std"], dtype=float),
        "profile_counts": np.asarray(profile["counts"], dtype=int),
        "spiral_order_parameter": float(fit["profile"]["spiral_metrics"]["spiral_order_parameter"]),
        "mode_2_amplitude": float(fit["profile"]["spiral_metrics"]["mode_2_amplitude"]),
        "mode_3_amplitude": float(fit["profile"]["spiral_metrics"]["mode_3_amplitude"]),
        "mode_1_amplitude": float(fit["profile"]["spiral_metrics"]["mode_1_amplitude"]),
        "mode_4_amplitude": float(fit["profile"]["spiral_metrics"]["mode_4_amplitude"]),
        "dominant_mode": float(fit["profile"]["spiral_metrics"]["dominant_mode"]),
        "dominant_mode_amplitude": float(fit["profile"]["spiral_metrics"]["dominant_mode_amplitude"]),
        "target_mode_amplitude": float(fit["profile"]["spiral_metrics"]["target_mode_amplitude"]),
        "target_mode_ratio": float(fit["profile"]["spiral_metrics"]["target_mode_ratio"]),
        "pitch_angle_proxy": float(fit["profile"]["spiral_metrics"]["pitch_angle_proxy"]),
        "radial_concentration": float(fit["profile"]["spiral_metrics"]["radial_concentration"]),
        "density_arm_contrast": float(fit["profile"]["spiral_metrics"]["density_arm_contrast"]),
        "angular_momentum_drift": float(fit["profile"]["spiral_metrics"]["angular_momentum_drift"]),
        "elastic_tension_max": float(fit["profile"]["spiral_metrics"]["elastic_tension_max"]),
        "tension_mean": float(fit["profile"]["spiral_metrics"]["tension_mean"]),
        "tension_gradient_mean": float(fit["profile"]["spiral_metrics"]["tension_gradient_mean"]),
        "mass_conservation_error": float(fit["profile"]["spiral_metrics"]["mass_conservation_error"]),
        "morphology_stability_score": float(fit["profile"]["spiral_metrics"]["morphology_stability_score"]),
        "field_feedback_strength": float(fit["profile"]["spiral_metrics"]["field_feedback_strength"]),
        "initialization_vs_evolution_score": float(fit["profile"]["spiral_metrics"]["initialization_vs_evolution_score"]),
        "arm_asymmetry_index": float(fit["profile"]["spiral_metrics"]["arm_asymmetry_index"]),
        "per_galaxy_prediction": per_galaxy_prediction,
        "fitted_parameters": {
            "radius_scale": float(radius_scale_mean / galaxy_count),
            "velocity_scale": float(velocity_scale_mean / galaxy_count),
            "aggregation_mix": float(aggregation_mix_mean / galaxy_count),
            "simulation_params": fit["profile"]["params"],
            "parameter_sweep_level": fit.get("parameter_sweep_level", "standard"),
            "arm_mode": str(fit.get("arm_mode", fit["profile"]["params"].get("arm_mode", 2))),
            "arm_modes_tested": fit.get("arm_modes_tested", ["2"]),
            "baseline_scores": fit["baseline_scores"],
            "selected_baselines": fit["selected_baselines"],
            "per_galaxy": fit["per_galaxy"],
        },
        "selected_baseline": "multi_galaxy_baseline_family",
    }


def compute_residuals(empirical: dict[str, Any], prediction: dict[str, Any]) -> dict[str, np.ndarray]:
    observed = np.asarray(empirical["velocity"], dtype=float)
    return {
        "tne_residual": np.asarray(prediction["tne_prediction"], dtype=float) - observed,
        "baseline_residual": np.asarray(prediction["baseline_prediction"], dtype=float) - observed,
        "flat_residual": np.asarray(prediction["flat_baseline_prediction"], dtype=float) - observed,
        "linear_residual": np.asarray(prediction["linear_baseline_prediction"], dtype=float) - observed,
    }


def compute_metrics(empirical: dict[str, Any], prediction: dict[str, Any], residuals: dict[str, np.ndarray]) -> dict[str, Any]:
    metrics = metric_bundle(
        observed=np.asarray(empirical["velocity"], dtype=float),
        predicted=np.asarray(prediction["tne_prediction"], dtype=float),
        uncertainty=np.asarray(empirical["velocity_uncertainty"], dtype=float),
        n_params=8,
        baseline=np.asarray(prediction["baseline_prediction"], dtype=float),
        baseline_params=2,
    )
    source_status = sorted(set(empirical.get("source_status", ["fixture_only"])))
    metrics["data_status"] = source_status[0] if len(source_status) == 1 else "mixed"
    metrics["baseline_model"] = prediction["selected_baseline"]
    metrics["flat_baseline_RMSE"] = rmse(empirical["velocity"], prediction["flat_baseline_prediction"])
    metrics["linear_baseline_RMSE"] = rmse(empirical["velocity"], prediction["linear_baseline_prediction"])
    metrics["smoothed_reference_RMSE"] = rmse(empirical["velocity"], prediction["smoothed_empirical_reference"])
    metrics["mean_RMSE"] = float(metrics["RMSE"])
    metrics["median_RMSE"] = float(np.median(np.abs(residuals["tne_residual"])))
    metrics["spiral_order_parameter"] = float(prediction["spiral_order_parameter"])
    metrics["mode_2_amplitude"] = float(prediction["mode_2_amplitude"])
    metrics["mode_3_amplitude"] = float(prediction["mode_3_amplitude"])
    metrics["mode_1_amplitude"] = float(prediction["mode_1_amplitude"])
    metrics["mode_4_amplitude"] = float(prediction["mode_4_amplitude"])
    metrics["dominant_mode"] = float(prediction["dominant_mode"])
    metrics["dominant_mode_amplitude"] = float(prediction["dominant_mode_amplitude"])
    metrics["target_mode_amplitude"] = float(prediction["target_mode_amplitude"])
    metrics["target_mode_ratio"] = float(prediction["target_mode_ratio"])
    metrics["pitch_angle_proxy"] = float(prediction["pitch_angle_proxy"])
    metrics["radial_concentration"] = float(prediction["radial_concentration"])
    metrics["density_arm_contrast"] = float(prediction["density_arm_contrast"])
    metrics["angular_momentum_drift"] = float(prediction["angular_momentum_drift"])
    metrics["elastic_tension_max"] = float(prediction["elastic_tension_max"])
    metrics["tension_mean"] = float(prediction["tension_mean"])
    metrics["tension_gradient_mean"] = float(prediction["tension_gradient_mean"])
    metrics["mass_conservation_error"] = float(prediction["mass_conservation_error"])
    metrics["morphology_stability_score"] = float(prediction["morphology_stability_score"])
    metrics["field_feedback_strength"] = float(prediction["field_feedback_strength"])
    metrics["initialization_vs_evolution_score"] = float(prediction["initialization_vs_evolution_score"])
    metrics["arm_asymmetry_index"] = float(prediction["arm_asymmetry_index"])
    metrics["galaxy_count"] = float(len(prediction["per_galaxy_prediction"]))
    metrics["arm_mode"] = prediction["fitted_parameters"]["arm_mode"]
    metrics["TNE_vs_baseline_note"] = (
        "Best preliminary residual fit under the implemented proxy mapping."
        if metrics["RMSE"] < metrics["baseline_RMSE"]
        else "Simple baseline family remains better or comparable under the implemented multi-galaxy proxy mapping."
    )
    return metrics


def plot_comparison(
    empirical: dict[str, Any],
    prediction: dict[str, Any],
    output_path: str | Path | dict[str, str | Path],
) -> list[Path]:
    if isinstance(output_path, dict):
        curve_path = Path(output_path["curve"])
        residual_path = Path(output_path["residual"])
        morphology_path = Path(output_path["morphology"])
    else:
        curve_path = Path(output_path)
        residual_path = curve_path.with_name("spiral_rotation_residuals.png")
        morphology_path = curve_path.with_name("spiral_morphology_comparison.png")

    galaxy_slices = _galaxy_slices(empirical["galaxy_id"])
    n_galaxies = len(galaxy_slices)
    fig, axes = plt.subplots(n_galaxies, 1, figsize=(8.4, 3.0 * n_galaxies), constrained_layout=True, sharex=False)
    axes = np.atleast_1d(axes)
    for ax, (galaxy_id, mask) in zip(axes, galaxy_slices, strict=True):
        radius = np.asarray(empirical["radius"], dtype=float)[mask]
        observed = np.asarray(empirical["velocity"], dtype=float)[mask]
        uncertainty = np.asarray(empirical["velocity_uncertainty"], dtype=float)[mask]
        tne = np.asarray(prediction["tne_prediction"], dtype=float)[mask]
        baseline = np.asarray(prediction["baseline_prediction"], dtype=float)[mask]
        ax.errorbar(radius, observed, yerr=uncertainty, color="#1f77b4", linewidth=1.8, marker="o", label=f"{galaxy_id} empirical")
        ax.plot(radius, tne, color="#d62728", linewidth=2.0, marker="s", label="TNE best-fit curve")
        ax.plot(radius, baseline, color="#2ca02c", linewidth=1.8, linestyle="--", label="local baseline")
        ax.plot(radius, np.asarray(prediction["smoothed_empirical_reference"], dtype=float)[mask], color="#7f7f7f", linewidth=1.4, linestyle=":", label="smoothed reference")
        local = prediction["per_galaxy_prediction"][galaxy_id]
        ax.set_title(f"Finite illustrative spiral rotation comparison: {galaxy_id}")
        ax.set_ylabel("normalized velocity")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="best")
        ax.text(
            0.02,
            0.03,
            (
                f"radius_scale={local['radius_scale']:.3f}\n"
                f"velocity_scale={local['velocity_scale']:.3f}\n"
                f"aggregation_mix={local['aggregation_mix']:.3f}"
            ),
            transform=ax.transAxes,
            fontsize=8,
            bbox={"facecolor": "white", "alpha": 0.75, "edgecolor": "#cccccc"},
        )
        ax.set_xlabel("normalized radius")
    save_figure(fig, curve_path, dpi=220)
    plt.close(fig)

    fig, axes = plt.subplots(n_galaxies, 1, figsize=(8.4, 2.6 * n_galaxies), constrained_layout=True, sharex=False)
    axes = np.atleast_1d(axes)
    for ax, (galaxy_id, mask) in zip(axes, galaxy_slices, strict=True):
        radius = np.asarray(empirical["radius"], dtype=float)[mask]
        observed = np.asarray(empirical["velocity"], dtype=float)[mask]
        ax.axhline(0.0, color="black", linewidth=0.8, linestyle="--")
        ax.plot(radius, np.asarray(prediction["flat_baseline_prediction"], dtype=float)[mask] - observed, color="#9467bd", linewidth=1.6, label="flat baseline residual")
        ax.plot(radius, np.asarray(prediction["linear_baseline_prediction"], dtype=float)[mask] - observed, color="#2ca02c", linewidth=1.6, linestyle="--", label="linear baseline residual")
        ax.plot(radius, np.asarray(prediction["tne_prediction"], dtype=float)[mask] - observed, color="#d62728", linewidth=2.0, label="TNE residual")
        ax.set_title(f"Spiral rotation residual diagnostics: {galaxy_id}")
        ax.set_xlabel("normalized radius")
        ax.set_ylabel("residual")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="best")
    save_figure(fig, residual_path, dpi=220)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(8.0, 6.2), constrained_layout=True)
    for galaxy_id, local in prediction["per_galaxy_prediction"].items():
        axes[0].plot(local["scaled_radius_profile"], local["scaled_velocity_profile"], linewidth=1.8, marker="o", label=f"{galaxy_id} TNE profile")
    axes[0].set_title("Tangential-velocity toy profiles")
    axes[0].set_ylabel("velocity")
    axes[0].grid(True, alpha=0.25)
    axes[0].legend(loc="best")
    axes[1].plot(np.arange(len(prediction["density_profile"])), prediction["density_profile"], color="#1f77b4", linewidth=2.0, marker="s", label="density profile")
    axes[1].axhline(prediction["density_arm_contrast"], color="#d62728", linewidth=1.4, linestyle="--", label="arm contrast proxy")
    axes[1].set_title("Shared radial density profile and arm contrast")
    axes[1].set_xlabel("profile bin")
    axes[1].set_ylabel("density / contrast proxy")
    axes[1].grid(True, alpha=0.25)
    axes[1].legend(loc="best")
    save_figure(fig, morphology_path, dpi=220)
    plt.close(fig)
    return [curve_path, residual_path, morphology_path]
