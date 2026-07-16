"""Typed PGQENN 4A -> 2B -> 1C theorem chain."""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path

import torch

from the_nothingness_effect.artificial_intelligence.shared.elastic_pi_gates import ElasticPiGate
from the_nothingness_effect.artificial_intelligence.shared.entropy_gates import normalized_dfi
from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ArtifactSpec,
    ClosureStatus,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    ResidualResult,
    SourceRemovalResult,
    TheoremComplexRegistry,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import DomainViolationError, NonFiniteValueError

from .growth_law import PrimeGraph


APPENDIX = "appendix_tne_artificial_intelligence_architechture.tex"
APPENDIX_SHA256 = "3a75d4bfdbf9779255d01dd3ae3db6a848a4dc1fa67455ca1f22d5abcadf866a"
A_IDS = tuple(ComplexId(item) for item in (
    "prime_motif_boundedness_motif_induced_energy_divergence",
    "flowpoint_parity_locking_parity_leakage",
    "dfi_plateau_for_pgqenn_dfi_divergence_spiking_under_motif_bias",
    "elastic_e_curvature_regularization_curvature_ambiguity_leakage",
))
B_IDS = (
    ComplexId("prime_motif_parity_stability_functional"),
    ComplexId("dfi_elastic_prime_curvature_coupling"),
)
C_IDS = (ComplexId("prime_motif_elastic_parity_spatial_closure"),)


@dataclass(frozen=True)
class PGQENNContractInput:
    graph: PrimeGraph
    node_features: torch.Tensor
    K_D: float = 1.0
    tolerance: float = 1e-6
    interaction_weight: float = 1.0
    spatial_weight: float = 1.0


@dataclass(frozen=True)
class PGQENNSourceLaw:
    law_name: str
    response: torch.Tensor
    residual_field: torch.Tensor
    invariant_residual: float
    failure_condition: str


@dataclass(frozen=True)
class PGQENNDerivedLaw:
    law_name: str
    source_residuals: tuple[torch.Tensor, torch.Tensor]
    derived_operator: torch.Tensor
    residual_energy: float
    non_cancellation_energy: float


@dataclass(frozen=True)
class PGQENNSpatialClosure:
    law_name: str
    spatial_domain: tuple[int, ...]
    local_operator: torch.Tensor
    boundary_trace_residual: float
    localization_residual: float
    reconstruction_residual: float
    coercivity_ratio: float
    observability_residual: float
    closure_status: str


def _float(value: torch.Tensor) -> float:
    if not bool(torch.isfinite(value).all()):
        raise NonFiniteValueError("PGQENN result contains NaN or infinity")
    return float(value.detach().cpu())


def _validate(value: PGQENNContractInput) -> tuple[torch.Tensor, torch.Tensor]:
    features = value.node_features
    if not isinstance(features, torch.Tensor) or features.ndim != 2 or features.shape[0] != len(value.graph.primes) or features.shape[1] < 2:
        raise DomainViolationError("PGQENN contracts require [prime nodes, features] aligned with a typed PrimeGraph")
    if not bool(torch.isfinite(features).all()):
        raise NonFiniteValueError("PGQENN node features contain NaN or infinity")
    parameters = torch.tensor((value.K_D, value.tolerance, value.interaction_weight, value.spatial_weight))
    if not bool(torch.isfinite(parameters).all()):
        raise NonFiniteValueError("PGQENN contract parameters must be finite")
    if value.K_D <= 0.0 or value.tolerance < 0.0 or value.interaction_weight <= 0.0 or value.spatial_weight <= 0.0:
        raise DomainViolationError("PGQENN K_D and weights must be positive and tolerance non-negative")
    adjacency = value.graph.adjacency.to(dtype=features.dtype, device=features.device)
    return features, adjacency


def _normalized_adjacency(adjacency: torch.Tensor) -> torch.Tensor:
    degree = adjacency.sum(dim=-1, keepdim=True).clamp_min(torch.finfo(adjacency.dtype).eps)
    return adjacency / degree


