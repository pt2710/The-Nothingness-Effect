"""
Author  : Budd McCrackn
Email   : thenothingnesseffect@gmail.com

McCracknsPrimeFlowpointLaw
--------------------------
Deterministic prime generation via regime–motif law and flowpoint operator.

Implements full mathematical regime–motif logic in line with The Nothingness Effect,
including regime expansion, motif algebra, and canonical flowpoint parity.

Usage:
    law = McCracknsPrimeFlowpointLaw(n_primes=1000)
    law.generate()
    law.export_all(script_dir)
"""

import sys
import os
import csv
import numpy as np
from equations.numbers_domains.numbers_domains import NumbersDomains
from equations.flowpoint.flowpoint import fp
from math import gcd

class McCracknsPrimeFlowpointLaw:
    """
    Deterministic, flowpoint- and regime–motif-driven prime generator.
    Implements full expansion and metadata per regime/motif algebra.
    """
    def __init__(self, n_primes: int = 1000):
        self.n_primes = int(n_primes)
        self.primes = []
        self.gaps = []
        self.motifs = []
        self.parities = []
        self.regimes = []
        self.domains = []
        self.nd = NumbersDomains()
        self._run_counter = {}
        self._motif_alphabet = ["U1", "E1.0"]
        self._used_motifs = set()
        self._primorial = 2 * 3
        self._regime_idx = 1
        self._regime_points = [1]
        self._parity_gen = fp(1)  # GLOBAL parity generator for the object's life
        self.alphabet_snapshots = [self._motif_alphabet.copy()]
    @staticmethod
    def _motif_gap(label):
        if label == "U1":
            return 1
        k, x = map(int, label[1:].split("."))
        if k == 1:
            return 1 << (x + 1)
        return (1 << (k - 1)) * (2 * x + 3)

    def _sort_alpha(self):
        self._motif_alphabet.sort(key=lambda lbl: (self._motif_gap(lbl),) + tuple(map(int, lbl[1:].split("."))) if lbl != "U1" else (0, 0))

    def _next_motif(self):
        g = self._motif_gap(self._motif_alphabet[-1]) + 2
        while True:
            lbl = self.nd.canonical_motif(g)
            if lbl != "U1" and lbl not in self._motif_alphabet:
                return lbl
            g += 2

    def _bump_regime(self):
        self.regimes.append(len(self.primes))
        self._motif_alphabet.append(self._next_motif())
        self._sort_alpha()
        self._regime_idx += 1
        if self._regime_idx == 1:
            pass
        else:
            self._motif_alphabet = [lbl for lbl in self._motif_alphabet if lbl != "U1"]
        self.alphabet_snapshots.append(self._motif_alphabet.copy())
        while len(self.primes) <= self._regime_idx:
            self._single_step(internal=True)
        self._primorial *= self.primes[self._regime_idx]
        self._used_motifs.clear()


    def _record(self, cand, gap, label, domain):
        parity = next(self._parity_gen)
        self.primes.append(cand)
        self.gaps.append(gap)
        run = self._run_counter.get(label, 0) + 1
        self._run_counter[label] = run
        self.motifs.append(label)
        self.parities.append(parity)
        self.domains.append(domain)
        self._used_motifs.add(label)
        if len(self._used_motifs) == len(self._motif_alphabet):
            self._bump_regime()

    def _single_step(self, internal=False):
        if len(self.primes) < 6:
            return
        while True:
            p_curr = self.primes[-1]
            P = self._primorial
            for lbl in self._motif_alphabet:
                gap = self._motif_gap(lbl)
                cand = p_curr + gap
                if gcd(cand, P) != 1:
                    continue
                while cand >= self.primes[self._regime_idx] ** 2:
                    self._bump_regime()
                    P = self._primorial
                    if gcd(cand, P) != 1:
                        break
                else:
                    domain = "U" if lbl == "U1" else "E"
                    self._record(cand, gap, lbl, domain)
                    return
            self._motif_alphabet.append(self._next_motif())
            self._sort_alpha()

    def generate(self):
        SEED_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
        SEED_GAPS   = [1, 2, 2, 4, 2, 4, 2, 4, 6, 2, 6, 4]
        SEED_MOTIFS = [
            "U1", "E1.0", "E1.0", "E1.1", "E1.0", "E1.1",
            "E1.0", "E1.1", "E2.0", "E1.0", "E2.0", "E1.1"
        ]
        SEED_PARITY = [1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1]
        SEED_DOMAINS = ["U"] + ["E"] * (len(SEED_PRIMES) - 1)
        SEED_REGIMES = [1, 6, 12]
        # Always reinitialize parity generator on generate call
        self._parity_gen = fp(1)
        if self.n_primes <= 13:
            self.primes = SEED_PRIMES[:self.n_primes]
            self.gaps = SEED_GAPS[:self.n_primes - 1]
            self.motifs = SEED_MOTIFS[:self.n_primes - 1]
            self.parities = SEED_PARITY[:self.n_primes - 1]
            self.domains = SEED_DOMAINS[:self.n_primes - 1]
            self.regimes = [r for r in SEED_REGIMES if r <= self.n_primes]
            return
        # Seeds
        seed_primes = [2, 3, 5, 7, 11, 13]
        self.primes = seed_primes[:]
        self.gaps   = [1, 2, 2, 4, 2]
        self.motifs = ["U1", "E1.0", "E1.0", "E1.1", "E1.0"]
        self.parities = [next(self._parity_gen) for _ in self.primes]
        self.domains = ["U", "E", "E", "E", "E", "E"]
        self.regimes = [1]
        self._run_counter = {"U1": 1, "E1.0": 2, "E1.1": 1}
        self._used_motifs = set(self._motif_alphabet)
        self._regime_idx = 1
        self._primorial = 2 * 3
        self._sort_alpha()
        if len(self.primes) >= 6:
            self._bump_regime()
        while len(self.primes) < self.n_primes:
            self._single_step()
        self.primes = self.primes[:self.n_primes]
        self.gaps = self.gaps[:self.n_primes - 1]
        self.motifs = self.motifs[:self.n_primes - 1]
        self.parities = self.parities[:self.n_primes - 1]
        self.domains = self.domains[:self.n_primes - 1]

    def export_all(self, script_dir):
        data_dir = os.path.join(script_dir, "data_results")
        os.makedirs(data_dir, exist_ok=True)
        csv_path = os.path.join(data_dir, "prime_flowpoint_table.csv")
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["index", "prime", "gap", "motif", "parity", "regime", "domain"])
            for i in range(self.n_primes):
                prime = self.primes[i]
                gap = self.gaps[i - 1] if i > 0 else ""
                motif = self.motifs[i - 1] if i > 0 else "U1"
                parity = self.parities[i - 1] if i > 0 else 1
                regime = 1 if (i + 1) in self.regimes else 0
                domain = self.domains[i - 1] if i > 0 else "U"
                writer.writerow([i + 1, prime, gap, motif, parity, regime, domain])

    def export_all_feather(self, script_dir):
        import pandas as pd
        data_dir = os.path.join(script_dir, "data_results")
        os.makedirs(data_dir, exist_ok=True)
        df = pd.DataFrame({
            "index": np.arange(1, self.n_primes + 1),
            "prime": self.primes,
            "gap": [np.nan] + self.gaps,
            "motif": ["U1"] + self.motifs,
            "parity": [1] + self.parities,
            "regime": [1 if (i + 1) in self.regimes else 0 for i in range(self.n_primes)],
            "domain": ["U"] + self.domains
        })
        df.to_feather(os.path.join(data_dir, "prime_flowpoint_table.feather"))
    
    def get_parent_motif(self, *, level: int, child: str) -> str:
        """
        Return the motif from the previous regime's alphabet that generated 'child'.
        """
        if child == "U1":
            if level == 0:
                return None  # No parent, root only
            else:
                raise ValueError("U1 should only be present at root (level 0)")
        prev_alpha = self.alphabet_snapshots[level-1]
        for parent in prev_alpha:
            # same motif expansion logic as used for building the tree
            if parent == "U1":
                children = ["E1.0", "E1.1"]
            else:
                k, x = map(int, parent[1:].split("."))
                children = [f"E{k}.{x+1}", f"E{k+1}.0"]
            if child in children:
                return parent
        raise ValueError(f"Could not find parent for motif {child} at level {level}")
