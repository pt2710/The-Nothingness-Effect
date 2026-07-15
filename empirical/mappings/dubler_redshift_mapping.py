"""Observable mapping for finite illustrative Dubler redshift comparisons."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from empirical.io import fixture_path, read_csv_rows
from empirical.metrics import metric_bundle, rmse
from the_nothingness_effect._runtime.artifacts.io import save_figure
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.elastic_dubler_effect import dubler_shift


def prepare_empirical_observable(path: str | Path | None = None) -> dict[str, Any]:
    rows = read_csv_rows(path or fixture_path("redshift_clock_fixture.csv"))
    return {
        "case_id": np.array([row["case_id"] for row in rows]),
        "observable_x": np.array([float(row["observable_x"]) for row in rows], dtype=float),
        "observed_shift": np.array([float(row["observed_shift"]) for row in rows], dtype=float),
        "observed_uncertainty": np.array([float(row["observed_uncertainty"]) for row in rows], dtype=float),
        "baseline_shift": np.array([float(row["baseline_shift"]) for row in rows], dtype=float),
        "raw_observed_shift": np.array([float(row.get("raw_observed_shift", row["observed_shift"])) for row in rows], dtype=float),
        "raw_baseline_shift": np.array([float(row.get("raw_baseline_shift", row["baseline_shift"])) for row in rows], dtype=float),
        "reference_label": [row.get("reference_label", "") for row in rows],
        "source_status": [row["source_status"] for row in rows],
        "observable_label": "normalized weak-field potential or height proxy",
        "observable_units": "dimensionless normalized benchmark coordinate",
        "sign_convention": "positive observable_x denotes larger upward potential difference; redshift is recorded as z < 0",
    }


def fit_parameters(empirical: dict[str, Any], beta_grid: np.ndarray | None = None, kd_grid: np.ndarray | None = None) -> dict[str, Any]:
    observable_x = np.asarray(empirical["observable_x"], dtype=float)
    observed = np.asarray(empirical["observed_shift"], dtype=float)
    betas = beta_grid if beta_grid is not None else np.linspace(0.02, 1.25, 180)
    kd_values = kd_grid if kd_grid is not None else np.linspace(0.25, 4.0, 24)
    best = {"beta": float(betas[0]), "K_D": float(kd_values[0]), "score": float("inf")}
    for kd in kd_values:
        for beta in betas:
            predicted = dubler_shift(beta * observable_x, kd)
            score = rmse(observed, predicted)
            if score < best["score"]:
                best = {"beta": float(beta), "K_D": float(kd), "score": float(score)}
    best["parameter_bounds"] = {
        "beta": [float(np.min(betas)), float(np.max(betas))],
        "K_D": [float(np.min(kd_values)), float(np.max(kd_values))],
    }
    best["formula"] = "z_TNE = exp(-(beta * observable_x) / K_D) - 1"
    return best


def prepare_model_prediction(empirical: dict[str, Any], fitted_parameters: dict[str, Any] | None = None) -> dict[str, Any]:
    fit = fitted_parameters or fit_parameters(empirical)
    observable_x = np.asarray(empirical["observable_x"], dtype=float)
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
    source_status = sorted(set(empirical.get("source_status", ["fixture_only"])))
    metrics["data_status"] = source_status[0] if len(source_status) == 1 else "mixed"
    metrics["baseline_model"] = "published_or_fixture_baseline_shift"
    metrics["sign_consistent"] = bool(np.all(np.sign(prediction["tne_prediction"]) == np.sign(empirical["observed_shift"])))
    metrics["holdout_feasible"] = False
    metrics["TNE_vs_baseline_note"] = (
        "Improved preliminary residual fit under the implemented proxy mapping."
        if metrics["RMSE"] < metrics["baseline_RMSE"]
        else "Published or fixture baseline remains better or comparable on this small benchmark."
    )
    return metrics


def plot_comparison(empirical: dict[str, Any], prediction: dict[str, Any], output_path: str | Path | dict[str, str | Path]):
    if isinstance(output_path, dict):
        curve_path = Path(output_path["curve"])
        residual_path = Path(output_path["residual"])
    else:
        curve_path = Path(output_path)
        residual_path = curve_path.with_name("dubler_redshift_residuals.png")

    x = np.asarray(empirical["observable_x"], dtype=float)
    fig, axes = plt.subplots(2, 1, figsize=(7.8, 6.2), constrained_layout=True, sharex=True)
    axes[0].errorbar(
        x,
        empirical["observed_shift"],
        yerr=empirical["observed_uncertainty"],
        color="#1f77b4",
        linewidth=1.8,
        marker="o",
        label="observed shift",
    )
    axes[0].plot(x, prediction["tne_prediction"], color="#d62728", linewidth=2.0, marker="s", label="TNE prediction")
    axes[0].plot(x, prediction["baseline_prediction"], color="#2ca02c", linewidth=1.8, linestyle="--", label="published/fixture baseline")
    axes[0].set_title("Finite illustrative Dubler redshift comparison")
    axes[0].set_ylabel("normalized shift")
    axes[0].grid(True, alpha=0.25)
    axes[0].legend(loc="best")
    axes[1].axhline(0.0, color="black", linewidth=0.8, linestyle="--")
    axes[1].plot(x, prediction["tne_prediction"] - empirical["observed_shift"], color="#d62728", linewidth=2.0, marker="o", label="TNE residual")
    axes[1].plot(x, prediction["baseline_prediction"] - empirical["observed_shift"], color="#2ca02c", linewidth=1.8, linestyle="--", label="baseline residual")
    axes[1].set_xlabel("normalized observable_x")
    axes[1].set_ylabel("residual")
    axes[1].grid(True, alpha=0.25)
    axes[1].legend(loc="best")
    if curve_path.exists():
        curve_path.unlink()
    save_figure(fig, curve_path, dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.4, 4.0), constrained_layout=True)
    ax.axhline(0.0, color="black", linewidth=0.8, linestyle="--")
    ax.scatter(x, (prediction["tne_prediction"] - empirical["observed_shift"]) / (empirical["observed_uncertainty"] + 1e-12), color="#d62728", s=50, label="TNE normalized residual")
    ax.scatter(x, (prediction["baseline_prediction"] - empirical["observed_shift"]) / (empirical["observed_uncertainty"] + 1e-12), color="#2ca02c", s=50, label="baseline normalized residual")
    ax.set_title("Dubler redshift residual diagnostics")
    ax.set_xlabel("normalized observable_x")
    ax.set_ylabel("residual / uncertainty")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    if residual_path.exists():
        residual_path.unlink()
    save_figure(fig, residual_path, dpi=220)
    plt.close(fig)
    return [curve_path, residual_path]
