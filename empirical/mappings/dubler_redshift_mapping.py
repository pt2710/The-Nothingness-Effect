"""Observable mapping for fixture-backed Dubler redshift comparisons."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from empirical.io import fixture_path, read_csv_rows
from empirical.metrics import metric_bundle, rmse
from empirical.visualization.plot_empirical_comparisons import plot_series_comparison
from equations.elastic_dubler_effect.elastic_dubler_effect import dubler_shift


def prepare_empirical_observable(path: str | Path | None = None) -> dict[str, Any]:
    rows = read_csv_rows(path or fixture_path("redshift_clock_fixture.csv"))
    return {
        "case_id": np.array([row["case_id"] for row in rows]),
        "observable_x": np.array([float(row["observable_x"]) for row in rows], dtype=float),
        "observed_shift": np.array([float(row["observed_shift"]) for row in rows], dtype=float),
        "observed_uncertainty": np.array([float(row["observed_uncertainty"]) for row in rows], dtype=float),
        "baseline_shift": np.array([float(row["baseline_shift"]) for row in rows], dtype=float),
        "source_status": [row["source_status"] for row in rows],
    }


def fit_parameters(empirical: dict[str, Any], beta_grid: np.ndarray | None = None, kd_grid: np.ndarray | None = None) -> dict[str, float]:
    observable_x = empirical["observable_x"]
    observed = empirical["observed_shift"]
    betas = beta_grid if beta_grid is not None else np.linspace(0.05, 1.0, 120)
    kd_values = kd_grid if kd_grid is not None else np.array([0.5, 1.0, 2.0, 5.0], dtype=float)
    best = {"beta": float(betas[0]), "K_D": float(kd_values[0]), "score": float("inf")}
    for kd in kd_values:
        for beta in betas:
            predicted = dubler_shift(beta * observable_x, kd)
            score = rmse(observed, predicted)
            if score < best["score"]:
                best = {"beta": float(beta), "K_D": float(kd), "score": float(score)}
    return best


def prepare_model_prediction(empirical: dict[str, Any], fitted_parameters: dict[str, float] | None = None) -> dict[str, Any]:
    fit = fitted_parameters or fit_parameters(empirical)
    observable_x = empirical["observable_x"]
    predicted = dubler_shift(fit["beta"] * observable_x, fit["K_D"])
    return {
        "tne_prediction": np.asarray(predicted, dtype=float),
        "baseline_prediction": np.asarray(empirical["baseline_shift"], dtype=float),
        "fitted_parameters": fit,
    }


def compute_residuals(empirical: dict[str, Any], prediction: dict[str, Any]) -> dict[str, np.ndarray]:
    observed = np.asarray(empirical["observed_shift"], dtype=float)
    return {
        "tne_residual": np.asarray(prediction["tne_prediction"], dtype=float) - observed,
        "baseline_residual": np.asarray(prediction["baseline_prediction"], dtype=float) - observed,
    }


def compute_metrics(empirical: dict[str, Any], prediction: dict[str, Any], residuals: dict[str, np.ndarray]) -> dict[str, Any]:
    metrics = metric_bundle(
        observed=np.asarray(empirical["observed_shift"], dtype=float),
        predicted=np.asarray(prediction["tne_prediction"], dtype=float),
        uncertainty=np.asarray(empirical["observed_uncertainty"], dtype=float),
        n_params=2,
        baseline=np.asarray(prediction["baseline_prediction"], dtype=float),
        baseline_params=1,
    )
    metrics["data_status"] = "fixture_only"
    metrics["baseline_model"] = "fixture_baseline_shift"
    metrics["TNE_vs_baseline_note"] = "Fixture-backed residual comparison only."
    return metrics


def plot_comparison(empirical: dict[str, Any], prediction: dict[str, Any], output_path: str | Path):
    x = np.asarray(empirical["observable_x"], dtype=float)
    return plot_series_comparison(
        x=x,
        observed=np.asarray(empirical["observed_shift"], dtype=float),
        predicted=np.asarray(prediction["tne_prediction"], dtype=float),
        baseline=np.asarray(prediction["baseline_prediction"], dtype=float),
        uncertainty=np.asarray(empirical["observed_uncertainty"], dtype=float),
        output_path=output_path,
        title="Fixture-backed Dubler redshift comparison",
        xlabel="observable X",
        ylabel="shift",
        baseline_label="fixture baseline shift",
    )
