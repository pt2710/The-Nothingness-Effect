from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from the_nothingness_effect._runtime.artifacts.io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz
from the_nothingness_effect.the_completeness_theorem.noether_structure.noether_tne import (
    NoetherParams,
    divergence_2d,
    fp_gauss_residual,
    fp_phase,
    gradient_2d,
    noether_validation_metrics,
    simulate_fp_gauss_identity,
    simulate_kd_flux_under_phase_shift,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def _write_test_artifacts() -> dict[str, Path]:
    flux = simulate_kd_flux_under_phase_shift(NoetherParams(n_phase=64, time_steps=24))
    gauss = simulate_fp_gauss_identity(grid_size=64)
    rows = noether_validation_metrics(flux["metrics"], gauss["metrics"])
    fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)
    ax.plot(flux["time"], flux["rx"], label="Rx(t)")
    ax.axhline(flux["rx"][0], linestyle="--", color="black", label="Rx(0)")
    ax.set_title("Noether TNE test visualization")
    ax.set_xlabel("time")
    ax.set_ylabel("Rx")
    ax.grid(True, alpha=0.25)
    ax.legend()
    figure = SCRIPT_DIR / "artifacts" / "noether_tne_test_visualization.png"
    data = SCRIPT_DIR / "artifacts" / "noether_tne_test_data.npz"
    results = SCRIPT_DIR / "artifacts" / "noether_tne_test_results.csv"
    save_figure(fig, figure)
    plt.close(fig)
    save_npz(data, time=flux["time"], rx=flux["rx"], residual=gauss["residual"])
    save_csv(results, [{**row, "claim_boundary": CLAIM_BOUNDARY} for row in rows])
    return {"figure": figure, "data": data, "results": results}


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


def test_test_script_outputs_are_generated_locally():
    paths = _write_test_artifacts()
    for path in paths.values():
        assert path.exists()
        assert path.stat().st_size > 0
