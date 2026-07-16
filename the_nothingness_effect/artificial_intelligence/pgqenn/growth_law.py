"""Deterministic prime/parity growth and explicit stochastic ablation."""

from __future__ import annotations

from dataclasses import dataclass
import random

import torch

from .mpl_tc_dependency import MPLTCMotifProvider


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
    motifs: tuple[str, ...] = ()
    motif_runs: tuple[int, ...] = ()
    dependency_commit: str = ""
    dependency_url: str = ""
    dependency_sha256: str = ""

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
        if self.motifs and (len(self.motifs) != node_count or len(self.motif_runs) != node_count):
            raise ValueError("prime graph motifs and motif runs must align with its nodes")
        if self.growth_mode == "mpl_tc_prime_motif" and (
            not self.motifs or not self.dependency_commit or not self.dependency_url or not self.dependency_sha256
        ):
            raise ValueError("canonical PGQENN growth requires verified MPL-TC motif provenance")


def two_adic_depth(value: int) -> TwoAdicDepth:
    if not isinstance(value, int) or value <= 0:
        raise ValueError("2-adic valuation requires a strictly positive integer")
    depth = 0
    while value % 2 == 0:
        value //= 2
        depth += 1
    return TwoAdicDepth(depth)


def first_primes(count: int) -> tuple[int, ...]:
    """Reference-only prime prefix retained for stochastic comparison mode."""

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
    """Pinned MPL-TC motif growth with 2-adic/parity edge weighting."""

    def __init__(self, motif_width: int = 2, *, provider: MPLTCMotifProvider | None = None):
        if motif_width < 1:
            raise ValueError("motif width must be positive")
        self.motif_width = int(motif_width)
        self.provider = provider or MPLTCMotifProvider()

    @staticmethod
    def _motif_key(label: str) -> tuple[int, int]:
        if label == "U1":
            return (0, 0)
        try:
            depth, index = (int(item) for item in label[1:].split(".", maxsplit=1))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid MPL-TC motif label {label!r}") from exc
        return depth, index

    def build(self, node_count: int, *, dtype: torch.dtype = torch.float32) -> PrimeGraph:
        prefix = self.provider.prefix(node_count)
        primes = prefix.primes
        depths = tuple(two_adic_depth(prime - 1) for prime in primes)
        motif_keys = tuple(self._motif_key(label) for label in prefix.motifs)
        adjacency = torch.zeros((node_count, node_count), dtype=dtype)
        for index in range(1, node_count):
            candidates = list(range(index))
            candidates.sort(key=lambda other: (
                abs(depths[index].value - depths[other].value),
                abs(motif_keys[index][0] - motif_keys[other][0]),
                abs(motif_keys[index][1] - motif_keys[other][1]),
                abs(prefix.motif_runs[index] - prefix.motif_runs[other]),
                abs((primes[index] - primes[other]) % 4 - 2),
                primes[index] - primes[other],
            ))
            targets = {index - 1, *candidates[: self.motif_width]}
            for target in targets:
                depth_distance = abs(depths[index].value - depths[target].value)
                motif_distance = abs(motif_keys[index][0] - motif_keys[target][0])
                run_distance = abs(prefix.motif_runs[index] - prefix.motif_runs[target])
                parity_phase = 1.0 if (index - target) % 2 == 0 else 0.5
                motif_phase = 1.0 / (1.0 + motif_distance)
                run_phase = 1.0 / (1.0 + run_distance)
                weight = parity_phase * motif_phase * run_phase / (1.0 + depth_distance)
                adjacency[index, target] = weight
                adjacency[target, index] = weight
        return PrimeGraph(
            primes,
            depths,
            adjacency,
            "mpl_tc_prime_motif",
            prefix.motifs,
            prefix.motif_runs,
            prefix.repository_commit,
            prefix.repository_url,
            prefix.module_sha256,
        )


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
