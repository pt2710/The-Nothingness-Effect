#!/usr/bin/env python3
"""
Author  : B. McCrackn
Email   : thenothingnesseffect@gmail.com
Usage   : from mccrackns_prime_law import McCracknsPrimeLaw

McCrackn’s Prime Law — Deterministic, recursive prime generator based on motif algebra.

Implements a deterministic, regime-based prime-generation algorithm via motif expansion
with no trial division, sieving, or primality tests. Primes are produced by canonical
motif-gap encoding and regime expansion; all metadata (gap, motif, regime) is tracked.

Dependencies:
    - numbers_domains.py providing NumbersDomains.canonical_motif(gap: int) -> str
"""
from equations.numbers_domains.numbers_domains import NumbersDomains

from math import gcd


class McCracknsPrimeLaw:
    """
    Deterministic prime generator using regime-motif logic.

    Args:
        n_primes (int): Number of primes to generate.
        verbose (bool): If True, print progress.
        progress_every (int): Progress print frequency.
    """

    def __init__(self, *, n_primes: int = 100, verbose: bool = False, progress_every: int = 1000):
        # Generator configuration
        self.n_primes       = max(2, n_primes)
        self.verbose        = verbose
        self.progress_every = max(1, progress_every)

        # Seeds: primes, gaps, and motifs
        seed_primes = [2, 3, 5, 7, 11, 13]
        self.primes = seed_primes[:self.n_primes]
        seed_gaps   = [1, 2, 2, 4, 2]
        seed_labels = ["U1", "E1.0", "E1.0", "E1.1", "E1.0"]

        self.gaps   = seed_gaps[:len(self.primes) - 1]
        self.motifs = [("U1", 1)]
        self._run_counter = {"U1": 1, "E1.0": 0, "E1.1": 0}
        for lbl in seed_labels[:len(self.primes) - 1]:
            run = self._run_counter.get(lbl, 0) + 1
            self._run_counter[lbl] = run
            self.motifs.append((lbl, run))

        self.domains        = NumbersDomains()
        self.regime_idx     = 1
        self.primorial      = 2 * 3
        self.alphabet       = ["U1", "E1.0"]
        self._sort_alpha()
        self.used_motifs    = set(self.alphabet)
        self.regime_points  = []

        if len(self.primes) >= 6:
            self._bump_regime()

    @staticmethod
    def _gap(label: str) -> int:
        """
        Decode motif label to integer gap.

        Args:
            label (str): Motif label ("U1", "E1.0", etc.)
        Returns:
            int: Numeric gap.
        """
        if label == "U1":
            return 1
        k, x = map(int, label[1:].split("."))
        if k == 1:
            return 1 << (x + 1)
        return (1 << (k - 1)) * (2 * x + 3)

    def _sort_alpha(self):
        """Sort alphabet by motif gap and specificity."""
        self.alphabet.sort(key=lambda lbl: (self._gap(lbl),) + tuple(map(int, lbl[1:].split("."))))

    def _next_motif(self) -> str:
        """
        Compute next unused motif by increasing gap.

        Returns:
            str: New motif label.
        """
        g = self._gap(self.alphabet[-1]) + 2
        while True:
            lbl = self.domains.canonical_motif(g)
            if lbl != "U1" and lbl not in self.alphabet:
                return lbl
            g += 2

    def _bump_regime(self):
        """
        Expand regime by adding motif, updating primorial.
        """
        self.regime_points.append(len(self.primes))
        self.alphabet.append(self._next_motif())
        self._sort_alpha()
        self.regime_idx += 1
        while len(self.primes) <= self.regime_idx:
            self._single_step(internal=True)
        self.primorial *= self.primes[self.regime_idx]
        self.used_motifs.clear()

    def _record(self, cand: int, gap: int, label: str):
        """
        Register candidate as next prime.

        Args:
            cand (int): Prime candidate.
            gap (int): Gap size.
            label (str): Motif label.
        """
        self.primes.append(cand)
        self.gaps.append(gap)
        run = self._run_counter.get(label, 0) + 1
        self._run_counter[label] = run
        self.motifs.append((label, run))
        self.used_motifs.add(label)
        if len(self.used_motifs) == len(self.alphabet):
            self._bump_regime()

    def _single_step(self, *, internal: bool = False):
        """
        Attempt next prime via active motifs.
        If no candidate found, extend motif alphabet.

        Args:
            internal (bool): Internal step (suppresses progress).
        """
        if len(self.primes) < 6:
            return
        while True:
            p_curr = self.primes[-1]
            P      = self.primorial
            for lbl in self.alphabet:
                gap  = self._gap(lbl)
                cand = p_curr + gap
                if gcd(cand, P) != 1:
                    continue
                while cand >= self.primes[self.regime_idx] ** 2:
                    self._bump_regime()
                    P = self.primorial
                    if gcd(cand, P) != 1:
                        break
                else:
                    self._record(cand, gap, lbl)
                    if self.verbose and not internal and len(self.primes) % self.progress_every == 0:
                        print(f"[prime {len(self.primes):>9}] {cand}")
                    return
            self.alphabet.append(self._next_motif())
            self._sort_alpha()

    def generate(self):
        """
        Generate all primes up to `n_primes`.

        Returns:
            list[int]: Generated primes.
        """
        while len(self.primes) < self.n_primes:
            self._single_step()
        return self.primes

    def generate_one(self):
        """
        Generate the next prime.

        Returns:
            tuple[int, int, int, str]: (index, prime, gap, motif)
        """
        if len(self.primes) < self.n_primes:
            self._single_step()
        idx   = len(self.primes)
        p     = self.primes[-1]
        gap   = 0 if idx == 1 else self.gaps[-1]
        motif = "U1" if idx == 1 else self.motifs[-1][0]
        return idx, p, gap, motif

    def stream_primes(self, *, start_idx=1):
        """
        Generator yielding (index, prime, gap, motif).

        Yields:
            tuple[int, int, int, str]: (index, prime, gap, motif)
        """
        while len(self.primes) < self.n_primes:
            self._single_step()
            idx = len(self.primes)
            if idx >= start_idx:
                p     = self.primes[-1]
                gap   = 0 if idx == 1 else self.gaps[-1]
                motif = "U1" if idx == 1 else self.motifs[-1][0]
                yield idx, p, gap, motif

    def get_primes(self):
        """Return copy of generated primes."""
        return self.primes.copy()

    def get_gaps(self):
        """Return copy of prime gaps."""
        return self.gaps.copy()

    def get_motifs(self):
        """Return copy of motif sequence (excluding seed)."""
        return self.motifs[1:].copy()

