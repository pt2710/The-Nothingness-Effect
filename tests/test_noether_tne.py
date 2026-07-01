from pathlib import Path

import numpy as np

from equations.noether_tne import (
    NoetherParams,
    divergence_2d,
    fp_gauss_residual,
    fp_phase,
    gradient_2d,
    noether_validation_metrics,
    simulate_fp_gauss_identity,
    simulate_kd_flux_under_phase_shift,
)
from simulations.run_noether_figures48_49 import run


def test_fp_phase_shift_shape():
    theta = np.arange(5.0)
    assert fp_phase(theta, 0.5).shape == theta.shape


def test_kd_flux_stability_under_global_phase():
    result = simulate_kd_flux_under_phase_shift(NoetherParams(n_phase=64, time_steps=20))
    assert result["metrics"]["rx_max_deviation"] < 1e-8


def test_gradient_divergence_shapes():
    field = np.ones((8, 8))
    grad_x, grad_y = gradient_2d(field, 1.0, 1.0)
    div = divergence_2d(grad_x, grad_y, 1.0, 1.0)
    assert grad_x.shape == field.shape
    assert grad_y.shape == field.shape
    assert div.shape == field.shape


def test_fp_gauss_residual_finite():
    theta = np.ones((8, 8))
    residual = fp_gauss_residual(theta, np.ones_like(theta), 1.0, 1.0)
    assert np.all(np.isfinite(residual))


def test_fp_gauss_identity_below_tolerance_for_constructed_case():
    result = simulate_fp_gauss_identity(grid_size=128)
    assert result["metrics"]["gauss_residual_inf_norm"] < 1e-6


def test_table19_metrics_pass():
    flux = simulate_kd_flux_under_phase_shift(NoetherParams(n_phase=64, time_steps=20))
    gauss = simulate_fp_gauss_identity(grid_size=64)
    rows = noether_validation_metrics(flux["metrics"], gauss["metrics"])
    assert all(row["passed"] for row in rows)


def test_figures48_49_outputs_exist_after_runner(tmp_path: Path):
    result = run(tmp_path, quick=True)
    assert result["figure48"].exists()
    assert result["figure49"].exists()
    assert result["metrics"].exists()
    assert result["metadata"].exists()
