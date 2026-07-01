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
from empirical.metrics import metric_bundle, rmse
from equations.artifact_io import save_figure
from equations.black_hole_dynamics.black_hole_dynamics import BlackHoleParams, black_hole_snapshot


@lru_cache(maxsize=1)
def _snapshot() -> dict[str, Any]:
    return black_hole_snapshot(BlackHoleParams().mass_proxy, BlackHoleParams())


def prepare_empirical_observable(path: str | Path | None = None) -> dict[str, Any]:
    rows = read_csv_rows(path or fixture_path("eht_observable_fixture.csv"))
    return {
        "source": [row["source"] for row in rows],
        "ring_diameter": np.asarray([float(row["ring_diameter"]) for row in rows], dtype=float),
        "ring_diameter_uncertainty": np.asarray([float(row["ring_diameter_uncertainty"]) for row in rows], dtype=float),
        "shadow_radius": np.asarray([float(row["shadow_radius"]) for row in rows], dtype=float),
        "shadow_radius_uncertainty": np.asarray([float(row["shadow_radius_uncertainty"]) for row in rows], dtype=float),
        "source_status": [row["source_status"] for row in rows],
    }


def fit_parameters(empirical: dict[str, Any]) -> dict[str, Any]:
    snapshot = _snapshot()
    ring_proxy = float(2.0 * snapshot["threshold_contour_radius"])
    shadow_proxy = float(snapshot["horizon_radius"])
    observed = np.concatenate([empirical["ring_diameter"], empirical["shadow_radius"]])
    uncertainty = np.concatenate([empirical["ring_diameter_uncertainty"], empirical["shadow_radius_uncertainty"]])
    model_terms = np.tile(np.array([ring_proxy, shadow_proxy], dtype=float), len(empirical["source"]))
    weights = 1.0 / (uncertainty**2 + 1e-12)
    shared_scale = float(np.sum(weights * observed * model_terms) / np.sum(weights * model_terms**2))
    source_scales: dict[str, float] = {}
    for idx, source in enumerate(empirical["source"]):
        observed_pair = np.array([empirical["ring_diameter"][idx], empirical["shadow_radius"][idx]], dtype=float)
        uncertainty_pair = np.array(
            [empirical["ring_diameter_uncertainty"][idx], empirical["shadow_radius_uncertainty"][idx]],
            dtype=float,
        )
        pair_terms = np.array([ring_proxy, shadow_proxy], dtype=float)
        pair_weights = 1.0 / (uncertainty_pair**2 + 1e-12)
        source_scales[source] = float(np.sum(pair_weights * observed_pair * pair_terms) / np.sum(pair_weights * pair_terms**2))
    return {
        "shared_scale": shared_scale,
        "source_scales": source_scales,
        "ring_proxy": ring_proxy,
        "shadow_proxy": shadow_proxy,
        "threshold_contour_radius": float(snapshot["threshold_contour_radius"]),
        "horizon_radius_proxy": float(snapshot["horizon_radius"]),
        "central_depression_proxy": float(snapshot["central_depression_proxy"]),
        "ring_contrast_proxy": float(snapshot["ring_contrast_proxy"]),
    }


def prepare_model_prediction(empirical: dict[str, Any], fitted_parameters: dict[str, Any] | None = None) -> dict[str, Any]:
    fit = fitted_parameters or fit_parameters(empirical)
    shared_ring = np.full(len(empirical["source"]), fit["shared_scale"] * fit["ring_proxy"], dtype=float)
    shared_shadow = np.full(len(empirical["source"]), fit["shared_scale"] * fit["shadow_proxy"], dtype=float)
    source_specific_ring = np.asarray(
        [fit["source_scales"][source] * fit["ring_proxy"] for source in empirical["source"]],
        dtype=float,
    )
    source_specific_shadow = np.asarray(
        [fit["source_scales"][source] * fit["shadow_proxy"] for source in empirical["source"]],
        dtype=float,
    )
    return {
        "ring_prediction": shared_ring,
        "shadow_prediction": shared_shadow,
        "ring_prediction_source_specific": source_specific_ring,
        "shadow_prediction_source_specific": source_specific_shadow,
        "horizon_radius_proxy": float(fit["horizon_radius_proxy"]),
        "threshold_contour_radius": float(fit["threshold_contour_radius"]),
        "central_depression_proxy": float(fit["central_depression_proxy"]),
        "ring_contrast_proxy": float(fit["ring_contrast_proxy"]),
        "fitted_parameters": fit,
    }


