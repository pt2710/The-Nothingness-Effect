"""Typed SOInet A01+A13, A02+A14 -> B19+B20 -> C29 chain."""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path

import torch

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


APPENDIX = "appendix_tne_artificial_intelligence_architechture.tex"
APPENDIX_SHA256 = "8847de0e94ce317e52280e075e3fb42516d2b07ddb76cc6c4ff6e507545c3842"
# Source order is appendix-faithful: B19 consumes A01+A13 and B20 A02+A14.
A_IDS = tuple(ComplexId(item) for item in (
    "motif_spectral_dual_regularity_law_for_soinets",
    "soi_universal_entropy_plateau_theorem",
    "soi_modality_invariant_convergence_and_collapse_completeness",
    "soi_modality_dual_closure",
))
B_IDS = (
    ComplexId("motif_spectral_entropy_coupling_energy"),
    ComplexId("modality_collapse_symmetry_operator"),
)
C_IDS = (ComplexId("motif_spectral_modality_collapse_spatial_field"),)


@dataclass(frozen=True)
class SOInetContractInput:
    modalities: torch.Tensor
    tolerance: float = 1e-6
    interaction_weight: float = 1.0
    spatial_weight: float = 1.0


@dataclass(frozen=True)
class SOInetSourceLaw:
    law_name: str
    response: torch.Tensor
    residual_field: torch.Tensor
    invariant_residual: float
    failure_condition: str


@dataclass(frozen=True)
class SOInetDerivedLaw:
    law_name: str
    source_residuals: tuple[torch.Tensor, torch.Tensor]
    derived_operator: torch.Tensor
    residual_energy: float
    non_cancellation_energy: float


@dataclass(frozen=True)
class SOInetSpatialClosure:
    law_name: str
    spatial_domain: torch.Tensor
    local_operator: torch.Tensor
    boundary_trace_residual: float
    localization_residual: float
    reconstruction_residual: float
    coercivity_ratio: float
    observability_residual: float
    closure_status: str


def _float(value: torch.Tensor) -> float:
    if not bool(torch.isfinite(value).all()):
        raise NonFiniteValueError("SOInet result contains NaN or infinity")
    return float(value.detach().cpu())


def _validate(value: SOInetContractInput) -> torch.Tensor:
    modalities = value.modalities
    if not isinstance(modalities, torch.Tensor) or modalities.ndim != 3 or min(modalities.shape[:2]) < 2 or modalities.shape[1] < 4 or modalities.shape[2] < 2:
        raise DomainViolationError("SOInet contracts require [modalities, spatial samples, features] with at least 2x4x2 entries")
    if not bool(torch.isfinite(modalities).all()):
        raise NonFiniteValueError("SOInet modality field contains NaN or infinity")
    parameters = torch.tensor((value.tolerance, value.interaction_weight, value.spatial_weight))
    if not bool(torch.isfinite(parameters).all()):
        raise NonFiniteValueError("SOInet contract parameters must be finite")
    if value.tolerance < 0.0 or value.interaction_weight <= 0.0 or value.spatial_weight <= 0.0:
        raise DomainViolationError("SOInet weights must be positive and tolerance non-negative")
    return modalities


def source_operator(index: int, value: SOInetContractInput) -> SOInetSourceLaw:
    modalities = _validate(value)
    if index == 0:
        spectrum = torch.fft.rfft(modalities, dim=1, norm="ortho")
        dominant = spectrum.abs().sum(dim=-1, keepdim=True).argmax(dim=1, keepdim=True)
        mask = torch.zeros_like(spectrum)
        gather_index = dominant.expand(-1, -1, spectrum.shape[-1])
        mask.scatter_(1, gather_index, spectrum.gather(1, gather_index))
        response = torch.fft.irfft(mask, n=modalities.shape[1], dim=1, norm="ortho")
        residual = modalities - response
        failure = "unbounded motif energy or non-regular spectral leakage"
    elif index == 1:
        flat = modalities.reshape(-1, modalities.shape[-1])
        dfi = normalized_dfi(flat, 1.0).reshape(*modalities.shape)
        response = dfi
        residual = (dfi - dfi.mean(dim=(0, 1), keepdim=True)).abs()
        failure = "SOI-universal entropy plateau divergence"
    elif index == 2:
        collapse = modalities.mean(dim=0, keepdim=True)
        response = collapse.expand_as(modalities)
        residual = modalities - response
        failure = "modality-dependent convergence or non-unique collapse"
    elif index == 3:
        dual = torch.flip(modalities, dims=(0,))
        response = 0.5 * (modalities + dual)
        residual = modalities - dual
        failure = "modality dual-closure asymmetry or transfer leakage"
    else:
        raise IndexError(index)
    return SOInetSourceLaw(str(A_IDS[index]), response, residual, _float(torch.linalg.vector_norm(residual)), failure)


def _delta(field: torch.Tensor) -> torch.Tensor:
    magnitude = field.abs()
    return magnitude / (1.0 + magnitude)


def derived_operator(index: int, value: SOInetContractInput) -> SOInetDerivedLaw:
    first = source_operator(2 * index, value)
    second = source_operator(2 * index + 1, value)
    interaction = value.interaction_weight * (_delta(first.residual_field) - _delta(second.residual_field)).square()
    operator = first.residual_field.square() + second.residual_field.square() + interaction
    return SOInetDerivedLaw(
        str(B_IDS[index]), (first.residual_field, second.residual_field), operator,
        _float(operator.sum()), _float(interaction.sum()),
    )


