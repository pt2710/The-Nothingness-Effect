from pathlib import Path

import numpy as np
import pytest

from equations.dubler_effect import dubler_frequency_ratio, dubler_shift
from simulations.run_dubler_effect_figure31 import run


def test_ratio_identity_at_zero_gradient():
    assert np.isclose(dubler_frequency_ratio(0.0, 1.0), 1.0)


def test_ratio_monotone_decreasing_for_positive_delta_s():
    delta_s = np.linspace(0.0, 5.0, 40)
    ratio = dubler_frequency_ratio(delta_s, 1.0)
    assert np.all(np.diff(ratio) <= 0.0)


def test_larger_kd_reduces_shift_strength():
    delta_s = 2.0
    assert abs(dubler_shift(delta_s, 5.0)) < abs(dubler_shift(delta_s, 0.5))


def test_invalid_kd_raises():
    with pytest.raises(ValueError):
        dubler_frequency_ratio(1.0, 0.0)


def test_figure31_outputs_exist_after_runner(tmp_path: Path):
    result = run(tmp_path, quick=True)
    for key in ("figure", "data", "metrics", "metadata"):
        assert result[key].exists()
