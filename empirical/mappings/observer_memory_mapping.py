"""Observable mapping for fixture-backed observer-memory comparisons."""

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


def _normalize_signal(values: np.ndarray) -> np.ndarray:
    centered = np.asarray(values, dtype=float) - float(np.mean(values))
    return centered / (float(np.max(np.abs(centered))) + 1e-12)


def prepare_empirical_observable(path: str | Path | None = None) -> dict[str, Any]:
    rows = read_csv_rows(path or fixture_path("ligo_ringdown_fixture.csv"))
    return {
        "time": np.asarray([float(row["time"]) for row in rows], dtype=float),
        "strain": np.asarray([float(row["strain"]) for row in rows], dtype=float),
        "strain_uncertainty": np.asarray([float(row["strain_uncertainty"]) for row in rows], dtype=float),
        "event_id": [row["event_id"] for row in rows],
        "source_status": [row["source_status"] for row in rows],
    }


def fit_parameters(empirical: dict[str, Any]) -> dict[str, float]:
    result = _black_hole_result()
    time = np.asarray(empirical["time"], dtype=float)
    model_time = np.linspace(float(np.min(time)), float(np.max(time)), len(result["memory"]))
    memory = _normalize_signal(result["memory"])
    distance = _normalize_signal(result["observer_distance"])
    proxy = memory + 0.45 * np.gradient(distance, model_time)
    proxy_interp = np.interp(time, model_time, proxy)
    amplitude = float(np.dot(empirical["strain"], proxy_interp) / (np.dot(proxy_interp, proxy_interp) + 1e-12))
    return {"amplitude_scale": amplitude}


def prepare_model_prediction(empirical: dict[str, Any], fitted_parameters: dict[str, float] | None = None) -> dict[str, Any]:
    fit = fitted_parameters or fit_parameters(empirical)
    result = _black_hole_result()
    time = np.asarray(empirical["time"], dtype=float)
    model_time = np.linspace(float(np.min(time)), float(np.max(time)), len(result["memory"]))
    memory = _normalize_signal(result["memory"])
    distance = _normalize_signal(result["observer_distance"])
    proxy = memory + 0.45 * np.gradient(distance, model_time)
    prediction = fit["amplitude_scale"] * np.interp(time, model_time, proxy)
    return {
        "tne_prediction": prediction,
        "memory_derivative_proxy": np.interp(time, model_time, np.gradient(memory, model_time)),
        "cumulative_memory_proxy": np.interp(time, model_time, np.cumsum(memory)),
        "fitted_parameters": fit,
    }


def compute_residuals(empirical: dict[str, Any], prediction: dict[str, Any]) -> dict[str, np.ndarray]:
    observed = np.asarray(empirical["strain"], dtype=float)
    return {"tne_residual": np.asarray(prediction["tne_prediction"], dtype=float) - observed}


def compute_metrics(empirical: dict[str, Any], prediction: dict[str, Any], residuals: dict[str, np.ndarray]) -> dict[str, Any]:
    metrics = metric_bundle(
        observed=np.asarray(empirical["strain"], dtype=float),
        predicted=np.asarray(prediction["tne_prediction"], dtype=float),
        uncertainty=np.asarray(empirical["strain_uncertainty"], dtype=float),
        n_params=1,
    )
    source_status = sorted(set(empirical.get("source_status", ["fixture_only"])))
    metrics["data_status"] = source_status[0] if len(source_status) == 1 else "mixed"
    metrics["baseline_model"] = "none"
    return metrics


def plot_comparison(empirical: dict[str, Any], prediction: dict[str, Any], output_path: str | Path):
    return plot_series_comparison(
        x=np.asarray(empirical["time"], dtype=float),
        observed=np.asarray(empirical["strain"], dtype=float),
        predicted=np.asarray(prediction["tne_prediction"], dtype=float),
        uncertainty=np.asarray(empirical["strain_uncertainty"], dtype=float),
        output_path=output_path,
        title="Observer-memory comparison",
        xlabel="time",
        ylabel="strain / proxy",
        predicted_label="observer-memory proxy",
    )
