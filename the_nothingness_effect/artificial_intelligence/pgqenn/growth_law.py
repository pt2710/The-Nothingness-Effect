"""Deterministic prime/parity growth and explicit stochastic ablation."""

from __future__ import annotations

from dataclasses import dataclass
import random

import torch

from .mpl_tc_dependency import (
    MPLTCAxisPlacement,
    MPLTCMotifProvider,
    MPLTCTriadicStreams,
    TCStreamKind,
)


@dataclass(frozen=True, order=True)
class TwoAdicDepth:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or self.value < 0:
            raise ValueError("2-adic depth must be a non-negative integer")


@dataclass(frozen=True)
class TriadicGrowthGraph:
    """Experimental PGQENN bridge over MPL-TC's four finite TC streams."""

    values: tuple[int, ...]
    stream_kinds: tuple[TCStreamKind, ...]
    domains: tuple[str, ...]
    axes: tuple[str, ...]
    dyadic_depths: tuple[int, ...]
    least_prime_factors: tuple[int | None, ...]
    cofactors: tuple[int | None, ...]
    source_prime_indices: tuple[int, ...]
    coordinates_3d: torch.Tensor
    adjacency: torch.Tensor
    spatial_adjacency: torch.Tensor
    finite_limit: int
    dependency_sha256: str
    axis_labels: tuple[str, str, str] = (
        "number_magnitude",
        "tc_stream_kind",
        "axis_depth",
    )

    def __post_init__(self) -> None:
        node_count = len(self.values)
        aligned = (
            self.stream_kinds,
            self.domains,
            self.axes,
            self.dyadic_depths,
            self.least_prime_factors,
            self.cofactors,
            self.source_prime_indices,
        )
        if node_count < 4 or any(len(field) != node_count for field in aligned):
            raise ValueError("triadic growth fields must align across at least four nodes")
        if set(self.stream_kinds) != {
            "pure_even_lift",
            "first_order_odd",
            "lpf_odd_composite",
            "mixed_even_composite",
        }:
            raise ValueError("triadic growth must contain all four MPL-TC streams")
        if self.coordinates_3d.shape != (node_count, 3):
            raise ValueError("triadic growth coordinates must have shape [nodes, 3]")
        for name, value in (
            ("adjacency", self.adjacency),
            ("spatial adjacency", self.spatial_adjacency),
        ):
            if value.shape != (node_count, node_count):
                raise ValueError(f"triadic growth {name} has the wrong shape")
            if not bool(torch.isfinite(value).all()) or not torch.allclose(value, value.T):
                raise ValueError(f"triadic growth {name} must be finite and symmetric")
            if not bool((torch.diagonal(value) == 0).all()):
                raise ValueError(f"triadic growth {name} cannot contain self loops")
        if not bool(torch.isfinite(self.coordinates_3d).all()):
            raise ValueError("triadic growth coordinates contain NaN or infinity")

    @property
    def stream_counts(self) -> dict[str, int]:
        return {
            kind: self.stream_kinds.count(kind)
            for kind in (
                "pure_even_lift",
                "first_order_odd",
                "lpf_odd_composite",
                "mixed_even_composite",
            )
        }


@dataclass(frozen=True)
class PrimeGraph:
    primes: tuple[int, ...]
    two_adic_depths: tuple[TwoAdicDepth, ...]
    adjacency: torch.Tensor
    coordinates_3d: torch.Tensor
    spatial_adjacency: torch.Tensor
    growth_mode: str
    motifs: tuple[str, ...] = ()
    motif_runs: tuple[int, ...] = ()
    dependency_commit: str = ""
    dependency_url: str = ""
    dependency_sha256: str = ""
    axis_labels: tuple[str, str, str] = (
        "prime_shell",
        "mpl_tc_motif",
        "two_adic_run_depth",
    )
    triadic_growth: TriadicGrowthGraph | None = None

    def __post_init__(self) -> None:
        node_count = len(self.primes)
        if node_count < 2 or len(self.two_adic_depths) != node_count:
            raise ValueError("prime graph requires aligned primes and 2-adic depths")
        if self.adjacency.shape != (node_count, node_count):
            raise ValueError("prime graph adjacency has the wrong shape")
        if self.coordinates_3d.shape != (node_count, 3):
            raise ValueError("prime graph 3D coordinates must have shape [nodes, 3]")
        if self.spatial_adjacency.shape != (node_count, node_count):
            raise ValueError("prime graph spatial adjacency has the wrong shape")
        for name, value in (
            ("adjacency", self.adjacency),
            ("3D coordinates", self.coordinates_3d),
            ("spatial adjacency", self.spatial_adjacency),
        ):
            if not bool(torch.isfinite(value).all()):
                raise ValueError(f"prime graph {name} contains NaN or infinity")
        for name, value in (
            ("adjacency", self.adjacency),
            ("spatial adjacency", self.spatial_adjacency),
        ):
            if not torch.allclose(value, value.T):
                raise ValueError(f"prime graph {name} must be symmetric")
            if not bool((torch.diagonal(value) == 0).all()):
                raise ValueError(f"prime graph {name} cannot contain self loops")
        if self.motifs and (len(self.motifs) != node_count or len(self.motif_runs) != node_count):
            raise ValueError("prime graph motifs and motif runs must align with its nodes")
        if self.growth_mode == "mpl_tc_prime_motif" and (
            not self.motifs or not self.dependency_commit or not self.dependency_url or not self.dependency_sha256
        ):
            raise ValueError("canonical PGQENN growth requires verified MPL-TC motif provenance")
        if self.growth_mode == "mpl_tc_prime_motif" and self.triadic_growth is None:
            raise ValueError("canonical PGQENN growth requires the typed four-stream TC bridge")

    @property
    def message_adjacency(self) -> torch.Tensor:
        """The canonical edges localized by the actual 3D growth geometry."""

        return self.spatial_adjacency


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


