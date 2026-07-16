#!/usr/bin/env python3
"""
Author: B. McCrackn
Email : thenothingnesseffect@gmail.com
Usage : python test_dfi.py

Unit tests for the DynamicFluctuationIndex class.
Includes process monitoring with elapsed time, estimated time left, and a dynamic terminal progress bar.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
import pytest

# --- Robust project root detection: adjust marker as needed

from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.dfi import DynamicFluctuationIndex

def print_progress_bar(iteration, total, start_time, bar_length=40):
    percent = iteration / total
    elapsed = time.time() - start_time
    est_total = elapsed / percent if percent > 0 else 0
    time_left = est_total - elapsed if percent > 0 else 0
    bar_fill = int(bar_length * percent)
    bar = '#' * bar_fill + '-' * (bar_length - bar_fill)
    sys.stdout.write(
        f'\r[{"{:>6.1f}%".format(percent*100)}] |{bar}| '
        f'Elapsed: {elapsed:6.2f}s | Left: {time_left:6.2f}s'
    )
    sys.stdout.flush()
    if iteration == total:
        print()  # Newline at end

def generate_spatial_temperatures(n_steps=100, n_locations=5, noise_scale=0.5, show_progress=False):
    """
    Simulate a 1D chain of n_locations with nearest-neighbor heat diffusion and small noise.
    Returns
    -------
    temps : np.ndarray
        Shape (n_steps, n_locations)
    """
    temps = np.zeros((n_steps, n_locations), dtype=float)
    temps[0] = np.linspace(10, 20, n_locations) + np.random.randn(n_locations) * noise_scale
    start_time = time.time()
    for t in range(1, n_steps):
        prev = temps[t - 1]
        new = prev.copy()
        for i in range(n_locations):
            if i == 0:
                new[i] = (prev[i] + prev[i + 1]) / 2
            elif i == n_locations - 1:
                new[i] = (prev[i] + prev[i - 1]) / 2
            else:
                new[i] = (prev[i - 1] + prev[i] + prev[i + 1]) / 3
        temps[t] = new + np.random.randn(n_locations) * noise_scale
        if show_progress:
            print_progress_bar(t, n_steps - 1, start_time)
    if show_progress:
        print_progress_bar(n_steps - 1, n_steps - 1, start_time)
    return temps

def test_uniform_data_zero_entropy():
    df = pd.DataFrame(np.full((50, 4), fill_value=5.0), columns=list("ABCD"))
    engine = DynamicFluctuationIndex()
    ent = engine.dfi(df)
    assert set(ent.keys()) == set(df.columns)
    for col, metrics in ent.items():
        S = metrics["Relative_Entropy"]
        assert S.shape == (50,)
        assert np.allclose(S, 0.0, atol=1e-12)

def test_spatially_correlated_data_smoke():
    n_steps, n_locations = 80, 5
    data = generate_spatial_temperatures(n_steps=n_steps, n_locations=n_locations, show_progress=True)
    df = pd.DataFrame(data, columns=[f"loc{i}" for i in range(n_locations)])
    engine = DynamicFluctuationIndex()
    start = time.time()
    ent = engine.dfi(df)
    print_progress_bar(n_steps, n_steps, start)  # Show as "done"
    assert set(ent.keys()) == set(df.columns)
    for col, metrics in ent.items():
        for key in ("Relative_Entropy", "Entropic_Weight", "Relative_Volume"):
            arr = metrics[key]
            assert isinstance(arr, np.ndarray)
            assert arr.shape == (n_steps,)
            assert np.all(np.isfinite(arr))

def test_override_soi_changes_V0():
    df = pd.DataFrame(np.full((10, 3), fill_value=2.0))
    soi_manual = 300.0
    engine = DynamicFluctuationIndex()
    start = time.time()
    ent = engine.dfi(df, soi=soi_manual)
    print_progress_bar(1, 1, start)
    xn = df.shape[1]
    expected_V0 = soi_manual / xn
    for metrics in ent.values():
        Vx = metrics["Relative_Volume"]
        assert np.allclose(Vx, expected_V0, atol=1e-12)

def test_cli_help_runs(capsys):
    import subprocess
    start = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.dfi", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    print_progress_bar(1, 1, start)
    assert result.returncode == 0
    assert "Compute Dynamic Fluctuation Index on a dataset" in result.stdout

if __name__ == "__main__":
    start_global = time.time()
    pytest.main(["-q", "--disable-warnings", "--maxfail=1"])
    print(f"\nProcess done. Total elapsed: {time.time() - start_global:.2f}s\n")
