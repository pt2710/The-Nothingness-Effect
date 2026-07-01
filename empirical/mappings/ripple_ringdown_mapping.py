"""Observable mapping for fixture-backed elastic-pi ringdown comparisons."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from empirical.io import fixture_path, read_csv_rows
from empirical.metrics import metric_bundle, rmse
from empirical.visualization.plot_empirical_comparisons import plot_residuals, plot_series_comparison
from equations.elastic_pi_ripples.elastic_pi_ripples import RippleParams, simulate_elastic_pi_ripple


def _fit_damped_sinusoid(time: np.ndarray, observed: np.ndarray) -> dict[str, float]:
    best = {"tau": 0.2, "frequency": 2.0, "phase": 0.0, "amplitude": 1.0, "score": float("inf")}
    for tau in np.linspace(0.12, 0.85, 12):
        decay = np.exp(-time / tau)
        for frequency in np.linspace(0.8, 3.8, 16):
            base_angle = 2.0 * np.pi * frequency * time
            for phase in np.linspace(0.0, 2.0 * np.pi, 12, endpoint=False):
                basis = decay * np.cos(base_angle + phase)
                amplitude = float(np.dot(observed, basis) / (np.dot(basis, basis) + 1e-12))
                prediction = amplitude * basis
                score = rmse(observed, prediction)
                if score < best["score"]:
                    best = {
                        "tau": float(tau),
                        "frequency": float(frequency),
                        "phase": float(phase),
                        "amplitude": amplitude,
                        "score": float(score),
                    }
    return best


@lru_cache(maxsize=1)
def _tne_ringdown_series() -> dict[str, Any]:
    params = RippleParams(n=240, steps=300)
    result = simulate_elastic_pi_ripple(params)
    center_index = len(result["x"]) // 2
    return {
        "params": params.__dict__,
        "time": np.asarray(result["time"], dtype=float),
        "signal": np.asarray(result["history"][:, center_index], dtype=float),
        "metrics": result["metrics"],
    }


def prepare_empirical_observable(path: str | Path | None = None) -> dict[str, Any]:
    rows = read_csv_rows(path or fixture_path("ligo_ringdown_fixture.csv"))
    return {
        "time": np.asarray([float(row["time"]) for row in rows], dtype=float),
        "strain": np.asarray([float(row["strain"]) for row in rows], dtype=float),
        "strain_uncertainty": np.asarray([float(row["strain_uncertainty"]) for row in rows], dtype=float),
        "event_id": [row["event_id"] for row in rows],
        "source_status": [row["source_status"] for row in rows],
    }


def fit_parameters(empirical: dict[str, Any]) -> dict[str, Any]:
    observed = np.asarray(empirical["strain"], dtype=float)
    time = np.asarray(empirical["time"], dtype=float)
    baseline_fit = _fit_damped_sinusoid(time, observed)
    tne = _tne_ringdown_series()
    best_tne = {"time_scale": 1.0, "amplitude": 1.0, "score": float("inf")}
    for time_scale in np.linspace(0.7, 1.35, 16):
        mapped = np.interp(time / time_scale, tne["time"], tne["signal"], left=tne["signal"][0], right=tne["signal"][-1])
        amplitude = float(np.dot(observed, mapped) / (np.dot(mapped, mapped) + 1e-12))
        prediction = amplitude * mapped
        score = rmse(observed, prediction)
        if score < best_tne["score"]:
            best_tne = {"time_scale": float(time_scale), "amplitude": amplitude, "score": float(score)}
    return {"baseline": baseline_fit, "tne": best_tne, "tne_series": tne}


def prepare_model_prediction(empirical: dict[str, Any], fitted_parameters: dict[str, Any] | None = None) -> dict[str, Any]:
    fit = fitted_parameters or fit_parameters(empirical)
    time = np.asarray(empirical["time"], dtype=float)
    baseline = fit["baseline"]["amplitude"] * np.exp(-time / fit["baseline"]["tau"]) * np.cos(
        2.0 * np.pi * fit["baseline"]["frequency"] * time + fit["baseline"]["phase"]
    )
    tne_series = fit["tne_series"]
    mapped = np.interp(time / fit["tne"]["time_scale"], tne_series["time"], tne_series["signal"], left=tne_series["signal"][0], right=tne_series["signal"][-1])
    tne_prediction = fit["tne"]["amplitude"] * mapped
    return {
        "tne_prediction": tne_prediction,
        "baseline_prediction": baseline,
        "fitted_parameters": {
            "tne": fit["tne"],
            "baseline": fit["baseline"],
        },
    }


def compute_residuals(empirical: dict[str, Any], prediction: dict[str, Any]) -> dict[str, np.ndarray]:
    observed = np.asarray(empirical["strain"], dtype=float)
    return {
        "tne_residual": np.asarray(prediction["tne_prediction"], dtype=float) - observed,
        "baseline_residual": np.asarray(prediction["baseline_prediction"], dtype=float) - observed,
    }


def compute_metrics(empirical: dict[str, Any], prediction: dict[str, Any], residuals: dict[str, np.ndarray]) -> dict[str, Any]:
    metrics = metric_bundle(
        observed=np.asarray(empirical["strain"], dtype=float),
        predicted=np.asarray(prediction["tne_prediction"], dtype=float),
        uncertainty=np.asarray(empirical["strain_uncertainty"], dtype=float),
        n_params=2,
        baseline=np.asarray(prediction["baseline_prediction"], dtype=float),
        baseline_params=4,
    )
    metrics["data_status"] = "fixture_only"
    metrics["baseline_model"] = "damped_sinusoid_baseline"
    metrics["TNE_vs_baseline_note"] = "Preliminary fixture-backed comparison only."
    return metrics


def plot_comparison(empirical: dict[str, Any], prediction: dict[str, Any], output_path: str | Path | dict[str, str | Path]):
    if isinstance(output_path, dict):
        curve_path = output_path["curve"]
        residual_path = output_path["residual"]
    else:
        curve_path = output_path
        residual_path = Path(output_path).with_name("elastic_pi_ringdown_residuals.png")
    curve = plot_series_comparison(
        x=np.asarray(empirical["time"], dtype=float),
        observed=np.asarray(empirical["strain"], dtype=float),
        predicted=np.asarray(prediction["tne_prediction"], dtype=float),
        baseline=np.asarray(prediction["baseline_prediction"], dtype=float),
        uncertainty=np.asarray(empirical["strain_uncertainty"], dtype=float),
        output_path=curve_path,
        title="Fixture-backed elastic-π ringdown comparison",
        xlabel="time",
        ylabel="strain / proxy",
        baseline_label="damped sinusoid baseline",
    )
    residual = plot_residuals(
        x=np.asarray(empirical["time"], dtype=float),
        residuals=np.asarray(prediction["tne_prediction"], dtype=float) - np.asarray(empirical["strain"], dtype=float),
        output_path=residual_path,
        title="Elastic-π ringdown residuals",
        xlabel="time",
    )
    return [curve, residual]
