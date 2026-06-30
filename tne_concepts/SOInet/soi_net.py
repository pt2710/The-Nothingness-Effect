import os
import math
import random
import sys
from copy import deepcopy
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

SOINET_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SOINET_DIR))

for module_name in (
    "flowpoint",
    "dfi",
    "elastic_pi",
    "soi",
    "countable_infinity",
    "uncountable_infinity",
    "symmetry",
    "duality",
    "spatiality",
):
    module = sys.modules.get(module_name)
    module_file = Path(getattr(module, "__file__", "")).resolve() if module else None
    if module_file and SOINET_DIR not in module_file.parents:
        del sys.modules[module_name]

from flowpoint import Flowpoint
from dfi import DFI
from elastic_pi import ElasticPi
from soi import SpectrumOfInfinities

class SOInet:
    def __init__(self, N=200, seeds=(10, 20, 30), shell_gap=3.0, K_D=np.pi, soi_params=None, mode='classifier'):
        self.N = N
        self.seeds = seeds
        self.shell_gap = shell_gap
        self.K_D = K_D
        self.fp = Flowpoint(1)
        self.dfi = DFI()
        self.elastic_pi = ElasticPi(K_D=K_D)
        self.soi = SpectrumOfInfinities(**(soi_params or {}))
        self.histories = []
        self.mode = mode

    def _soi_growth_params(self):
        if hasattr(self.soi, 'adv_mode') and self.soi.adv_mode and getattr(self.soi, 'type', None) == 'symmetric':
            soi_tuple = self.soi.get_value(self.N)
            soi_val = abs(soi_tuple[0])
            symmetry = 'symmetric'
        else:
            soi_val = self.soi.get_value(self.N)
            symmetry = None
        return soi_val, symmetry

    def build_pgqenn_with_history(self, seed):
        random.seed(seed)
        primes       = [2]
        edges        = defaultdict(set)
        edge_weights = defaultdict(dict)
        k_depth      = {2: 0}
        edges[2]     = set()

        all_primes, all_edges, all_coords = [], [], []

        def compute_coords(k_depth, soi_val=1.0, symmetry=None, required_primes=None):
            shell_nodes = defaultdict(list)
            for p, k in k_depth.items():
                shell_nodes[k].append(p)
            coords = {}
            φg = (1 + 5**0.5) / 2
            for k, nodes in shell_nodes.items():
                n_shell = len(nodes)
                for idx, p in enumerate(nodes):
                    φ = math.acos(1 - 2*(idx+0.5)/n_shell)
                    θ = 2 * math.pi * (idx / φg)
                    r = (k+1) * self.shell_gap * soi_val
                    if symmetry == 'symmetric':
                        direction = 1 if (k % 2 == 0) else -1
                        coords[p] = (
                            direction * r*math.sin(φ)*math.cos(θ),
                            direction * r*math.sin(φ)*math.sin(θ),
                            direction * r*math.cos(φ)
                        )
                    else:
                        coords[p] = (
                            r*math.sin(φ)*math.cos(θ),
                            r*math.sin(φ)*math.sin(θ),
                            r*math.cos(φ)
                        )
            # Ensure all primes have a coordinate (fallback to origin)
            if required_primes is not None:
                for p in required_primes:
                    if p not in coords:
                        coords[p] = (0., 0., 0.)
            return coords

        soi_val, symmetry = self._soi_growth_params()

        all_primes.append(primes.copy())
        all_edges.append(deepcopy(edges))
        all_coords.append(compute_coords(k_depth, soi_val=soi_val, symmetry=symmetry, required_primes=primes.copy()))

        cand = 3
        while len(primes) < self.N:
            limit = int(math.sqrt(cand)) + 1
            is_prime = all(cand % p != 0 for p in primes if p <= limit)
            if not is_prime:
                cand += 2
                continue

            primes.append(cand)
            gap = cand - primes[-2]
            k = 0
            gtmp = gap
            while gtmp % 2 == 0:
                gtmp //= 2; k += 1
            k_depth[cand] = k

            width = min(2**k, len(edges))
            targets = random.sample(list(edges.keys()), width)
            for t in targets:
                edges[cand].add(t)
                edges[t].add(cand)
                w = next(self.fp)
                edge_weights[cand][t] = w
                edge_weights[t][cand] = w

            # Always align coords with primes, edges, weight_map
            current_primes = primes.copy()
            all_primes.append(current_primes)
            all_edges.append(deepcopy(edges))
            all_coords.append(compute_coords(k_depth, soi_val=soi_val, symmetry=symmetry, required_primes=current_primes))

            cand += 2

        final_shells = defaultdict(list)
        for p, k in k_depth.items():
            final_shells[k].append(p)

        return primes, edges, all_coords, all_edges, all_primes, edge_weights, final_shells

    def run(self):
        self.histories = [
            self.build_pgqenn_with_history(seed)
            for seed in self.seeds
        ]
        L, N = 10, 100
        elastic_fp = Flowpoint(1)
        S = self.elastic_pi.build_S_analytic(L, N, num_primes=50, fp_gen=elastic_fp)
        x, piE, lap = self.elastic_pi.compute_piE_and_laplacian(L, N, S)
        edge_weights_matrix = []
        for _, _, _, _, _, weight_map, _ in self.histories:
            net_w = []
            for u in weight_map:
                net_w.extend(list(weight_map[u].values()))
            edge_weights_matrix.append(net_w)
        edge_weights_arr = np.vstack([np.array(w).reshape(-1, 1) for w in edge_weights_matrix])
        dfi_result = self.dfi.compute_entropical_data(edge_weights_arr, soi=self.soi)
        return {
            "histories": self.histories,
            "elastic_pi": {"x": x, "S": S, "piE": piE, "lap": lap},
            "dfi": dfi_result
        }

    @staticmethod
    def encode_audio(audio, n_fft=None):
        spectrum = np.fft.rfft(audio, n=n_fft)
        return spectrum

    @staticmethod
    def decode_audio(spectrum, n_samples=None):
        audio = np.fft.irfft(spectrum, n=n_samples)
        return audio
