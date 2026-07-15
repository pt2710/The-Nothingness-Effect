"""Six canonical DFI theorem contracts (3A -> 2B -> 1C)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from equations.theorem_complex_runtime import (
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
from equations.theorem_complex_runtime.invariants import source_removal_result

from .dfi import (
    DFIStatus,
    NormalizedDFIResult,
    dfi_rescaling_residual,
    normalized_dfi,
    require_finite_dfi,
    spatial_localization_residual,
)


APPENDIX = "appendix_tne_fluctuation_and_elastic_dynamics.tex"
APPENDIX_SHA256 = "3277f0ffffcc27dc37ed17f7ecf721ba32234706544ceb5cfbeb5538846f2ba2"


@dataclass(frozen=True)
class DFIInput:
    data: np.ndarray
    spectrum_scale: float


@dataclass(frozen=True)
class DFIRescalingInput:
    data: np.ndarray
    first_scale: float
    second_scale: float


@dataclass(frozen=True)
class ScaleInvariantDFI:
    first: NormalizedDFIResult
    second: NormalizedDFIResult
    rescaling_residual: float
    interaction_energy: float


@dataclass(frozen=True)
class ApplicabilityInput:
    data: np.ndarray
    spectrum_scale: float
    threshold: float


@dataclass(frozen=True)
class EntropicApplicability:
    dfi: NormalizedDFIResult
    response: np.ndarray
    applicability_mask: np.ndarray
    threshold: float
    residual: float


@dataclass(frozen=True)
class SpatialDFIInput:
    data: np.ndarray
    spectrum_scale: float
    tolerance: float = 1e-10


@dataclass(frozen=True)
class SpatialDFIClosure:
    dfi: NormalizedDFIResult
    spatial_domain: tuple[int, ...]
    local_exchange_residual: float
    boundary_leakage_residual: float
    normalization_residual: float
    closure_status: str


def dfi_operator(value: DFIInput) -> NormalizedDFIResult:
    return normalized_dfi(value.data, spectrum_scale=value.spectrum_scale)


def scale_invariant_operator(value: DFIRescalingInput) -> ScaleInvariantDFI:
    first = require_finite_dfi(normalized_dfi(value.data, spectrum_scale=value.first_scale))
    second = require_finite_dfi(normalized_dfi(value.data, spectrum_scale=value.second_scale))
    residual = dfi_rescaling_residual(value.data, value.first_scale, value.second_scale)
    energy = float(np.linalg.norm(first.normalized_entropy) ** 2 + np.linalg.norm(second.normalized_entropy) ** 2)
    return ScaleInvariantDFI(first, second, residual, energy)


def applicability_operator(value: ApplicabilityInput) -> EntropicApplicability:
    result = require_finite_dfi(normalized_dfi(value.data, spectrum_scale=value.spectrum_scale))
    response = np.abs(result.normalized_entropy)
    mask = response <= value.threshold
    residual = float(np.linalg.norm(np.maximum(response - value.threshold, 0.0)))
    return EntropicApplicability(result, response, mask, value.threshold, residual)


def spatial_operator(value: SpatialDFIInput) -> SpatialDFIClosure:
    result = require_finite_dfi(normalized_dfi(value.data, spectrum_scale=value.spectrum_scale))
    exchange, boundary = spatial_localization_residual(result)
    closed = result.normalization_residual <= value.tolerance
    return SpatialDFIClosure(
        result,
        tuple(range(value.data.shape[0])),
        exchange,
        boundary,
        result.normalization_residual,
        "numerical_candidate" if closed else "open",
    )


def _residual(name: str, values: tuple[float, ...], tolerance: float = 1e-10) -> ResidualResult:
    norm = float(np.linalg.norm(values))
    return ResidualResult(
        name,
        values,
        tolerance,
        norm <= tolerance,
        ClosureStatus.SATISFIED if norm <= tolerance else ClosureStatus.OPEN,
    )


def remove_existence_source(value: DFIRescalingInput) -> SourceRemovalResult:
    complete = scale_invariant_operator(value)
    removed = np.zeros_like(complete.first.normalized_entropy)
    return source_removal_result(
        ComplexId("dfi_spectrum_normalized_existence_and_normalization_breakdown"),
        complete.first.normalized_entropy,
        removed,
        tolerance=1e-12,
    )


def remove_rescaling_source(value: DFIRescalingInput) -> SourceRemovalResult:
    complete = scale_invariant_operator(value)
    removed = complete.first.relative_volume - complete.first.base_volume
    return source_removal_result(
        ComplexId("dfi_invariance_under_soi_rescaling_and_spurious_scale_dependence"),
        complete.first.normalized_entropy,
        removed,
        tolerance=1e-12,
    )


def remove_entropy_source(value: ApplicabilityInput) -> SourceRemovalResult:
    complete = applicability_operator(value)
    return source_removal_result(
        ComplexId("dfi_entropic_fluctuation_encoding_and_fluctuation_divergence"),
        complete.response,
        np.zeros_like(complete.response),
        tolerance=1e-12,
    )


def remove_applicability_source(value: ApplicabilityInput) -> SourceRemovalResult:
    complete = applicability_operator(value)
    return source_removal_result(
        ComplexId("dfi_spectrum_normalized_existence_and_normalization_breakdown"),
        complete.applicability_mask.astype(float),
        np.ones_like(complete.response),
        tolerance=1e-12,
    )


def remove_homogeneity_source(value: SpatialDFIInput) -> SourceRemovalResult:
    complete = spatial_operator(value)
    return source_removal_result(
        ComplexId("scale_normalized_dfi_homogeneity_invariant"),
        complete.dfi.normalized_entropy,
        complete.dfi.relative_volume - complete.dfi.base_volume,
        tolerance=1e-12,
    )


def remove_response_source(value: SpatialDFIInput) -> SourceRemovalResult:
    complete = spatial_operator(value)
    return source_removal_result(
        ComplexId("entropic_applicability_response_operator"),
        complete.dfi.normalized_entropy,
        np.zeros_like(complete.dfi.normalized_entropy),
        tolerance=1e-12,
    )


def contracts() -> tuple[ComplexContract, ...]:
    a_ids = (
        "dfi_spectrum_normalized_existence_and_normalization_breakdown",
        "dfi_invariance_under_soi_rescaling_and_spurious_scale_dependence",
        "dfi_entropic_fluctuation_encoding_and_fluctuation_divergence",
    )
    a1 = ComplexContract(
        ComplexId(a_ids[0]), APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (),
        DomainSpec("DFI matrix and spectrum", "finite 2D data and positive spectrum", (DFIInput,)),
        CodomainSpec("normalized DFI", "finite result or explicit singular status", (NormalizedDFIResult,)),
        dfi_operator,
        residual=lambda _source, output: _residual("DFI normalization", (output.normalization_residual,)) if output.status is DFIStatus.FINITE else ResidualResult("DFI singularity", (), 0.0, False, ClosureStatus.SINGULAR),
        implementation_path="equations/dynamic_fluctuation_index/contracts.py",
    )
    a2 = ComplexContract(
        ComplexId(a_ids[1]), APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (),
        DomainSpec("two spectrum scales", "same finite data under two positive scales", (DFIRescalingInput,)),
        CodomainSpec("scale-invariant DFI", "normalized outputs and scale residual", (ScaleInvariantDFI,)),
        scale_invariant_operator,
        residual=lambda _source, output: _residual("DFI scale invariance", (output.rescaling_residual,)),
        implementation_path="equations/dynamic_fluctuation_index/contracts.py",
    )
    a3 = ComplexContract(
        ComplexId(a_ids[2]), APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (),
        DomainSpec("entropic DFI input", "finite data and positive spectrum", (DFIInput,)),
        CodomainSpec("normalized entropic encoding", "finite normalized entropy or obstruction status", (NormalizedDFIResult,)),
        dfi_operator,
        implementation_path="equations/dynamic_fluctuation_index/contracts.py",
    )
    b1 = ComplexContract(
        ComplexId("scale_normalized_dfi_homogeneity_invariant"), APPENDIX, APPENDIX_SHA256, ComplexLevel.B,
        (ComplexId(a_ids[0]), ComplexId(a_ids[1])),
        DomainSpec("homogeneity interaction", "two-scale complete DFI data", (DFIRescalingInput,)),
        CodomainSpec("homogeneity law", "new scale comparison and energy", (ScaleInvariantDFI,)),
        scale_invariant_operator,
        residual=lambda _source, output: _residual("homogeneity", (output.rescaling_residual,)),
        source_removal_checks=(remove_existence_source, remove_rescaling_source),
        artifact_spec=ArtifactSpec(("ablation_table", "scale_plot"), "python -m equations.dynamic_fluctuation_index.simulation.run_contract_suite"),
        implementation_path="equations/dynamic_fluctuation_index/contracts.py",
    )
    b2 = ComplexContract(
        ComplexId("entropic_applicability_response_operator"), APPENDIX, APPENDIX_SHA256, ComplexLevel.B,
        (ComplexId(a_ids[0]), ComplexId(a_ids[2])),
        DomainSpec("entropic applicability", "complete DFI plus declared threshold", (ApplicabilityInput,)),
        CodomainSpec("applicability response", "response field, mask, and residual", (EntropicApplicability,)),
        applicability_operator,
        source_removal_checks=(remove_entropy_source, remove_applicability_source),
        artifact_spec=ArtifactSpec(("ablation_table", "response_plot"), "python -m equations.dynamic_fluctuation_index.simulation.run_contract_suite"),
        implementation_path="equations/dynamic_fluctuation_index/contracts.py",
    )
    c1 = ComplexContract(
        ComplexId("spatially_localized_dfi_consistency_closure"), APPENDIX, APPENDIX_SHA256, ComplexLevel.C,
        (ComplexId("scale_normalized_dfi_homogeneity_invariant"), ComplexId("entropic_applicability_response_operator")),
        DomainSpec("spatial DFI samples", "finite ordered sample domain", (SpatialDFIInput,)),
        CodomainSpec("localized DFI closure", "local exchange, boundary leakage, and status", (SpatialDFIClosure,)),
        spatial_operator,
        residual=lambda _source, output: _residual("spatial DFI normalization", (output.normalization_residual,)),
        closure_predicate=lambda output, residual: output.closure_status == "numerical_candidate" and residual is not None and residual.passed,
        source_removal_checks=(remove_homogeneity_source, remove_response_source),
        artifact_spec=ArtifactSpec(("field_csv", "boundary_plot", "animation_generator"), "python -m equations.dynamic_fluctuation_index.simulation.run_contract_suite"),
        exact_semantics=False,
        implementation_path="equations/dynamic_fluctuation_index/contracts.py",
    )
    return a1, a2, a3, b1, b2, c1


def registered_dfi_registry(matrix: str | Path = "docs/data/theorem_complex_implementation_matrix.csv") -> TheoremComplexRegistry:
    registry = TheoremComplexRegistry.from_csv(matrix)
    for contract in contracts():
        registry.register(contract)
    return registry
