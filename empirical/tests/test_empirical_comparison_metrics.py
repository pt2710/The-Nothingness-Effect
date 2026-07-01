from __future__ import annotations

import numpy as np

from empirical.metrics import metric_bundle


def test_metric_bundle_returns_finite_values_with_baseline():
    observed = np.array([1.0, 2.0, 3.0, 4.0], dtype=float)
    predicted = np.array([1.1, 1.9, 2.8, 4.2], dtype=float)
    baseline = np.array([0.9, 2.2, 3.3, 3.7], dtype=float)
    uncertainty = np.array([0.1, 0.1, 0.2, 0.2], dtype=float)

    metrics = metric_bundle(
        observed=observed,
        predicted=predicted,
        uncertainty=uncertainty,
        n_params=2,
        baseline=baseline,
        baseline_params=2,
    )

    assert metrics["RMSE"] > 0.0
    assert metrics["MAE"] > 0.0
    assert metrics["normalized_RMSE"] > 0.0
    assert np.isfinite(metrics["R2"])
    assert np.isfinite(metrics["chi_square"])
    assert np.isfinite(metrics["AIC"])
    assert np.isfinite(metrics["BIC"])
    assert np.isfinite(metrics["baseline_RMSE"])
    assert np.isfinite(metrics["baseline_AIC"])
    assert metrics["passed_validation"] is True