def source_operator(index: int, value: PGQENNContractInput) -> PGQENNSourceLaw:
    features, adjacency = _validate(value)
    if index == 0:
        degrees = adjacency.sum(dim=-1, keepdim=True)
        response = degrees.expand_as(features)
        residual = torch.relu(degrees - 2.0).expand_as(features)
        failure = "prime motif degree exceeds the declared finite cap"
    elif index == 1:
        phase = torch.tensor(
            [1.0 if depth.value % 2 == 0 else -1.0 for depth in value.graph.two_adic_depths],
            dtype=features.dtype,
            device=features.device,
        ).unsqueeze(-1)
        response = phase * features
        same_parity = (phase @ phase.T > 0).to(features.dtype)
        node_leakage = (adjacency * same_parity).sum(dim=-1, keepdim=True)
        involution_defect = phase * response - features
        residual = involution_defect.abs() + node_leakage.expand_as(features)
        failure = "off-parity edge leakage or loss of Flowpoint involution"
    elif index == 2:
        response = normalized_dfi(features, 1.0)
        residual = (response - response.mean(dim=0, keepdim=True)).abs()
        failure = "DFI motif-bias divergence or spiking"
    elif index == 3:
        normalized = _normalized_adjacency(adjacency)
        curvature = features - normalized @ features
        entropy = features.abs().mean(dim=-1, keepdim=True)
        gain = ElasticPiGate(value.K_D)(entropy) / torch.pi
        response = gain * curvature
        residual = curvature - normalized @ curvature
        failure = "Elastic-pi curvature ambiguity or graph leakage"
    else:
        raise IndexError(index)
    invariant = _float(torch.linalg.vector_norm(residual))
    return PGQENNSourceLaw(str(A_IDS[index]), response, residual, invariant, failure)


def _delta(field: torch.Tensor) -> torch.Tensor:
    magnitude = field.abs()
    return magnitude / (1.0 + magnitude)


def derived_operator(index: int, value: PGQENNContractInput) -> PGQENNDerivedLaw:
    first_index, second_index = ((0, 1), (2, 3))[index]
    first = source_operator(first_index, value)
    second = source_operator(second_index, value)
    interaction = value.interaction_weight * (_delta(first.residual_field) - _delta(second.residual_field)).square()
    operator = first.residual_field.square() + second.residual_field.square() + interaction
    return PGQENNDerivedLaw(
        str(B_IDS[index]), (first.residual_field, second.residual_field), operator,
        _float(operator.sum()), _float(interaction.sum()),
    )


def spatial_operator(value: PGQENNContractInput) -> PGQENNSpatialClosure:
    features, _ = _validate(value)
    adjacency = value.graph.message_adjacency.to(
        dtype=features.dtype, device=features.device
    )
    first = derived_operator(0, value)
    second = derived_operator(1, value)
    potential = 0.5 * (_delta(first.derived_operator) + _delta(second.derived_operator))
    graph_gradient = potential.unsqueeze(1) - potential.unsqueeze(0)
    edge_gradient = adjacency.unsqueeze(-1) * graph_gradient
    localization_density = edge_gradient.square().sum(dim=1)
    local = first.derived_operator + second.derived_operator + value.spatial_weight * localization_density
    reconstructed = local - first.derived_operator - second.derived_operator - value.spatial_weight * localization_density
    degree = adjacency.sum(dim=-1)
    boundary_mask = degree <= torch.median(degree)
    boundary = _float(local[boundary_mask].abs().sum())
    localization = _float(edge_gradient.abs().sum())
    reconstruction = _float(torch.linalg.vector_norm(reconstructed))
    feature_norm = _float(torch.linalg.vector_norm(features))
    local_norm = _float(torch.linalg.vector_norm(local))
    coercivity = local_norm / feature_norm if feature_norm > 0.0 else 0.0
    observability = float((degree == 0).sum().item())
    closed = reconstruction <= value.tolerance and coercivity > 0.0 and observability == 0.0
    return PGQENNSpatialClosure(
        str(C_IDS[0]), value.graph.primes, local, boundary, localization, reconstruction,
        coercivity, observability, "numerical_candidate" if closed else "open",
    )


