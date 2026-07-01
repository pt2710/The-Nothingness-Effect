"""Reusable metrics for fixture-backed empirical comparisons."""

from __future__ import annotations

import math
from typing import Any

import numpy as np


def _aligned_arrays(
    observed: np.ndarray,
    predicted: np.ndarray,
    uncertainty: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    obs = np.asarray(observed, dtype=float)
    pred = np.asarray(predicted, dtype=float)
    if obs.shape != pred.shape:
        raise ValueError("observed and predicted arrays must have the same shape.")
    mask = np.isfinite(obs) & np.isfinite(pred)
    unc_out = None
    if uncertainty is not None:
        unc = np.asarray(uncertainty, dtype=float)
        mask &= np.isfinite(unc) & (unc > 0.0)
        unc_out = unc[mask]
    return obs[mask], pred[mask], unc_out


def rmse(observed: np.ndarray, predicted: np.ndarray) -> float:
    obs, pred, _ = _aligned_arrays(observed, predicted)
    return float(np.sqrt(np.mean((pred - obs) ** 2)))


def mae(observed: np.ndarray, predicted: np.ndarray) -> float:
    obs, pred, _ = _aligned_arrays(observed, predicted)
    return float(np.mean(np.abs(pred - obs)))


def normalized_rmse(observed: np.ndarray, predicted: np.ndarray) -> float:
    obs, pred, _ = _aligned_arrays(observed, predicted)
    span = float(np.ptp(obs))
    return float(np.sqrt(np.mean((pred - obs) ** 2)) / (span + 1e-12))


def r_squared(observed: np.ndarray, predicted: np.ndarray) -> float:
    obs, pred, _ = _aligned_arrays(observed, predicted)
    ss_tot = float(np.sum((obs - np.mean(obs)) ** 2))
    if ss_tot == 0.0:
        return float("nan")
    ss_res = float(np.sum((obs - pred) ** 2))
    return float(1.0 - ss_res / ss_tot)


def chi_square(observed: np.ndarray, predicted: np.ndarray, uncertainty: np.ndarray | None) -> float:
    if uncertainty is None:
        return float("nan")
    obs, pred, unc = _aligned_arrays(observed, predicted, uncertainty)
    if unc is None or len(unc) == 0:
        return float("nan")
    return float(np.sum(((pred - obs) / unc) ** 2))


def weighted_rmse(observed: np.ndarray, predicted: np.ndarray, uncertainty: np.ndarray | None) -> float:
    if uncertainty is None:
        return float("nan")
    obs, pred, unc = _aligned_arrays(observed, predicted, uncertainty)
    if unc is None or len(unc) == 0:
        return float("nan")
    return float(np.sqrt(np.mean(((pred - obs) / unc) ** 2)))


def residual_summary(observed: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    obs, pred, _ = _aligned_arrays(observed, predicted)
    residuals = pred - obs
    return {
        "residual_mean": float(np.mean(residuals)),
        "residual_std": float(np.std(residuals)),
    }


def aic_bic(observed: np.ndarray, predicted: np.ndarray, n_params: int) -> tuple[float, float]:
    obs, pred, _ = _aligned_arrays(observed, predicted)
    n = len(obs)
    if n == 0:
        return float("nan"), float("nan")
    rss = float(np.sum((pred - obs) ** 2)) + 1e-12
    aic = float(n * math.log(rss / n) + 2 * n_params)
    bic = float(n * math.log(rss / n) + n_params * math.log(n))
    return aic, bic


def metric_bundle(
    observed: np.ndarray,
    predicted: np.ndarray,
    uncertainty: np.ndarray | None = None,
    n_params: int = 1,
    baseline: np.ndarray | None = None,
    baseline_params: int = 1,
) -> dict[str, Any]:
    metrics = {
        "RMSE": rmse(observed, predicted),
        "MAE": mae(observed, predicted),
        "normalized_RMSE": normalized_rmse(observed, predicted),
        "R2": r_squared(observed, predicted),
        "chi_square": chi_square(observed, predicted, uncertainty),
        "weighted_RMSE": weighted_rmse(observed, predicted, uncertainty),
    }
    aic_value, bic_value = aic_bic(observed, predicted, n_params=n_params)
    metrics["AIC"] = aic_value
    metrics["BIC"] = bic_value
    metrics.update(residual_summary(observed, predicted))
    if baseline is not None:
        baseline_aic, baseline_bic = aic_bic(observed, baseline, n_params=baseline_params)
        metrics["baseline_RMSE"] = rmse(observed, baseline)
        metrics["baseline_MAE"] = mae(observed, baseline)
        metrics["baseline_R2"] = r_squared(observed, baseline)
        metrics["baseline_chi_square"] = chi_square(observed, baseline, uncertainty)
        metrics["baseline_weighted_RMSE"] = weighted_rmse(observed, baseline, uncertainty)
        metrics["baseline_AIC"] = baseline_aic
        metrics["baseline_BIC"] = baseline_bic
    numeric_values = [
        float(value)
        for value in metrics.values()
        if isinstance(value, (int, float, np.floating, np.integer))
    ]
    metrics["passed_validation"] = bool(all(np.isfinite(value) for value in numeric_values))
    return metrics
