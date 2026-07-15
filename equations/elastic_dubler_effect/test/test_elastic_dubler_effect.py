from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest

from tne_runtime.artifacts.io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz
from equations.elastic_dubler_effect.elastic_dubler_effect import (
    compute_dubler_grid,
    dubler_frequency_ratio,
    dubler_shift,
)
from equations.elastic_pi.elastic_pi import ElasticPiEvaluationError
from tne_runtime.theorem_complex_runtime.types import NonFiniteValueError


SCRIPT_DIR = Path(__file__).resolve().parent


def _write_test_artifacts() -> dict[str, Path]:
    delta_s = np.linspace(-2.0, 2.0, 41)
    grid = compute_dubler_grid(delta_s, np.array([1.0, 2.0]))
    fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)
    for kd, shift in zip(grid["K_D"], grid["dubler_shift"]):
        ax.plot(delta_s, shift, label=f"K_D={kd:g}")
    ax.set_title("Elastic Dubler-effect test visualization")
    ax.set_xlabel("delta S")
    ax.set_ylabel("shift")
    ax.grid(True, alpha=0.25)
    ax.legend()
    figure = SCRIPT_DIR / "elastic_dubler_effect_test_visualization.png"
    data = SCRIPT_DIR / "elastic_dubler_effect_test_data.npz"
    results = SCRIPT_DIR / "elastic_dubler_effect_test_results.csv"
    save_figure(fig, figure)
    plt.close(fig)
    save_npz(data, **grid)
    save_csv(
        results,
        [
            {
                "ratio_at_zero": float(dubler_frequency_ratio(0.0, 1.0)),
                "finite": bool(np.all(np.isfinite(grid["dubler_shift"]))),
                "claim_boundary": CLAIM_BOUNDARY,
            }
        ],
    )
    return {"figure": figure, "data": data, "results": results}


def test_ratio_identity_at_zero_gradient():
    assert np.isclose(dubler_frequency_ratio(0.0, 1.0), 1.0)


def test_ratio_monotone_decreasing_for_positive_delta_s():
    delta_s = np.linspace(0.0, 5.0, 40)
    ratio = dubler_frequency_ratio(delta_s, 1.0)
    assert np.all(np.diff(ratio) <= 0.0)


def test_larger_kd_reduces_shift_strength():
    assert abs(dubler_shift(2.0, 5.0)) < abs(dubler_shift(2.0, 0.5))


def test_invalid_kd_raises():
    with pytest.raises(ValueError):
        dubler_frequency_ratio(1.0, 0.0)


def test_nonfinite_input_is_not_masked():
    with pytest.raises(NonFiniteValueError):
        dubler_frequency_ratio(np.nan, 1.0)


def test_vector_underflow_is_not_clipped_to_a_finite_proxy():
    with pytest.raises(ElasticPiEvaluationError):
        dubler_frequency_ratio(np.array([1000.0, 2000.0]), np.array([1.0, 1.0]))


def test_test_script_outputs_are_generated_locally():
    paths = _write_test_artifacts()
    for path in paths.values():
        assert path.exists()
        assert path.stat().st_size > 0