def compute_residuals(empirical: dict[str, Any], prediction: dict[str, Any]) -> dict[str, np.ndarray]:
    ring_residual = np.asarray(prediction["ring_prediction"], dtype=float) - np.asarray(empirical["ring_diameter"], dtype=float)
    shadow_residual = np.asarray(prediction["shadow_prediction"], dtype=float) - np.asarray(empirical["shadow_radius"], dtype=float)
    return {
        "ring_residual": ring_residual,
        "shadow_residual": shadow_residual,
        "ring_residual_source_specific": np.asarray(prediction["ring_prediction_source_specific"], dtype=float) - np.asarray(empirical["ring_diameter"], dtype=float),
        "shadow_residual_source_specific": np.asarray(prediction["shadow_prediction_source_specific"], dtype=float) - np.asarray(empirical["shadow_radius"], dtype=float),
        "ring_normalized_residual": ring_residual / (np.asarray(empirical["ring_diameter_uncertainty"], dtype=float) + 1e-12),
        "shadow_normalized_residual": shadow_residual / (np.asarray(empirical["shadow_radius_uncertainty"], dtype=float) + 1e-12),
    }


def compute_metrics(empirical: dict[str, Any], prediction: dict[str, Any], residuals: dict[str, np.ndarray]) -> dict[str, Any]:
    observed = np.concatenate([empirical["ring_diameter"], empirical["shadow_radius"]])
    predicted = np.concatenate([prediction["ring_prediction"], prediction["shadow_prediction"]])
    uncertainty = np.concatenate([empirical["ring_diameter_uncertainty"], empirical["shadow_radius_uncertainty"]])
    metrics = metric_bundle(observed=observed, predicted=predicted, uncertainty=uncertainty, n_params=1)
    source_specific_predicted = np.concatenate(
        [prediction["ring_prediction_source_specific"], prediction["shadow_prediction_source_specific"]]
    )
    metrics["source_specific_RMSE"] = rmse(observed, source_specific_predicted)
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
    metrics["TNE_vs_baseline_note"] = (
        "Shared-scale fit remains preliminary; per-source scaling is reported separately as a diagnostic and not as an independent validation."
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
    fig, axes = plt.subplots(2, 1, figsize=(8.0, 6.8), constrained_layout=True)
    axes[0].bar(x - width, empirical["ring_diameter"], width, yerr=empirical["ring_diameter_uncertainty"], color="#1f77b4", label="observed ring")
    axes[0].bar(x, prediction["ring_prediction"], width, color="#d62728", label="shared-scale TNE ring")
    axes[0].bar(x + width, prediction["ring_prediction_source_specific"], width, color="#ff9896", label="per-source TNE ring")
    axes[0].set_xticks(x, empirical["source"])
    axes[0].set_title("Finite illustrative EHT ring proxy comparison")
    axes[0].set_ylabel("angular observable")
    axes[0].grid(True, axis="y", alpha=0.25)
    axes[0].legend(loc="best")
    axes[1].bar(x - width, empirical["shadow_radius"], width, yerr=empirical["shadow_radius_uncertainty"], color="#9ecae1", label="observed shadow")
    axes[1].bar(x, prediction["shadow_prediction"], width, color="#9467bd", label="shared-scale TNE shadow")
    axes[1].bar(x + width, prediction["shadow_prediction_source_specific"], width, color="#c5b0d5", label="per-source TNE shadow")
    axes[1].set_xticks(x, empirical["source"])
    axes[1].set_ylabel("angular observable")
    axes[1].grid(True, axis="y", alpha=0.25)
    axes[1].legend(loc="best")
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
    ax.plot(source_positions, residual_values, color="#d62728", linewidth=2.0, marker="o", label="shared-scale normalized residual")
    ax.plot(source_positions, source_specific_values, color="#9467bd", linewidth=1.8, marker="s", label="per-source normalized residual")
    ax.set_xticks(source_positions, labels)
    ax.set_title("EHT normalized residual diagnostics")
    ax.set_ylabel("residual / uncertainty")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    save_figure(fig, residual_path, dpi=220)
    plt.close(fig)
    return [curve_path, residual_path]