def _normalize_axis(values: torch.Tensor) -> torch.Tensor:
    minimum = torch.min(values)
    maximum = torch.max(values)
    extent = maximum - minimum
    if float(extent) <= torch.finfo(values.dtype).eps:
        return torch.zeros_like(values)
    return 2.0 * (values - minimum) / extent - 1.0


def growth_coordinates_3d(
    primes: tuple[int, ...],
    depths: tuple[TwoAdicDepth, ...],
    motifs: tuple[str, ...],
    motif_runs: tuple[int, ...],
    *,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    """Map prime shells, MPL-TC motifs and 2-adic run depth to three axes."""

    node_count = len(primes)
    if len(depths) != node_count:
        raise ValueError("3D growth requires aligned primes and 2-adic depths")
    if motifs and (len(motifs) != node_count or len(motif_runs) != node_count):
        raise ValueError("3D growth requires aligned MPL-TC motifs and runs")
    prime_axis = _normalize_axis(torch.log(torch.tensor(primes, dtype=dtype)))
    if motifs:
        motif_values = []
        for label in motifs:
            depth, index = CanonicalPrimeGrowth._motif_key(label)
            motif_values.append(float(depth) + float(index) / (2.0 + depth))
        motif_axis = _normalize_axis(torch.tensor(motif_values, dtype=dtype))
        runs = torch.tensor(motif_runs, dtype=dtype)
    else:
        # The stochastic graph is an explicit ablation; its second axis uses
        # prime residues instead of claiming MPL-TC motif semantics.
        motif_axis = _normalize_axis(
            torch.tensor([prime % 6 for prime in primes], dtype=dtype)
        )
        runs = torch.arange(1, node_count + 1, dtype=dtype)
    depth_values = torch.tensor([depth.value for depth in depths], dtype=dtype)
    depth_run_axis = _normalize_axis(depth_values + torch.log1p(runs))
    coordinates = torch.stack((prime_axis, motif_axis, depth_run_axis), dim=-1)
    if not bool(torch.isfinite(coordinates).all()):
        raise ValueError("3D growth coordinate construction became non-finite")
    return coordinates


def spatial_locality_adjacency(
    adjacency: torch.Tensor,
    coordinates_3d: torch.Tensor,
) -> torch.Tensor:
    """Localize canonical edges by distance without removing either source."""

    if adjacency.ndim != 2 or adjacency.shape[0] != adjacency.shape[1]:
        raise ValueError("spatial locality requires a square adjacency")
    if coordinates_3d.shape != (adjacency.shape[0], 3):
        raise ValueError("spatial locality requires one 3D coordinate per node")
    distances = torch.cdist(coordinates_3d, coordinates_3d)
    edge_distances = distances[adjacency > 0]
    if edge_distances.numel() == 0:
        raise ValueError("spatial locality requires at least one canonical edge")
    scale = torch.median(edge_distances).clamp_min(
        torch.finfo(coordinates_3d.dtype).eps
    )
    locality = 0.25 + 0.75 * torch.exp(-distances / scale)
    spatial = adjacency * locality.to(dtype=adjacency.dtype, device=adjacency.device)
    spatial.fill_diagonal_(0.0)
    if not bool(torch.isfinite(spatial).all()):
        raise ValueError("3D spatial locality adjacency became non-finite")
    return spatial


_STREAM_ORDER: dict[TCStreamKind, int] = {
    "pure_even_lift": 0,
    "first_order_odd": 1,
    "lpf_odd_composite": 2,
    "mixed_even_composite": 3,
}


def _source_prime_index(
    placement: MPLTCAxisPlacement,
    primes: tuple[int, ...],
) -> int:
    if placement.stream_kind == "pure_even_lift":
        return min(max(placement.dyadic_depth - 1, 0), len(primes) - 1)
    if placement.value in primes:
        return primes.index(placement.value)
    if placement.least_prime_factor in primes:
        return primes.index(int(placement.least_prime_factor))
    odd_face = int(placement.cofactor or placement.value)
    for index, prime in enumerate(primes):
        if prime > 2 and odd_face % prime == 0:
            return index
    raise ValueError(f"TC placement {placement.value} has no realized prime source")


def triadic_growth_graph(
    streams: MPLTCTriadicStreams,
    primes: tuple[int, ...],
    *,
    dtype: torch.dtype = torch.float32,
) -> TriadicGrowthGraph:
    """Build a heterogeneous 3D graph while retaining typed stream identity."""

    placements = tuple(
        sorted(
            streams.placements,
            key=lambda item: (item.value, _STREAM_ORDER[item.stream_kind]),
        )
    )
    values = tuple(item.value for item in placements)
    kinds = tuple(item.stream_kind for item in placements)
    source_indices = tuple(_source_prime_index(item, primes) for item in placements)
    magnitude = _normalize_axis(torch.log(torch.tensor(values, dtype=dtype)))
    stream_axis = torch.tensor(
        [-1.0 + 2.0 * _STREAM_ORDER[kind] / 3.0 for kind in kinds], dtype=dtype
    )
    structural_values = []
    for placement in placements:
        if placement.stream_kind == "pure_even_lift":
            structural = float(placement.dyadic_depth)
        elif placement.stream_kind == "first_order_odd":
            structural = float(two_adic_depth(placement.value - 1).value)
        elif placement.stream_kind == "lpf_odd_composite":
            structural = float(int(placement.axis[1:])) + torch.log1p(
                torch.tensor(float(placement.cofactor or 1))
            ).item()
        else:
            structural = float(placement.dyadic_depth) + torch.log1p(
                torch.tensor(float(placement.cofactor or 1))
            ).item()
        structural_values.append(structural)
    structural_axis = _normalize_axis(torch.tensor(structural_values, dtype=dtype))
    coordinates = torch.stack((magnitude, stream_axis, structural_axis), dim=-1)

    node_count = len(placements)
    adjacency = torch.zeros((node_count, node_count), dtype=dtype)
    by_stream: dict[str, list[int]] = {kind: [] for kind in _STREAM_ORDER}
    by_value = {placement.value: index for index, placement in enumerate(placements)}
    for index, placement in enumerate(placements):
        by_stream[placement.stream_kind].append(index)
    for indices in by_stream.values():
        for source, target in zip(indices[:-1], indices[1:], strict=True):
            gap = abs(values[target] - values[source])
            weight = 1.0 / (1.0 + torch.log1p(torch.tensor(float(gap))).item())
            adjacency[source, target] = adjacency[target, source] = weight

    prime_representatives: dict[int, int] = {}
    for index, placement in enumerate(placements):
        source = source_indices[index]
        if placement.value == primes[source]:
            prime_representatives[source] = index
    for index, placement in enumerate(placements):
        representative = prime_representatives[source_indices[index]]
        if representative != index:
            distance = abs(
                torch.log(torch.tensor(float(placement.value))).item()
                - torch.log(torch.tensor(float(primes[source_indices[index]]))).item()
            )
            weight = 1.0 / (1.0 + distance)
            adjacency[index, representative] = adjacency[representative, index] = max(
                float(adjacency[index, representative]), weight
            )
        parent = by_value.get(placement.value // 2) if placement.value % 2 == 0 else None
        if parent is not None and parent != index:
            adjacency[index, parent] = adjacency[parent, index] = max(
                float(adjacency[index, parent]), 0.75
            )
    spatial = spatial_locality_adjacency(adjacency, coordinates)
    return TriadicGrowthGraph(
        values=values,
        stream_kinds=kinds,
        domains=tuple(item.domain for item in placements),
        axes=tuple(item.axis for item in placements),
        dyadic_depths=tuple(item.dyadic_depth for item in placements),
        least_prime_factors=tuple(item.least_prime_factor for item in placements),
        cofactors=tuple(item.cofactor for item in placements),
        source_prime_indices=source_indices,
        coordinates_3d=coordinates,
        adjacency=adjacency,
        spatial_adjacency=spatial,
        finite_limit=streams.finite_limit,
        dependency_sha256=streams.module_sha256,
    )


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
        coordinates = growth_coordinates_3d(
            primes, depths, prefix.motifs, prefix.motif_runs, dtype=dtype
        )
        spatial_adjacency = spatial_locality_adjacency(adjacency, coordinates)
        triadic = triadic_growth_graph(
            self.provider.triadic_streams(node_count), primes, dtype=dtype
        )
        return PrimeGraph(
            primes=primes,
            two_adic_depths=depths,
            adjacency=adjacency,
            coordinates_3d=coordinates,
            spatial_adjacency=spatial_adjacency,
            growth_mode="mpl_tc_prime_motif",
            motifs=prefix.motifs,
            motif_runs=prefix.motif_runs,
            dependency_commit=prefix.repository_commit,
            dependency_url=prefix.repository_url,
            dependency_sha256=prefix.module_sha256,
            triadic_growth=triadic,
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
    coordinates = growth_coordinates_3d(primes, depths, (), (), dtype=adjacency.dtype)
    spatial_adjacency = spatial_locality_adjacency(adjacency, coordinates)
    return PrimeGraph(
        primes=primes,
        two_adic_depths=depths,
        adjacency=adjacency,
        coordinates_3d=coordinates,
        spatial_adjacency=spatial_adjacency,
        growth_mode="stochastic_comparison_ablation",
        axis_labels=("prime_shell", "prime_residue_ablation", "two_adic_index_depth"),
    )