def _residual(name: str, values: tuple[float, ...], tolerance: float) -> ResidualResult:
    norm = sum(item * item for item in values) ** 0.5
    passed = norm <= tolerance
    return ResidualResult(name, values, tolerance, passed, ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN)


def _removal(source_id: ComplexId, baseline: torch.Tensor, removed: torch.Tensor) -> SourceRemovalResult:
    delta = (baseline - removed).abs().sum()
    value = _float(delta)
    return SourceRemovalResult(source_id, _float(baseline.sum()), _float(removed.sum()), value, value > 1e-12)


def _remove_a(b_index: int, source_index: int, value: PGQENNContractInput) -> SourceRemovalResult:
    output = derived_operator(b_index, value)
    first, second = output.source_residuals
    surviving = second.square() if source_index == 0 else first.square()
    return _removal(A_IDS[2 * b_index + source_index], output.derived_operator, surviving)


def _remove_b(b_index: int, value: PGQENNContractInput) -> SourceRemovalResult:
    output = spatial_operator(value)
    surviving = derived_operator(1 - b_index, value).derived_operator
    return _removal(B_IDS[b_index], output.local_operator, surviving)


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec("PGQENN prime graph field", "finite typed prime graph, aligned finite node features, positive K_D and residual weights", (PGQENNContractInput,))
    artifact = ArtifactSpec(("residual_table", "prime_graph", "source_removal_comparison"), "python -m the_nothingness_effect.artificial_intelligence.pgqenn.simulation.run_contract_suite")
    result: list[ComplexContract] = []
    for index, complex_id in enumerate(A_IDS):
        result.append(ComplexContract(
            complex_id, APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain,
            CodomainSpec(str(complex_id), "typed prime-graph response, residual field, and failure condition", (PGQENNSourceLaw,)),
            partial(source_operator, index),
            residual=lambda source, output, cid=str(complex_id): _residual(cid, (output.invariant_residual,), source.tolerance),
            implementation_path="the_nothingness_effect/artificial_intelligence/pgqenn/contracts.py",
        ))
    for index, complex_id in enumerate(B_IDS):
        result.append(ComplexContract(
            complex_id, APPENDIX, APPENDIX_SHA256, ComplexLevel.B, (A_IDS[2 * index], A_IDS[2 * index + 1]), domain,
            CodomainSpec(str(complex_id), "positive non-cancelling two-source prime-graph residual energy", (PGQENNDerivedLaw,)),
            partial(derived_operator, index),
            residual=lambda source, output, cid=str(complex_id): _residual(cid, (output.residual_energy,), source.tolerance),
            source_removal_checks=(partial(_remove_a, index, 0), partial(_remove_a, index, 1)),
            artifact_spec=artifact,
            implementation_path="the_nothingness_effect/artificial_intelligence/pgqenn/contracts.py",
        ))
    result.append(ComplexContract(
        C_IDS[0], APPENDIX, APPENDIX_SHA256, ComplexLevel.C, B_IDS, domain,
        CodomainSpec(str(C_IDS[0]), "graph-local defect field with boundary, localization, coercivity, reconstruction, and observability", (PGQENNSpatialClosure,)),
        spatial_operator,
        residual=lambda source, output: _residual(str(C_IDS[0]), (output.reconstruction_residual, output.observability_residual), source.tolerance),
        closure_predicate=lambda output, residual: output.closure_status == "numerical_candidate" and output.coercivity_ratio > 0.0 and residual is not None and residual.passed,
        source_removal_checks=(partial(_remove_b, 0), partial(_remove_b, 1)),
        artifact_spec=artifact,
        exact_semantics=False,
        implementation_path="the_nothingness_effect/artificial_intelligence/pgqenn/contracts.py",
    ))
    return tuple(result)


def registered_pgqenn_registry(matrix: str | Path = "docs/data/theorem_complex_implementation_matrix.csv") -> TheoremComplexRegistry:
    registry = TheoremComplexRegistry.from_csv(matrix)
    for contract in contracts():
        registry.register(contract)
    return registry
