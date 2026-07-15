"""Deterministic prime/parity growth and explicit stochastic ablation."""

from __future__ import annotations

from dataclasses import dataclass
import random

import torch


@dataclass(frozen=True, order=True)
class TwoAdicDepth:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or self.value < 0:
            raise ValueError("2-adic depth must be a non-negative integer")


@dataclass(frozen=True)
class PrimeGraph:
    primes: tuple[int, ...]
    two_adic_depths: tuple[TwoAdicDepth, ...]
    adjacency: torch.Tensor
    growth_mode: str

    def __post_init__(self) -> None:
        node_count = len(self.primes)
        if node_count < 2 or len(self.two_adic_depths) != node_count:
            raise ValueError("prime graph requires aligned primes and 2-adic depths")
        if self.adjacency.shape != (node_count, node_count):
            raise ValueError("prime graph adjacency has the wrong shape")
        if not bool(torch.isfinite(self.adjacency).all()):
            raise ValueError("prime graph adjacency contains NaN or infinity")
        if not torch.allclose(self.adjacency, self.adjacency.T):
            raise ValueError("prime graph adjacency must be symmetric")
        if not bool((torch.diagonal(self.adjacency) == 0).all()):
            raise ValueError("prime graph adjacency cannot contain self loops")


def two_adic_depth(value: int) -> TwoAdicDepth:
    if not isinstance(value, int) or value <= 0:
        raise ValueError("2-adic valuation requires a strictly positive integer")
    depth = 0
    while value % 2 == 0:
        value //= 2
        depth += 1
    return TwoAdicDepth(depth)


def first_primes(count: int) -> tuple[int, ...]:
    if not isinstance(count, int) or count < 2:
        raise ValueError("prime growth requires at least two nodes")
    primes: list[int] = []
    candidate = 2
    while len(primes) < count:
        if all(candidate % prime for prime in primes if prime * prime <= candidate):
            primes.append(candidate)
        candidate += 1
    return tuple(primes)


class CanonicalPrimeGrowth:
    """Prime-gap and 2-adic-parity growth with no stochastic choices."""

    def __init__(self, motif_width: int = 2):
        if motif_width < 1:
            raise ValueError("motif width must be positive")
        self.motif_width = int(motif_width)

    def build(self, node_count: int, *, dtype: torch.dtype = torch.float32) -> PrimeGraph:
        primes = first_primes(node_count)
        depths = tuple(two_adic_depth(prime - 1) for prime in primes)
        adjacency = torch.zeros((node_count, node_count), dtype=dtype)
        for index in range(1, node_count):
            candidates = list(range(index))
            candidates.sort(key=lambda other: (
                abs(depths[index].value - depths[other].value),
                abs((primes[index] - primes[other]) % 4 - 2),
                primes[index] - primes[other],
            ))
            targets = {index - 1, *candidates[: self.motif_width]}
            for target in targets:
                depth_distance = abs(depths[index].value - depths[target].value)
                parity_phase = 1.0 if (index - target) % 2 == 0 else 0.5
                weight = parity_phase / (1.0 + depth_distance)
                adjacency[index, target] = weight
                adjacency[target, index] = weight
        return PrimeGraph(primes, depths, adjacency, "canonical_prime_parity")


def stochastic_comparison_graph(node_count: int, *, seed: int = 0, width: int = 2) -> PrimeGraph:
    """Legacy-style random sampling retained only as a named ablation mode."""

    primes = first_primes(node_count)
    depths = tuple(two_adic_depth(prime - 1) for prime in primes)
    adjacency = torch.zeros((node_count, node_count), dtype=torch.float32)
    generator = random.Random(seed)
    for index in range(1, node_count):
        targets = generator.sample(range(index), min(width, index))
        for target in targets:
            adjacency[index, target] = adjacency[target, index] = 1.0
    return PrimeGraph(primes, depths, adjacency, "stochastic_comparison_ablation")
