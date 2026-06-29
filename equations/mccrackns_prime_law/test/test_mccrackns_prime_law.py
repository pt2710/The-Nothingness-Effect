"""
Author : B. McCrackn
Email  : thenothingnesseffect@gmail.com
Usage  : python test_mccrackns_prime_law.py

Unit tests for NumbersDomains and McCracknsPrimeLaw.
Covers motif encoding, gap logic, prime stream, and progress bar.
"""

import os
import sys
import time
import numpy as np
import pytest

def find_project_root(marker_file_or_folder="equations"):
    d = os.path.abspath(__file__)
    while True:
        d = os.path.dirname(d)
        if marker_file_or_folder in os.listdir(d):
            return d
        if d == os.path.dirname(d):
            break
    raise RuntimeError(f"Could not find project root with marker '{marker_file_or_folder}'.")

project_root = find_project_root()
sys.path.insert(0, project_root)

from equations.mccrackns_prime_law.mccrackns_prime_law import McCracknsPrimeLaw as mpl
from equations.numbers_domains.numbers_domains import NumbersDomains

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

# ---------------------------
# NumbersDomains tests
# ---------------------------

def test_NumbersDomains_U1():
    nd = NumbersDomains()
    assert nd.canonical_motif(1) == "U1"

def test_NumbersDomains_pow2_labels():
    nd = NumbersDomains()
    assert nd.canonical_motif(2) == "E1.0"
    assert nd.canonical_motif(4) == "E1.1"
    assert nd.canonical_motif(8) == "E1.2"

def test_NumbersDomains_examples():
    nd = NumbersDomains()
    assert nd.canonical_motif(1) == "U1"
    assert nd.canonical_motif(2) == "E1.0"
    assert nd.canonical_motif(4) == "E1.1"
    assert nd.canonical_motif(6) == "E2.0"
    assert nd.canonical_motif(8) == "E1.2"
    assert nd.canonical_motif(10) == "E2.1"
    assert nd.canonical_motif(12) == "E3.0"
    assert nd.canonical_motif(14) == "E2.2"
    assert nd.canonical_motif(16) == "E1.3"
    assert nd.canonical_motif(18) == "E2.3"
    assert nd.canonical_motif(20) == "E3.1"
    assert nd.canonical_motif(22) == "E2.4"
    assert nd.canonical_motif(24) == "E4.0"
    assert nd.canonical_motif(26) == "E2.5"
    assert nd.canonical_motif(28) == "E3.2"
    assert nd.canonical_motif(30) == "E2.6"

def test_NumbersDomains_cache():
    nd = NumbersDomains()
    v1 = nd.canonical_motif(10)
    v2 = nd.canonical_motif(10)
    assert v1 == v2
    assert 10 in nd._cache

def test_NumbersDomains_invalid():
    nd = NumbersDomains()
    try:
        nd.canonical_motif(5)
        assert False
    except ValueError:
        pass
    try:
        nd.canonical_motif(12)
        assert nd.canonical_motif(12) == "E3.0"
    except ValueError:
        assert False

def test_NumbersDomains_large():
    nd = NumbersDomains()
    assert nd.canonical_motif(2**12) == "E1.11"

# ---------------------------
# McCracknsPrimeLaw tests
# ---------------------------

def test_mpl_basic_api():
    pgen = mpl(n_primes=20)
    primes = pgen.generate()
    assert isinstance(primes, list)
    assert all(isinstance(p, int) for p in primes)
    assert primes[0] == 2 and primes[1] == 3

def test_mpl_stream_primes_yields():
    pgen = mpl(n_primes=20)
    out = list(pgen.stream_primes(start_idx=10))
    assert all(isinstance(row, tuple) and len(row) == 4 for row in out)
    idxs = [row[0] for row in out]
    assert idxs[0] == 10

def test_mpl_gaps_and_motifs():
    pgen = mpl(n_primes=30)
    pgen.generate() 
    primes = pgen.get_primes()
    gaps = pgen.get_gaps()
    motifs = pgen.get_motifs()
    assert len(primes) == 30
    assert len(gaps) == 29
    assert len(motifs) == 29

def test_mpl_stepwise_consistency():
    pgen = mpl(n_primes=15)
    results = []
    for _ in range(5):
        results.append(pgen.generate_one())
    idxs = [r[0] for r in results]
    assert sorted(idxs) == idxs

def test_mpl_large_batch_progress():
    n = 80
    pgen = mpl(n_primes=n, verbose=False)
    start_time = time.time()
    for i in range(1, n+1):
        pgen.generate_one()
        print_progress_bar(i, n, start_time)
    assert pgen.get_primes()[-1] > 0

if __name__ == "__main__":
    start_global = time.time()
    pytest.main(["-q", "--disable-warnings", "--maxfail=1"])
    print(f"\nProcess done. Total elapsed: {time.time() - start_global:.2f}s\n")
