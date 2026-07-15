"""Observable mapping for finite illustrative EHT-style horizon comparisons."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from empirical.io import fixture_path, read_csv_rows
from empirical.metrics import metric_bundle
from tne_runtime.artifacts.io import save_figure
from equations.black_hole_dynamics.black_hole_dynamics import BlackHoleParams, black_hole_snapshot


DEFAULT_SOURCE_METADATA: dict[str, tuple[float, float]] = {
    "M87*": (6.5, 16.8),
    "M87*_fixture": (6.5, 16.8),
    "SgrA*": (0.0040, 0.0082),
    "SgrA*_fixture": (0.0040, 0.0082),
}


@lru_cache(maxsize=1)
def _snapshot() -> dict[str, Any]:
    return black_hole_snapshot(BlackHoleParams().mass_proxy, BlackHoleParams())


def _angular_factor(mass_billion_solar: np.ndarray, distance_mpc: np.ndarray) -> np.ndarray:
    mass = np.asarray(mass_billion_solar, dtype=float)
    distance = np.asarray(distance_mpc, dtype=float)
    return mass / (distance + 1e-12)


def _source_metadata(row: dict[str, str]) -> tuple[float, float]:
    if "mass_billion_solar" in row and "distance_mpc" in row:
        return float(row["mass_billion_solar"]), float(row["distance_mpc"])
    return DEFAULT_SOURCE_METADATA.get(row["source"], (1.0, 1.0))


def prepare_empirical_observable(path: str | Path | None = None) -> dict[str, Any]:
    rows = read_csv_rows(path or fixture_path("eht_observable_fixture.csv"))
    metadata = [_source_metadata(row) for row in rows]
    return {
        "source": [row["source"] for row in rows],
        "ring_diameter": np.asarray([float(row["ring_diameter"]) for row in rows], dtype=float),
        "ring_diameter_uncertainty": np.asarray([float(row["ring_diameter_uncertainty"]) for row in rows], dtype=float),
        "shadow_radius": np.asarray([float(row["shadow_radius"]) for row in rows], dtype=float),
        "shadow_radius_uncertainty": np.asarray([float(row["shadow_radius_uncertainty"]) for row in rows], dtype=float),
        "mass_billion_solar": np.asarray([item[0] for item in metadata], dtype=float),
        "distance_mpc": np.asarray([item[1] for item in metadata], dtype=float),
        "angular_scale_note": [row.get("angular_scale_note", "published summary mass-distance proxy") for row in rows],
        "source_status": [row["source_status"] for row in rows],
    }


def fit_parameters(empirical: dict[str, Any]) -> dict[str, Any]:
    snapshot = _snapshot()
    ring_proxy = float(2.0 * snapshot["threshold_contour_radius"])
    shadow_proxy = float(snapshot["horizon_radius"])
    angular_factor = _angular_factor(empirical["mass_billion_solar"], empirical["distance_mpc"])
    ring_terms = angular_factor * ring_proxy
    shadow_terms = angular_factor * shadow_proxy
    ring_weights = 1.0 / (np.asarray(empirical["ring_diameter_uncertainty"], dtype=float) ** 2 + 1e-12)
    shadow_weights = 1.0 / (np.asarray(empirical["shadow_radius_uncertainty"], dtype=float) ** 2 + 1e-12)
    ring_scale = float(np.sum(ring_weights * empirical["ring_diameter"] * ring_terms) / np.sum(ring_weights * ring_terms**2))
    shadow_scale = float(
        np.sum(shadow_weights * empirical["shadow_radius"] * shadow_terms) / np.sum(shadow_weights * shadow_terms**2)
    )
    source_specific_scale: dict[str, float] = {}
    for idx, source in enumerate(empirical["source"]):
        ring_local = float(empirical["ring_diameter"][idx] / (ring_terms[idx] + 1e-12))
        shadow_local = float(empirical["shadow_radius"][idx] / (shadow_terms[idx] + 1e-12))
        source_specific_scale[source] = 0.5 * (ring_local + shadow_local)
    return {
        "ring_scale": ring_scale,
        "shadow_scale": shadow_scale,
        "source_specific_scale": source_specific_scale,
        "angular_factor": angular_factor.tolist(),
        "ring_proxy": ring_proxy,
        "shadow_proxy": shadow_proxy,
        "threshold_contour_radius": float(snapshot["threshold_contour_radius"]),
        "horizon_radius_proxy": float(snapshot["horizon_radius"]),
        "central_depression_proxy": float(snapshot["central_depression_proxy"]),
        "ring_contrast_proxy": float(snapshot["ring_contrast_proxy"]),
    }


def prepare_model_prediction(empirical: dict[str, Any], fitted_parameters: dict[str, Any] | None = None) -> dict[str, Any]:
    fit = fitted_parameters or fit_parameters(empirical)
    angular_factor = np.asarray(fit["angular_factor"], dtype=float)
    ring_prediction = fit["ring_scale"] * angular_factor * fit["ring_proxy"]
    shadow_prediction = fit["shadow_scale"] * angular_factor * fit["shadow_proxy"]
    source_specific_ring = np.asarray(
        [fit["source_specific_scale"][source] * angular_factor[idx] * fit["ring_proxy"] for idx, source in enumerate(empirical["source"])],
        dtype=float,
    )
    source_specific_shadow = np.asarray(
        [fit["source_specific_scale"][source] * angular_factor[idx] * fit["shadow_proxy"] for idx, source in enumerate(empirical["source"])],
        dtype=float,
    )
    return {
        "ring_prediction": ring_prediction,
        "shadow_prediction": shadow_prediction,
        "ring_prediction_source_specific": source_specific_ring,
        "shadow_prediction_source_specific": source_specific_shadow,
        "angular_factor": angular_factor,
        "horizon_radius_proxy": float(fit["horizon_radius_proxy"]),
        "threshold_contour_radius": float(fit["threshold_contour_radius"]),
        "central_depression_proxy": float(fit["central_depression_proxy"]),
        "ring_contrast_proxy": float(fit["ring_contrast_proxy"]),
        "fitted_parameters": fit,
    }


def compute_residuals(empirical: dict[str, Any], prediction: dict[str, Any]) -> dict[str, np.ndarray]:
    ring_residual = np.asarray(prediction["ring_prediction"], dtype=float) - np.asarray(empirical["ring_diameter"], dtype=float)
    shadow_residual = np.asarray(prediction["shadow_prediction"], dtype=float) - np.asarray(empirical["shadow_radius"], dtype=float)
    ring_uncertainty = np.asarray(empirical["ring_diameter_uncertainty"], dtype=float)
    shadow_uncertainty = np.asarray(empirical["shadow_radius_uncertainty"], dtype=float)
    return {
        "ring_residual": ring_residual,
        "shadow_residual": shadow_residual,
        "ring_residual_source_specific": np.asarray(prediction["ring_prediction_source_specific"], dtype=float) - np.asarray(empirical["ring_diameter"], dtype=float),
        "shadow_residual_source_specific": np.asarray(prediction["shadow_prediction_source_specific"], dtype=float) - np.asarray(empirical["shadow_radius"], dtype=float),
        "ring_normalized_residual": ring_residual / (ring_uncertainty + 1e-12),
        "shadow_normalized_residual": shadow_residual / (shadow_uncertainty + 1e-12),
    }


def compute_metrics(empirical: dict[str, Any], prediction: dict[str, Any], residuals: dict[str, np.ndarray]) -> dict[str, Any]:
    observed = np.concatenate([empirical["ring_diameter"], empirical["shadow_radius"]])
    predicted = np.concatenate([prediction["ring_prediction"], prediction["shadow_prediction"]])
    uncertainty = np.concatenate([empirical["ring_diameter_uncertainty"], empirical["shadow_radius_uncertainty"]])
    metrics = metric_bundle(observed=observed, predicted=predicted, uncertainty=uncertainty, n_params=2)
    source_specific_predicted = np.concatenate(
        [prediction["ring_prediction_source_specific"], prediction["shadow_prediction_source_specific"]]
    )
    metrics["source_specific_RMSE"] = float(np.sqrt(np.mean((source_specific_predicted - observed) ** 2)))
    metrics["source_specific_weighted_RMSE"] = float(
        np.sqrt(np.mean(((source_specific_predicted - observed) / (uncertainty + 1e-12)) ** 2))
    )
    source_status = sorted(set(empirical.get("source_status", ["fixture_only"])))
    metrics["data_status"] = source_status[0] if len(source_status) == 1 else "mixed"
    metrics["baseline_model"] = "none"
    metrics["threshold_contour_radius"] = float(prediction["threshold_contour_radius"])
    metrics["horizon_radius_proxy"] = float(prediction["horizon_radius_proxy"])
    metrics["ring_contrast_proxy"] = float(prediction["ring_contrast_proxy"])
    metrics["central_depression_proxy"] = float(prediction["central_depression_proxy"])
    metrics["mean_angular_factor"] = float(np.mean(prediction["angular_factor"]))
    metrics["TNE_vs_baseline_note"] = (
        "Mass-distance angular mapping is reported as a finite illustrative proxy; source-specific scaling remains diagnostic only."
    )
    return metrics


def plot_comparison(empirical: dict[str, Any], prediction: dict[str, Any], output_path: str | Path | dict[str, str | Path]):
    if isinstance(output_path, dict):
        curve_path = Path(output_path["curve"])
        residual_path = Path(output_path["residual"])
    else:
        curve_path = Path(output_path)
        residual_path = curve_path.with_name("eht_horizon_residuals.png")

    x = np.arange(len(empirical["source"]))
    width = 0.28
    fig, axes = plt.subplots(3, 1, figsize=(8.0, 8.8), constrained_layout=True)
    axes[0].bar(x - width, empirical["ring_diameter"], width, yerr=empirical["ring_diameter_uncertainty"], color="#1f77b4", label="observed ring")
    axes[0].bar(x, prediction["ring_prediction"], width, color="#d62728", label="angular TNE ring")
    axes[0].bar(x + width, prediction["ring_prediction_source_specific"], width, color="#ff9896", label="per-source diagnostic ring")
    axes[0].set_xticks(x, empirical["source"])
    axes[0].set_title("Finite illustrative EHT ring proxy comparison")
    axes[0].set_ylabel("angular observable")
    axes[0].grid(True, axis="y", alpha=0.25)
    axes[0].legend(loc="best")

    axes[1].bar(x - width, empirical["shadow_radius"], width, yerr=empirical["shadow_radius_uncertainty"], color="#9ecae1", label="observed shadow")
    axes[1].bar(x, prediction["shadow_prediction"], width, color="#9467bd", label="angular TNE shadow")
    axes[1].bar(x + width, prediction["shadow_prediction_source_specific"], width, color="#c5b0d5", label="per-source diagnostic shadow")
    axes[1].set_xticks(x, empirical["source"])
    axes[1].set_ylabel("angular observable")
    axes[1].grid(True, axis="y", alpha=0.25)
    axes[1].legend(loc="best")

    axes[2].bar(x, prediction["angular_factor"], color="#8c564b", width=0.45)
    axes[2].set_xticks(x, empirical["source"])
    axes[2].set_ylabel("mass / distance proxy")
    axes[2].set_title("Published summary angular-size proxy")
    axes[2].grid(True, axis="y", alpha=0.25)
    save_figure(fig, curve_path, dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.0, 4.6), constrained_layout=True)
    ax.axhline(0.0, color="black", linewidth=0.8, linestyle="--")
    source_positions = np.arange(2 * len(empirical["source"]))
    labels = [f"{source} ring" for source in empirical["source"]] + [f"{source} shadow" for source in empirical["source"]]
    residuals = compute_residuals(empirical, prediction)
    residual_values = np.concatenate([residuals["ring_normalized_residual"], residuals["shadow_normalized_residual"]])
    source_specific_values = np.concatenate(
        [
            residuals["ring_residual_source_specific"] / (np.asarray(empirical["ring_diameter_uncertainty"], dtype=float) + 1e-12),
            residuals["shadow_residual_source_specific"] / (np.asarray(empirical["shadow_radius_uncertainty"], dtype=float) + 1e-12),
        ]
    )
    ax.plot(source_positions, residual_values, color="#d62728", linewidth=2.0, marker="o", label="shared angular residual")
    ax.plot(source_positions, source_specific_values, color="#9467bd", linewidth=1.8, marker="s", label="per-source diagnostic residual")
    ax.set_xticks(source_positions, labels)
    ax.set_title("EHT normalized residual diagnostics")
    ax.set_ylabel("residual / uncertainty")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    save_figure(fig, residual_path, dpi=220)
    plt.close(fig)
    return [curve_path, residual_path]