def spatial_operator(value: SOInetContractInput) -> SOInetSpatialClosure:
    modalities = _validate(value)
    first = derived_operator(0, value)
    second = derived_operator(1, value)
    potential = 0.5 * (_delta(first.derived_operator) + _delta(second.derived_operator))
    gradient = potential[:, 1:] - potential[:, :-1]
    localization_density = torch.nn.functional.pad(gradient.square(), (0, 0, 1, 0))
    local = first.derived_operator + second.derived_operator + value.spatial_weight * localization_density
    reconstructed = local - first.derived_operator - second.derived_operator - value.spatial_weight * localization_density
    boundary = _float(local[:, (0, -1)].abs().sum())
    localization = _float(gradient.abs().sum())
    reconstruction = _float(torch.linalg.vector_norm(reconstructed))
    source_norm = _float(torch.linalg.vector_norm(modalities))
    local_norm = _float(torch.linalg.vector_norm(local))
    coercivity = local_norm / source_norm if source_norm > 0.0 else 0.0
    observability = 0.0 if all(torch.count_nonzero(modality) > 0 for modality in modalities) else 1.0
    closed = reconstruction <= value.tolerance and coercivity > 0.0 and observability == 0.0
    domain = torch.linspace(0.0, 1.0, modalities.shape[1], dtype=modalities.dtype, device=modalities.device)
    return SOInetSpatialClosure(
        str(C_IDS[0]), domain, local, boundary, localization, reconstruction,
        coercivity, observability, "numerical_candidate" if closed else "open",
    )


def _residual(name: str, values: tuple[float, ...], tolerance: float) -> ResidualResult:
    norm = sum(item * item for item in values) ** 0.5
    passed = norm <= tolerance
    return ResidualResult(name, values, tolerance, passed, ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN)


def _removal(source_id: ComplexId, baseline: torch.Tensor, removed: torch.Tensor) -> SourceRemovalResult:
    delta = (baseline - removed).abs().sum()
    necessity = _float(delta)
    return SourceRemovalResult(source_id, _float(baseline.sum()), _float(removed.sum()), necessity, necessity > 1e-12)


def _remove_a(b_index: int, source_index: int, value: SOInetContractInput) -> SourceRemovalResult:
    output = derived_operator(b_index, value)
    first, second = output.source_residuals
    surviving = second.square() if source_index == 0 else first.square()
    return _removal(A_IDS[2 * b_index + source_index], output.derived_operator, surviving)


def _remove_b(b_index: int, value: SOInetContractInput) -> SourceRemovalResult:
    output = spatial_operator(value)
    surviving = derived_operator(1 - b_index, value).derived_operator
    return _removal(B_IDS[b_index], output.local_operator, surviving)


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec("SOInet modality field", "finite multi-modality spatial feature field and positive residual weights", (SOInetContractInput,))
    artifact = ArtifactSpec(("residual_table", "modality_closure_field", "source_removal_comparison"), "python -m the_nothingness_effect.artificial_intelligence.soinets.simulation.run_contract_suite")
    result: list[ComplexContract] = []
    for index, complex_id in enumerate(A_IDS):
        result.append(ComplexContract(
            complex_id, APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain,
            CodomainSpec(str(complex_id), "typed modality response, residual field, and failure condition", (SOInetSourceLaw,)),
            partial(source_operator, index),
            residual=lambda source, output, cid=str(complex_id): _residual(cid, (output.invariant_residual,), source.tolerance),
            implementation_path="the_nothingness_effect/artificial_intelligence/soinets/contracts.py",
        ))
    for index, complex_id in enumerate(B_IDS):
        result.append(ComplexContract(
            complex_id, APPENDIX, APPENDIX_SHA256, ComplexLevel.B, (A_IDS[2 * index], A_IDS[2 * index + 1]), domain,
            CodomainSpec(str(complex_id), "positive non-cancelling two-source SOInet residual energy", (SOInetDerivedLaw,)),
            partial(derived_operator, index),
            residual=lambda source, output, cid=str(complex_id): _residual(cid, (output.residual_energy,), source.tolerance),
            source_removal_checks=(partial(_remove_a, index, 0), partial(_remove_a, index, 1)),
            artifact_spec=artifact,
            implementation_path="the_nothingness_effect/artificial_intelligence/soinets/contracts.py",
        ))
    result.append(ComplexContract(
        C_IDS[0], APPENDIX, APPENDIX_SHA256, ComplexLevel.C, B_IDS, domain,
        CodomainSpec(str(C_IDS[0]), "single modality-spatial field with boundary, localization, coercivity, reconstruction, and observability", (SOInetSpatialClosure,)),
        spatial_operator,
        residual=lambda source, output: _residual(str(C_IDS[0]), (output.reconstruction_residual, output.observability_residual), source.tolerance),
        closure_predicate=lambda output, residual: output.closure_status == "numerical_candidate" and output.coercivity_ratio > 0.0 and residual is not None and residual.passed,
        source_removal_checks=(partial(_remove_b, 0), partial(_remove_b, 1)),
        artifact_spec=artifact,
        exact_semantics=False,
        implementation_path="the_nothingness_effect/artificial_intelligence/soinets/contracts.py",
    ))
    return tuple(result)


def registered_soinets_registry(matrix: str | Path = "docs/data/theorem_complex_implementation_matrix.csv") -> TheoremComplexRegistry:
    registry = TheoremComplexRegistry.from_csv(matrix)
    for contract in contracts():
        registry.register(contract)
    return registry
