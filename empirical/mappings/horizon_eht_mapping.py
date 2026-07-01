"""Observable mapping for fixture-backed EHT-style horizon comparisons."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from empirical.io import fixture_path, read_csv_rows
from empirical.metrics import metric_bundle
from empirical.visualization.plot_empirical_comparisons import plot_grouped_bars
from equations.black_hole_dynamics.black_hole_dynamics import BlackHoleParams, simulate_black_hole_dynamics


@lru_cache(maxsize=1)
def _black_hole_result() -> dict[str, Any]:
    return simulate_black_hole_dynamics(BlackHoleParams())


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


def fit_parameters(empirical: dict[str, Any]) -> dict[str, float]:
    result = _black_hole_result()
    horizon_ref = float(np.nanmean(result["horizon_radius"][-10:]))
    model_vector = np.array([2.0 * horizon_ref, horizon_ref], dtype=float)
    observed = np.concatenate([empirical["ring_diameter"], empirical["shadow_radius"]])
    uncertainty = np.concatenate([empirical["ring_diameter_uncertainty"], empirical["shadow_radius_uncertainty"]])
    model_terms = np.tile(model_vector, len(empirical["source"]))
    weights = 1.0 / (uncertainty**2 + 1e-12)
    alpha = float(np.sum(weights * observed * model_terms) / np.sum(weights * model_terms**2))
    return {"alpha": alpha, "horizon_reference": horizon_ref}


def prepare_model_prediction(empirical: dict[str, Any], fitted_parameters: dict[str, float] | None = None) -> dict[str, Any]:
    fit = fitted_parameters or fit_parameters(empirical)
    result = _black_hole_result()
    horizon_ref = fit["horizon_reference"]
    alpha = fit["alpha"]
    ring_pred = np.full(len(empirical["source"]), alpha * 2.0 * horizon_ref, dtype=float)
    shadow_pred = np.full(len(empirical["source"]), alpha * horizon_ref, dtype=float)
    pi_final = np.asarray(result["pi_E_time"][-1], dtype=float)
    ring_contrast_proxy = float(np.max(pi_final) - np.min(pi_final))
    return {
        "ring_prediction": ring_pred,
        "shadow_prediction": shadow_pred,
        "central_depression_proxy": float(np.min(pi_final)),
        "ring_contrast_proxy": ring_contrast_proxy,
        "fitted_parameters": fit,
    }


def compute_residuals(empirical: dict[str, Any], prediction: dict[str, Any]) -> dict[str, np.ndarray]:
    return {
        "ring_residual": np.asarray(prediction["ring_prediction"], dtype=float) - np.asarray(empirical["ring_diameter"], dtype=float),
        "shadow_residual": np.asarray(prediction["shadow_prediction"], dtype=float) - np.asarray(empirical["shadow_radius"], dtype=float),
    }


def compute_metrics(empirical: dict[str, Any], prediction: dict[str, Any], residuals: dict[str, np.ndarray]) -> dict[str, Any]:
    observed = np.concatenate([empirical["ring_diameter"], empirical["shadow_radius"]])
    predicted = np.concatenate([prediction["ring_prediction"], prediction["shadow_prediction"]])
    uncertainty = np.concatenate([empirical["ring_diameter_uncertainty"], empirical["shadow_radius_uncertainty"]])
    metrics = metric_bundle(observed=observed, predicted=predicted, uncertainty=uncertainty, n_params=1)
    metrics["data_status"] = "fixture_only"
    metrics["baseline_model"] = "none"
    metrics["ring_contrast_proxy"] = float(prediction["ring_contrast_proxy"])
    return metrics


def plot_comparison(empirical: dict[str, Any], prediction: dict[str, Any], output_path: str | Path):
    labels = [f"{source} ring" for source in empirical["source"]] + [f"{source} shadow" for source in empirical["source"]]
    observed = np.concatenate([empirical["ring_diameter"], empirical["shadow_radius"]])
    predicted = np.concatenate([prediction["ring_prediction"], prediction["shadow_prediction"]])
    return plot_grouped_bars(
        labels=labels,
        observed=observed,
        predicted=predicted,
        output_path=output_path,
        title="Fixture-backed EHT horizon/shadow comparison",
        ylabel="angular observable",
    )
