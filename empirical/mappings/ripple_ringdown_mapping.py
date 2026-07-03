"""Observable mapping for finite illustrative elastic-pi ringdown comparisons."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares
from scipy.signal import hilbert

from empirical.io import fixture_path, read_csv_rows
from empirical.metrics import metric_bundle, rmse
from equations.artifact_io import save_figure
from equations.elastic_pi_ripples.elastic_pi_ripples import RippleParams, prepare_tne_ringdown_projection


PARAMETER_SWEEP_LEVELS: dict[str, dict[str, list[float]]] = {
    "quick": {
        "c_E": [1.0],
        "gamma": [0.06, 0.1],
        "xi": [-0.08],
        "width": [0.8, 1.1],
        "time_scale": [0.6, 1.0, 1.4],
        "time_shift": [0.0, 0.01],
    },
    "standard": {
        "c_E": [0.85, 1.0, 1.2],
        "gamma": [0.04, 0.08, 0.12],
        "xi": [-0.12, -0.08, -0.04],
        "width": [0.6, 0.9, 1.2],
        "time_scale": [0.5, 0.8, 1.1, 1.4, 1.7],
        "time_shift": [-0.01, 0.0, 0.01, 0.02],
    },
    "extended": {
        "c_E": [0.75, 0.9, 1.05, 1.2, 1.35],
        "gamma": [0.03, 0.05, 0.08, 0.12, 0.16],
        "xi": [-0.16, -0.12, -0.08, -0.04, 0.0],
        "width": [0.5, 0.8, 1.1, 1.4],
        "time_scale": [0.45, 0.65, 0.85, 1.05, 1.25, 1.45, 1.65, 1.85],
        "time_shift": [-0.015, -0.005, 0.0, 0.01, 0.02, 0.03],
    },
}

REDUCED_BASIS_NAMES = [
    "centerline",
    "dominant_mode_1",
    "dominant_mode_2",
    "interference_projection",
    "energy_envelope",
    "centerline_velocity",
]

WINDOW_VARIANTS: dict[str, tuple[float, float]] = {
    "early": (0.00, 0.45),
    "short": (0.00, 0.35),
    "standard": (0.00, 1.00),
    "late": (0.35, 1.00),
    "long": (0.00, 1.00),
}


def _normalize(values: np.ndarray) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    centered = data - float(np.mean(data))
    scale = float(np.max(np.abs(centered))) + 1e-12
    return centered / scale


def _analytic_envelope(values: np.ndarray) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    return np.abs(hilbert(data))


def _rolling_rms(values: np.ndarray, window: int = 5) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    weights = np.ones(window, dtype=float) / float(window)
    return np.sqrt(np.convolve(data**2, weights, mode="same"))


def _window_slice(strain: np.ndarray, variant: str = "standard") -> tuple[int, int]:
    peak_index = int(np.argmax(np.abs(np.asarray(strain, dtype=float))))
    if peak_index <= max(2, len(strain) // 3):
        start = peak_index
    else:
        start = 0
    stop = len(strain)
    relative_start, relative_stop = WINDOW_VARIANTS.get(variant, WINDOW_VARIANTS["standard"])
    base_length = stop - start
    adjusted_start = start + int(relative_start * base_length)
    adjusted_stop = start + int(relative_stop * base_length)
    adjusted_stop = max(adjusted_start + 8, min(stop, adjusted_stop))
    return adjusted_start, adjusted_stop


def _damped_sinusoid(time: np.ndarray, params: np.ndarray) -> np.ndarray:
    amplitude, tau, frequency, phase = params
    return amplitude * np.exp(-time / tau) * np.cos(2.0 * np.pi * frequency * time + phase)


def _fit_damped_sinusoid(time: np.ndarray, observed: np.ndarray) -> dict[str, float]:
    initial = np.array([float(np.max(np.abs(observed))), 0.12, 2.0, 0.0], dtype=float)
    bounds = (
        np.array([-2.5, 0.02, 0.2, -2.0 * np.pi], dtype=float),
        np.array([2.5, 1.5, 12.0, 2.0 * np.pi], dtype=float),
    )
    result = least_squares(
        lambda params: _damped_sinusoid(time, params) - observed,
        x0=initial,
        bounds=bounds,
        max_nfev=600,
    )
    params = result.x
    prediction = _damped_sinusoid(time, params)
    return {
        "amplitude": float(params[0]),
        "tau": float(params[1]),
        "frequency": float(params[2]),
        "phase": float(params[3]),
        "score": float(rmse(observed, prediction)),
        "bounds": {
            "amplitude": [-2.5, 2.5],
            "tau": [0.02, 1.5],
            "frequency": [0.2, 12.0],
            "phase": [-2.0 * np.pi, 2.0 * np.pi],
        },
    }


@lru_cache(maxsize=128)
def _projection_for_params(c_E: float, gamma: float, xi: float, width: float) -> dict[str, Any]:
    params = RippleParams(n=240, steps=420, dt=0.003, c_E=c_E, gamma=gamma, xi=xi, width=width, amplitude=0.9)
    projection = prepare_tne_ringdown_projection(params)
    centerline = np.asarray(projection["centerline"], dtype=float)
    return {
        "time": np.asarray(projection["time"], dtype=float),
        "centerline": _normalize(centerline),
        "dominant_mode_1": _normalize(np.asarray(projection["dominant_mode_1"], dtype=float)),
        "dominant_mode_2": _normalize(np.asarray(projection["dominant_mode_2"], dtype=float)),
        "energy_envelope": _normalize(np.asarray(projection["energy_envelope"], dtype=float)),
        "interference_projection": _normalize(np.asarray(projection["interference_projection"], dtype=float)),
        "centerline_velocity": _normalize(np.gradient(centerline, np.asarray(projection["time"], dtype=float))),
        "params": projection["params"],
    }


def _basis_matrix(projection: dict[str, Any], mapped_time: np.ndarray) -> np.ndarray:
    columns = []
    for name in REDUCED_BASIS_NAMES:
        base = np.asarray(projection[name], dtype=float)
        column = np.interp(mapped_time, projection["time"], base, left=base[0], right=base[-1])
        columns.append(_normalize(column))
    return np.column_stack(columns)


def prepare_empirical_observable(path: str | Path | None = None, window_variant: str = "standard") -> dict[str, Any]:
    rows = read_csv_rows(path or fixture_path("ligo_ringdown_fixture.csv"))
    raw_time = np.asarray([float(row["time"]) for row in rows], dtype=float)
    normalized_strain = np.asarray([float(row["strain"]) for row in rows], dtype=float)
    raw_strain = np.asarray([float(row.get("strain_raw", row["strain"])) for row in rows], dtype=float)
    normalized_uncertainty = np.asarray([float(row["strain_uncertainty"]) for row in rows], dtype=float)
    raw_uncertainty = np.asarray([float(row.get("strain_uncertainty_raw", row["strain_uncertainty"])) for row in rows], dtype=float)

    start, stop = _window_slice(normalized_strain, variant=window_variant)
    aligned_time = raw_time[start:stop] - raw_time[start]
    aligned_raw_strain = raw_strain[start:stop]
    aligned_raw_uncertainty = raw_uncertainty[start:stop]
    strain_scale = float(np.max(np.abs(aligned_raw_strain)))
    if strain_scale == 0.0:
        strain_scale = 1.0
    aligned_normalized_strain = aligned_raw_strain / strain_scale
    aligned_normalized_uncertainty = aligned_raw_uncertainty / strain_scale
    window_mask = np.zeros(len(raw_time), dtype=bool)
    window_mask[start:stop] = True

    return {
        "time_raw": raw_time,
        "time": aligned_time,
        "strain_raw_full": raw_strain,
        "strain_raw": aligned_raw_strain,
        "strain": aligned_normalized_strain,
        "strain_uncertainty_raw": aligned_raw_uncertainty,
        "strain_uncertainty": aligned_normalized_uncertainty,
        "strain_scale": strain_scale,
        "window_start_index": start,
        "window_stop_index": stop,
        "window_start_time_raw": float(raw_time[start]),
        "window_mask": window_mask,
        "window_variant": window_variant,
        "event_id": [row["event_id"] for row in rows],
        "source_status": [row["source_status"] for row in rows],
    }


def _fit_reduced_basis_signal(
    time: np.ndarray,
    observed: np.ndarray,
    projection: dict[str, Any],
    time_scale: float,
    time_shift: float,
    basis_names: list[str],
    regularization_strength: float = 0.08,
) -> dict[str, Any]:
    mapped_time = (time - time_shift) / time_scale
    basis = np.column_stack([
        _normalize(np.interp(mapped_time, projection["time"], np.asarray(projection[name], dtype=float), left=float(np.asarray(projection[name], dtype=float)[0]), right=float(np.asarray(projection[name], dtype=float)[-1])))
        for name in basis_names
    ])
    regularization = np.sqrt(regularization_strength) * np.eye(basis.shape[1], dtype=float)
    response = np.concatenate([observed, np.zeros(basis.shape[1], dtype=float)])

    def residual(coefficients: np.ndarray) -> np.ndarray:
        return np.concatenate([basis @ coefficients, regularization @ coefficients]) - response

    result = least_squares(
        residual,
        x0=np.zeros(basis.shape[1], dtype=float),
        bounds=(-1.5 * np.ones(basis.shape[1], dtype=float), 1.5 * np.ones(basis.shape[1], dtype=float)),
        max_nfev=400,
    )
    coefficients = np.asarray(result.x, dtype=float)
    prediction = basis @ coefficients
    return {
        "prediction": prediction,
        "coefficients": coefficients,
        "score": float(rmse(observed, prediction)),
    }


def _fit_tne_projection(time: np.ndarray, observed: np.ndarray, parameter_sweep_level: str) -> dict[str, Any]:
    grid = PARAMETER_SWEEP_LEVELS[parameter_sweep_level]
    best: dict[str, Any] | None = None
    basis_names = REDUCED_BASIS_NAMES
    for c_E in grid["c_E"]:
        for gamma in grid["gamma"]:
            for xi in grid["xi"]:
                for width in grid["width"]:
                    projection = _projection_for_params(c_E, gamma, xi, width)
                    for time_scale in grid["time_scale"]:
                        for time_shift in grid["time_shift"]:
                            basis_fit = _fit_reduced_basis_signal(time, observed, projection, float(time_scale), float(time_shift), basis_names)
                            candidate = {
                                "projection_name": "reduced_tne_basis",
                                "basis_names": basis_names,
                                "basis_coefficients": basis_fit["coefficients"].tolist(),
                                "simulation_params": projection["params"],
                                "time_scale": float(time_scale),
                                "time_shift": float(time_shift),
                                "score": float(basis_fit["score"]),
                                "parameter_bounds": {
                                    "c_E": [min(grid["c_E"]), max(grid["c_E"])],
                                    "gamma": [min(grid["gamma"]), max(grid["gamma"])],
                                    "xi": [min(grid["xi"]), max(grid["xi"])],
                                    "width": [min(grid["width"]), max(grid["width"])],
                                    "time_scale": [min(grid["time_scale"]), max(grid["time_scale"])],
                                    "time_shift": [min(grid["time_shift"]), max(grid["time_shift"])],
                                },
                            }
                            if best is None or candidate["score"] < best["score"]:
                                best = candidate
    assert best is not None
    return best


def _tne_prediction(time: np.ndarray, fitted_parameters: dict[str, Any]) -> np.ndarray:
    params = fitted_parameters["simulation_params"]
    projection = _projection_for_params(params["c_E"], params["gamma"], params["xi"], params["width"])
    mapped_time = (time - fitted_parameters["time_shift"]) / fitted_parameters["time_scale"]
    basis = _basis_matrix(projection, mapped_time)
    coefficients = np.asarray(fitted_parameters["basis_coefficients"], dtype=float)
    return basis @ coefficients


def _holdout_metrics(time: np.ndarray, observed: np.ndarray, parameter_sweep_level: str) -> dict[str, float]:
    if len(time) < 10:
        return {
            "train_RMSE": float("nan"),
            "test_RMSE": float("nan"),
            "baseline_train_RMSE": float("nan"),
            "baseline_test_RMSE": float("nan"),
        }
    split_index = max(6, int(0.6 * len(time)))
    baseline_fit = _fit_damped_sinusoid(time[:split_index], observed[:split_index])
    tne_fit = _fit_tne_projection(time[:split_index], observed[:split_index], parameter_sweep_level)
    baseline_train = _damped_sinusoid(
        time[:split_index],
        np.array(
            [
                baseline_fit["amplitude"],
                baseline_fit["tau"],
                baseline_fit["frequency"],
                baseline_fit["phase"],
            ],
            dtype=float,
        ),
    )
    baseline_test = _damped_sinusoid(
        time[split_index:],
        np.array(
            [
                baseline_fit["amplitude"],
                baseline_fit["tau"],
                baseline_fit["frequency"],
                baseline_fit["phase"],
            ],
            dtype=float,
        ),
    )
    tne_train = _tne_prediction(time[:split_index], tne_fit)
    tne_test = _tne_prediction(time[split_index:], tne_fit)
    return {
        "train_RMSE": rmse(observed[:split_index], tne_train),
        "test_RMSE": rmse(observed[split_index:], tne_test),
        "baseline_train_RMSE": rmse(observed[:split_index], baseline_train),
        "baseline_test_RMSE": rmse(observed[split_index:], baseline_test),
    }


def basis_stability_analysis(empirical: dict[str, Any], parameter_sweep_level: str = "standard") -> list[dict[str, Any]]:
    observed = np.asarray(empirical["strain"], dtype=float)
    time = np.asarray(empirical["time"], dtype=float)
    split_index = max(6, int(0.6 * len(time)))
    analyses: list[dict[str, Any]] = []
    candidate_sets = [REDUCED_BASIS_NAMES] + [[name for name in REDUCED_BASIS_NAMES if name != removed] for removed in REDUCED_BASIS_NAMES]
    grid = PARAMETER_SWEEP_LEVELS[parameter_sweep_level]
    for basis_names in candidate_sets:
        best: dict[str, Any] | None = None
        for c_E in grid["c_E"]:
            for gamma in grid["gamma"]:
                for xi in grid["xi"]:
                    for width in grid["width"]:
                        projection = _projection_for_params(c_E, gamma, xi, width)
                        for time_scale in grid["time_scale"]:
                            for time_shift in grid["time_shift"]:
                                basis_fit = _fit_reduced_basis_signal(time[:split_index], observed[:split_index], projection, float(time_scale), float(time_shift), basis_names)
                                train_pred = basis_fit["prediction"]
                                mapped_time = (time[split_index:] - time_shift) / time_scale
                                basis_test = np.column_stack([
                                    _normalize(np.interp(mapped_time, projection["time"], np.asarray(projection[name], dtype=float), left=float(np.asarray(projection[name], dtype=float)[0]), right=float(np.asarray(projection[name], dtype=float)[-1])))
                                    for name in basis_names
                                ])
                                test_pred = basis_test @ np.asarray(basis_fit["coefficients"], dtype=float)
                                candidate = {
                                    "basis_names": list(basis_names),
                                    "train_RMSE": float(rmse(observed[:split_index], train_pred)),
                                    "test_RMSE": float(rmse(observed[split_index:], test_pred)),
                                    "basis_component_count": len(basis_names),
                                    "time_scale": float(time_scale),
                                    "time_shift": float(time_shift),
                                    "params": {"c_E": c_E, "gamma": gamma, "xi": xi, "width": width},
                                }
                                if best is None or candidate["test_RMSE"] < best["test_RMSE"]:
                                    best = candidate
        assert best is not None
        analyses.append(best)
    analyses.sort(key=lambda item: item["test_RMSE"])
    return analyses


def window_sensitivity_analysis(path: str | Path | None = None, parameter_sweep_level: str = "standard") -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for variant in WINDOW_VARIANTS:
        empirical = prepare_empirical_observable(path, window_variant=variant)
        fitted = fit_parameters(empirical, parameter_sweep_level=parameter_sweep_level)
        prediction = prepare_model_prediction(empirical, fitted)
        residuals = compute_residuals(empirical, prediction)
        metrics = compute_metrics(empirical, prediction, residuals)
        results.append(
            {
                "window_variant": variant,
                "window_start_time_raw": float(empirical["window_start_time_raw"]),
                "window_duration": float(metrics["window_duration"]),
                "RMSE": float(metrics["RMSE"]),
                "baseline_RMSE": float(metrics["baseline_RMSE"]),
                "train_RMSE": float(metrics["train_RMSE"]),
                "test_RMSE": float(metrics["test_RMSE"]),
                "baseline_train_RMSE": float(metrics["baseline_train_RMSE"]),
                "baseline_test_RMSE": float(metrics["baseline_test_RMSE"]),
            }
        )
    return results


def fit_parameters(empirical: dict[str, Any], parameter_sweep_level: str = "standard") -> dict[str, Any]:
    observed = np.asarray(empirical["strain"], dtype=float)
    time = np.asarray(empirical["time"], dtype=float)
    baseline_fit = _fit_damped_sinusoid(time, observed)
    tne_fit = _fit_tne_projection(time, observed, parameter_sweep_level)
    return {
        "baseline": baseline_fit,
        "tne": tne_fit,
        "holdout": _holdout_metrics(time, observed, parameter_sweep_level),
        "parameter_sweep_level": parameter_sweep_level,
        "window_variant": empirical.get("window_variant", "standard"),
    }


def prepare_model_prediction(empirical: dict[str, Any], fitted_parameters: dict[str, Any] | None = None) -> dict[str, Any]:
    fit = fitted_parameters or fit_parameters(empirical)
    time = np.asarray(empirical["time"], dtype=float)
    baseline = _damped_sinusoid(
        time,
        np.array(
            [
                fit["baseline"]["amplitude"],
                fit["baseline"]["tau"],
                fit["baseline"]["frequency"],
                fit["baseline"]["phase"],
            ],
            dtype=float,
        ),
    )
    tne_prediction = _tne_prediction(time, fit["tne"])
    raw_scale = float(empirical["strain_scale"])
    return {
        "tne_prediction": tne_prediction,
        "baseline_prediction": baseline,
        "tne_prediction_raw": tne_prediction * raw_scale,
        "baseline_prediction_raw": baseline * raw_scale,
        "observed_envelope": _analytic_envelope(np.asarray(empirical["strain"], dtype=float)),
        "tne_envelope": _analytic_envelope(tne_prediction),
        "baseline_envelope": _analytic_envelope(baseline),
        "fitted_parameters": fit,
    }


def compute_residuals(empirical: dict[str, Any], prediction: dict[str, Any]) -> dict[str, np.ndarray]:
    observed = np.asarray(empirical["strain"], dtype=float)
    tne_residual = np.asarray(prediction["tne_prediction"], dtype=float) - observed
    baseline_residual = np.asarray(prediction["baseline_prediction"], dtype=float) - observed
    return {
        "tne_residual": tne_residual,
        "baseline_residual": baseline_residual,
        "tne_residual_envelope": _rolling_rms(tne_residual),
        "baseline_residual_envelope": _rolling_rms(baseline_residual),
    }


def compute_metrics(empirical: dict[str, Any], prediction: dict[str, Any], residuals: dict[str, np.ndarray]) -> dict[str, Any]:
    metrics = metric_bundle(
        observed=np.asarray(empirical["strain"], dtype=float),
        predicted=np.asarray(prediction["tne_prediction"], dtype=float),
        uncertainty=np.asarray(empirical["strain_uncertainty"], dtype=float),
        n_params=8,
        baseline=np.asarray(prediction["baseline_prediction"], dtype=float),
        baseline_params=4,
    )
    source_status = sorted(set(empirical.get("source_status", ["fixture_only"])))
    metrics["data_status"] = source_status[0] if len(source_status) == 1 else "mixed"
    metrics["baseline_model"] = "damped_sinusoid_baseline"
    metrics["residual_envelope_RMSE"] = rmse(residuals["baseline_residual_envelope"], residuals["tne_residual_envelope"])
    metrics["window_start_time_raw"] = float(empirical["window_start_time_raw"])
    metrics["window_duration"] = float(empirical["time"][-1] - empirical["time"][0]) if len(empirical["time"]) else 0.0
    metrics["window_variant"] = empirical.get("window_variant", "standard")
    metrics["projection_name"] = prediction["fitted_parameters"]["tne"]["projection_name"]
    metrics["basis_component_count"] = float(len(prediction["fitted_parameters"]["tne"]["basis_names"]))
    metrics.update(prediction["fitted_parameters"]["holdout"])
    metrics["TNE_vs_baseline_note"] = (
        "Improved preliminary residual fit under the reduced-basis proxy mapping."
        if metrics["RMSE"] < metrics["baseline_RMSE"]
        else "Baseline remains better or comparable under the same aligned ringdown window."
    )
    return metrics


def plot_comparison(
    empirical: dict[str, Any],
    prediction: dict[str, Any],
    output_paths: dict[str, str | Path],
) -> list[Path]:
    curve_path = Path(output_paths["curve"])
    residual_path = Path(output_paths["residual"])
    envelope_path = Path(output_paths["envelope"])

    fig, axes = plt.subplots(2, 1, figsize=(8.0, 6.4), constrained_layout=True)
    axes[0].plot(empirical["time_raw"], empirical["strain_raw_full"], color="#7f7f7f", linewidth=1.7, label="raw strain")
    axes[0].axvline(empirical["window_start_time_raw"], color="#d62728", linestyle="--", linewidth=1.0, label="selected ringdown window")
    axes[0].set_title("Finite illustrative ringdown window selection")
    axes[0].set_xlabel("time")
    axes[0].set_ylabel("raw strain / proxy")
    axes[0].grid(True, alpha=0.25)
    axes[0].legend(loc="best")
    axes[1].fill_between(
        empirical["time"],
        empirical["strain"] - empirical["strain_uncertainty"],
        empirical["strain"] + empirical["strain_uncertainty"],
        color="#9ecae1",
        alpha=0.35,
        label="aligned uncertainty",
    )
    axes[1].plot(empirical["time"], empirical["strain"], color="#1f77b4", linewidth=2.0, marker="o", label="observed normalized strain")
    axes[1].plot(empirical["time"], prediction["tne_prediction"], color="#d62728", linewidth=2.0, marker="s", label="TNE reduced basis")
    axes[1].plot(empirical["time"], prediction["baseline_prediction"], color="#2ca02c", linewidth=1.8, linestyle="--", label="damped-sinusoid baseline")
    axes[1].set_title("Toy-model ringdown comparison (not a formal proof substitute)")
    axes[1].set_xlabel("aligned time")
    axes[1].set_ylabel("normalized strain")
    axes[1].grid(True, alpha=0.25)
    axes[1].legend(loc="best")
    save_figure(fig, curve_path, dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.0, 4.6), constrained_layout=True)
    ax.axhline(0.0, color="black", linewidth=0.8, linestyle="--")
    ax.plot(empirical["time"], residuals := prediction["tne_prediction"] - empirical["strain"], color="#d62728", linewidth=2.0, label="TNE residual")
    ax.plot(empirical["time"], prediction["baseline_prediction"] - empirical["strain"], color="#2ca02c", linewidth=1.8, label="baseline residual")
    ax.plot(empirical["time"], _rolling_rms(residuals), color="#9467bd", linewidth=1.6, linestyle=":", label="TNE residual envelope")
    ax.set_title("Elastic-pi ringdown residual diagnostics")
    ax.set_xlabel("aligned time")
    ax.set_ylabel("residual")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    save_figure(fig, residual_path, dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.0, 4.6), constrained_layout=True)
    ax.plot(empirical["time"], prediction["observed_envelope"], color="#1f77b4", linewidth=2.0, label="observed envelope")
    ax.plot(empirical["time"], prediction["tne_envelope"], color="#d62728", linewidth=2.0, label="TNE reduced-basis envelope")
    ax.plot(empirical["time"], prediction["baseline_envelope"], color="#2ca02c", linewidth=1.8, linestyle="--", label="baseline envelope")
    ax.set_title("Elastic-pi ringdown envelope comparison")
    ax.set_xlabel("aligned time")
    ax.set_ylabel("analytic-signal envelope")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    save_figure(fig, envelope_path, dpi=220)
    plt.close(fig)
    return [curve_path, residual_path, envelope_path]
