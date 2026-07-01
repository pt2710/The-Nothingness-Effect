"""Observable mapping for fixture-backed Hawking-like flux comparisons."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from empirical.io import fixture_path, read_csv_rows
from empirical.metrics import metric_bundle
from empirical.visualization.plot_empirical_comparisons import plot_series_comparison
from equations.black_hole_dynamics.black_hole_dynamics import BlackHoleParams, simulate_black_hole_dynamics


@lru_cache(maxsize=1)
def _black_hole_result() -> dict[str, Any]:
    return simulate_black_hole_dynamics(BlackHoleParams())


def _fit_exponential_baseline(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    positive = np.maximum(y, 1e-12)
    slope, intercept = np.polyfit(x, np.log(positive), deg=1)
    return float(np.exp(intercept)), float(-slope)


def prepare_empirical_observable(path: str | Path | None = None) -> dict[str, Any]:
    rows = read_csv_rows(path or fixture_path("hawking_flux_fixture.csv"))
    return {
        "x": np.asarray([float(row["x"]) for row in rows], dtype=float),
        "flux": np.asarray([float(row["flux"]) for row in rows], dtype=float),
        "flux_uncertainty": np.asarray([float(row["flux_uncertainty"]) for row in rows], dtype=float),
        "source_type": [row["source_type"] for row in rows],
        "source_status": [row["source_status"] for row in rows],
    }


def fit_parameters(empirical: dict[str, Any]) -> dict[str, float]:
    result = _black_hole_result()
    x = np.asarray(empirical["x"], dtype=float)
    model_time = np.linspace(float(np.min(x)), float(np.max(x)), len(result["flux_proxy"]))
    base = np.interp(x, model_time, result["flux_proxy"])
    amplitude_scale = float(np.dot(empirical["flux"], base) / (np.dot(base, base) + 1e-12))
    baseline_amp, baseline_decay = _fit_exponential_baseline(x, np.asarray(empirical["flux"], dtype=float))
    return {
        "amplitude_scale": amplitude_scale,
        "baseline_amplitude": baseline_amp,
        "baseline_decay": baseline_decay,
    }


def prepare_model_prediction(empirical: dict[str, Any], fitted_parameters: dict[str, float] | None = None) -> dict[str, Any]:
    fit = fitted_parameters or fit_parameters(empirical)
    result = _black_hole_result()
    x = np.asarray(empirical["x"], dtype=float)
    model_time = np.linspace(float(np.min(x)), float(np.max(x)), len(result["flux_proxy"]))
    base = np.interp(x, model_time, result["flux_proxy"])
    tne = fit["amplitude_scale"] * base
    baseline = fit["baseline_amplitude"] * np.exp(-fit["baseline_decay"] * x)
    return {
        "tne_prediction": tne,
        "baseline_prediction": baseline,
        "fitted_parameters": fit,
    }


def compute_residuals(empirical: dict[str, Any], prediction: dict[str, Any]) -> dict[str, np.ndarray]:
    observed = np.asarray(empirical["flux"], dtype=float)
    return {
        "tne_residual": np.asarray(prediction["tne_prediction"], dtype=float) - observed,
        "baseline_residual": np.asarray(prediction["baseline_prediction"], dtype=float) - observed,
    }


def compute_metrics(empirical: dict[str, Any], prediction: dict[str, Any], residuals: dict[str, np.ndarray]) -> dict[str, Any]:
    metrics = metric_bundle(
        observed=np.asarray(empirical["flux"], dtype=float),
        predicted=np.asarray(prediction["tne_prediction"], dtype=float),
        uncertainty=np.asarray(empirical["flux_uncertainty"], dtype=float),
        n_params=1,
        baseline=np.asarray(prediction["baseline_prediction"], dtype=float),
        baseline_params=2,
    )
    metrics["data_status"] = "fixture_only"
    metrics["baseline_model"] = "exponential_decay_baseline"
    return metrics


def plot_comparison(empirical: dict[str, Any], prediction: dict[str, Any], output_path: str | Path):
    return plot_series_comparison(
        x=np.asarray(empirical["x"], dtype=float),
        observed=np.asarray(empirical["flux"], dtype=float),
        predicted=np.asarray(prediction["tne_prediction"], dtype=float),
        baseline=np.asarray(prediction["baseline_prediction"], dtype=float),
        uncertainty=np.asarray(empirical["flux_uncertainty"], dtype=float),
        output_path=output_path,
        title="Fixture-backed Hawking-like flux comparison",
        xlabel="normalized coordinate",
        ylabel="flux",
        baseline_label="exponential baseline",
    )
