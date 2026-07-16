#!/usr/bin/env python3
"""
Author: B. McCrackn
Email : thenothingnesseffect@gmail.com
Usage : python test_elastic_pi.py

Unit tests for the ElasticPi class. Covers API, math, and DFI integration.
Includes process monitoring and a dynamic progress bar.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
import pytest


from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.dfi import DynamicFluctuationIndex
from the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.elastic_pi import ElasticPi

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
        print()

def test_default_init_and_api():
    epi = ElasticPi()
    assert isinstance(epi, ElasticPi)
    assert np.isclose(epi.K_D, 1.0)   # <-- Rettet fra np.pi til 1.0

def test_build_S_analytic_zero():
    x = np.linspace(0, 10, 50)
    epi = ElasticPi()
    S = epi.build_S_analytic(x)
    assert S.shape == x.shape
    assert np.allclose(S, 0.0)

def test_build_S_analytic_formula():
    x = np.linspace(0, 4, 10)
    def cubic(x, a=1): return a * x ** 3
    epi = ElasticPi()
    S = epi.build_S_analytic(x, formula=cubic, a=2)
    assert np.allclose(S, 2 * x ** 3)

def test_compute_piE_and_laplacian_basic():
    S = np.zeros(20)
    epi = ElasticPi()
    x, piE, lap = epi.compute_piE_and_laplacian(S)
    assert np.allclose(piE, np.pi)
    assert np.allclose(lap[1:-1], 0.0)
    assert x.shape == S.shape
    assert piE.shape == S.shape
    assert lap.shape == S.shape

def test_KD_override_and_math():
    S = np.linspace(-2, 2, 30)
    epi = ElasticPi()
    _, piE1, _ = epi.compute_piE_and_laplacian(S)
    _, piE2, _ = epi.compute_piE_and_laplacian(S, K_D=2.0)
    assert not np.allclose(piE1, piE2)
    assert np.all(np.isfinite(piE2))

def test_empirical_from_dfi_mean_vs_feature():
    df = pd.DataFrame(np.random.rand(40, 4), columns=list("ABCD"))
    dfi_engine = DynamicFluctuationIndex()
    epi = ElasticPi()
    S_mean = epi.empirical_from_dfi(df, dfi_engine)
    S_A = epi.empirical_from_dfi(df, dfi_engine, feature="A")
    assert S_mean.shape == S_A.shape
    assert np.all(np.isfinite(S_mean))
    assert np.all(np.isfinite(S_A))

def test_integration_progress():
    # Run a synthetic computation with progress bar
    n = 30
    x = np.linspace(0, 10, n)
    start_time = time.time()
    epi = ElasticPi()
    for i in range(1, n + 1):
        S = epi.build_S_analytic(x[:i])
        _, piE, lap = epi.compute_piE_and_laplacian(S)
        assert piE.shape == (i,)
        print_progress_bar(i, n, start_time)

if __name__ == "__main__":
    start_global = time.time()
    # Show all warnings!
    pytest.main(["-q", "--maxfail=1"])
    print(f"\nProcess done. Total elapsed: {time.time() - start_global:.2f}s\n")
