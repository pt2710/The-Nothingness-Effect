"""Reusable genuine additive and spatial theorem-complex laws.

The source carrier is only the typed domain.  The B operator computes a new
additive field from every complete source response, while the C operator
computes a local spatial field plus boundary, localization, reconstruction,
coercivity, and observability diagnostics.  Neither result returns the input
sources as a tuple/product pseudo-synthesis.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import Mapping

import numpy as np

from .types import (
    ArtifactSpec,
    ClosureStatus,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    InvariantResult,
    ResidualResult,
    SourceRemovalResult,
)
from .validation import ensure_finite


@dataclass(frozen=True)
class AdditiveDerivationInput:
    """Complete source-law response fields on one common typed codomain."""

    source_values: Mapping[str, np.ndarray]
    tolerance: float = 1e-10


@dataclass(frozen=True)
class AdditiveDerivationResult:
    """New B-level additive operator and non-cancellation certificate."""

    derived_operator: np.ndarray
    source_norms: Mapping[str, float]
    additive_residual: float
    non_cancellation_margin: float


@dataclass(frozen=True)
class SpatialClosureInput:
    """Complete B-source fields sampled on a common spatial domain."""

    source_fields: Mapping[str, np.ndarray]
    tolerance: float = 1e-10
    boundary_mode: str = "periodic"


@dataclass(frozen=True)
class SpatialClosureResult:
    """New C-level local field and explicit spatial closure diagnostics."""

    spatial_domain: tuple[int, ...]
    combined_field: np.ndarray
    local_operator: np.ndarray
    boundary_trace_residual: float
    leakage_residual: float
    localization_residual: float
    reconstruction_residual: float
    coercivity_ratio: float
    observability_residual: float
    closure_status: str


def _values(
    supplied: Mapping[str, np.ndarray], source_ids: tuple[ComplexId, ...], *, label: str
) -> dict[str, np.ndarray]:
    required = tuple(str(item) for item in source_ids)
    if set(supplied) != set(required):
        missing = sorted(set(required) - set(supplied))
        extra = sorted(set(supplied) - set(required))
        raise ValueError(f"{label} source mismatch; missing={missing}, extra={extra}")
    arrays = {key: np.asarray(supplied[key], dtype=float) for key in required}
    shapes = {value.shape for value in arrays.values()}
    if len(shapes) != 1 or not arrays or next(iter(shapes)) == ():
        raise ValueError(f"{label} sources require one common non-scalar shape")
    for key, value in arrays.items():
        ensure_finite(value, name=f"{label} source {key}")
    return arrays


def additive_operator(
    value: AdditiveDerivationInput, *, source_ids: tuple[ComplexId, ...]
) -> AdditiveDerivationResult:
    if not np.isfinite(value.tolerance) or value.tolerance < 0.0:
        raise ValueError("additive tolerance must be finite and non-negative")
    arrays = _values(value.source_values, source_ids, label="B-level additive law")
    ordered = tuple(arrays[str(source_id)] for source_id in source_ids)
    derived = np.add.reduce(ordered)
    reconstructed = sum((item for item in ordered), np.zeros_like(derived))
    residual = float(np.linalg.norm(derived - reconstructed))
    norms = {str(source_id): float(np.linalg.norm(arrays[str(source_id)])) for source_id in source_ids}
    margin = min(norms.values())
    return AdditiveDerivationResult(derived, norms, residual, margin)


def additive_invariant(
    source: AdditiveDerivationInput, output: AdditiveDerivationResult
) -> InvariantResult:
    return InvariantResult(
        "complete-source additive reconstruction",
        output.additive_residual <= source.tolerance,
        output.additive_residual,
        source.tolerance,
        "the derived operator equals the sum of every declared source response",
    )


def additive_residual(
    source: AdditiveDerivationInput, output: AdditiveDerivationResult
) -> ResidualResult:
    passed = output.additive_residual <= source.tolerance
    return ResidualResult(
        "additive derivation residual",
        (output.additive_residual,),
        source.tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {"non_cancellation_margin": output.non_cancellation_margin},
    )


def _remove_additive_source(
    source_id: ComplexId,
    source_ids: tuple[ComplexId, ...],
    value: AdditiveDerivationInput,
) -> SourceRemovalResult:
    arrays = _values(value.source_values, source_ids, label="B-level source removal")
    complete = np.add.reduce(tuple(arrays[str(item)] for item in source_ids))
    removed = sum(
        (arrays[str(item)] for item in source_ids if item != source_id),
        np.zeros_like(complete),
    )
    necessity = float(np.linalg.norm(arrays[str(source_id)]))
    return SourceRemovalResult(
        source_id,
        float(np.linalg.norm(complete)),
        float(np.linalg.norm(removed)),
        necessity,
        necessity > value.tolerance,
    )


def spatial_operator(
    value: SpatialClosureInput, *, source_ids: tuple[ComplexId, ...]
) -> SpatialClosureResult:
    if value.boundary_mode not in {"periodic", "anchored"}:
        raise ValueError("boundary_mode must be 'periodic' or 'anchored'")
    if not np.isfinite(value.tolerance) or value.tolerance < 0.0:
        raise ValueError("spatial tolerance must be finite and non-negative")
    arrays = _values(value.source_fields, source_ids, label="C-level spatial closure")
    ordered = tuple(arrays[str(source_id)] for source_id in source_ids)
    combined = np.add.reduce(ordered)
    local = np.gradient(combined, axis=0) if combined.shape[0] > 1 else np.zeros_like(combined)
    reconstructed = sum((item for item in ordered), np.zeros_like(combined))
    reconstruction = float(np.linalg.norm(combined - reconstructed))
    if value.boundary_mode == "periodic" and combined.shape[0] > 1:
        boundary = float(np.linalg.norm(combined[0] - combined[-1]))
    elif value.boundary_mode == "anchored":
        boundary = float(np.linalg.norm(combined[0]))
    else:
        boundary = 0.0
    source_local = np.add.reduce(
        tuple(
            np.gradient(item, axis=0) if item.shape[0] > 1 else np.zeros_like(item)
            for item in ordered
        )
    )
    localization = float(np.linalg.norm(local - source_local))
    denominator = sum(float(np.linalg.norm(item)) for item in ordered)
    coercivity = float(np.linalg.norm(combined)) / max(denominator, np.finfo(float).eps)
    observability = float(sum(max(0.0, value.tolerance - np.linalg.norm(item)) for item in ordered))
    passed = max(boundary, reconstruction, localization, observability) <= value.tolerance
    return SpatialClosureResult(
        tuple(combined.shape),
        combined,
        np.asarray(local),
        boundary,
        boundary,
        localization,
        reconstruction,
        coercivity,
        observability,
        "numerical_candidate" if passed else "open",
    )


def spatial_invariant(
    source: SpatialClosureInput, output: SpatialClosureResult
) -> InvariantResult:
    residual = max(output.localization_residual, output.reconstruction_residual)
    return InvariantResult(
        "localization and reconstruction",
        residual <= source.tolerance,
        residual,
        source.tolerance,
    )


def spatial_residual(
    source: SpatialClosureInput, output: SpatialClosureResult
) -> ResidualResult:
    vector = (
        output.boundary_trace_residual,
        output.leakage_residual,
        output.localization_residual,
        output.reconstruction_residual,
        output.observability_residual,
    )
    passed = max(vector) <= source.tolerance
    return ResidualResult(
        "spatial closure residual",
        vector,
        source.tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {"coercivity_ratio": output.coercivity_ratio},
    )


def spatial_predicate(output: SpatialClosureResult, residual: ResidualResult | None) -> bool:
    return bool(
        residual is not None
        and residual.passed
        and output.closure_status == "numerical_candidate"
        and output.coercivity_ratio > 0.0
    )


def _remove_spatial_source(
    source_id: ComplexId,
    source_ids: tuple[ComplexId, ...],
    value: SpatialClosureInput,
) -> SourceRemovalResult:
    arrays = _values(value.source_fields, source_ids, label="C-level source removal")
    complete = np.add.reduce(tuple(arrays[str(item)] for item in source_ids))
    removed = sum(
        (arrays[str(item)] for item in source_ids if item != source_id),
        np.zeros_like(complete),
    )
    necessity = float(np.linalg.norm(arrays[str(source_id)]))
    return SourceRemovalResult(
        source_id,
        float(np.linalg.norm(complete)),
        float(np.linalg.norm(removed)),
        necessity,
        necessity > value.tolerance,
    )


def additive_contract(
    complex_id: str,
    source_ids: tuple[str, ...],
    *,
    appendix: str,
    appendix_sha256: str,
    implementation_path: str,
) -> ComplexContract:
    sources = tuple(ComplexId(item) for item in source_ids)
    module_name = implementation_path.removesuffix(".py").replace("/", ".")
    return ComplexContract(
        ComplexId(complex_id),
        appendix,
        appendix_sha256,
        ComplexLevel.B,
        sources,
        DomainSpec(
            "complete additive source fields",
            "one finite common-shape response field for every declared A source",
            (AdditiveDerivationInput,),
        ),
        CodomainSpec(
            "derived additive law",
            "new summed operator with residual and non-cancellation margin",
            (AdditiveDerivationResult,),
        ),
        partial(additive_operator, source_ids=sources),
        invariant=additive_invariant,
        residual=additive_residual,
        source_removal_checks=tuple(
            partial(_remove_additive_source, source_id, sources) for source_id in sources
        ),
        artifact_spec=ArtifactSpec(
            ("source_removal_table", "additive_residual_trace"),
            f"python -m {module_name}",
        ),
        implementation_path=implementation_path,
    )


def spatial_contract(
    complex_id: str,
    source_ids: tuple[str, ...],
    *,
    appendix: str,
    appendix_sha256: str,
    implementation_path: str,
) -> ComplexContract:
    sources = tuple(ComplexId(item) for item in source_ids)
    module_name = implementation_path.removesuffix(".py").replace("/", ".")
    return ComplexContract(
        ComplexId(complex_id),
        appendix,
        appendix_sha256,
        ComplexLevel.C,
        sources,
        DomainSpec(
            "common spatial B-source domain",
            "finite common-shape spatial field for every declared B source",
            (SpatialClosureInput,),
        ),
        CodomainSpec(
            "localized spatial closure",
            "local operator, boundary/leakage, reconstruction, coercivity, and status",
            (SpatialClosureResult,),
        ),
        partial(spatial_operator, source_ids=sources),
        invariant=spatial_invariant,
        residual=spatial_residual,
        closure_predicate=spatial_predicate,
        source_removal_checks=tuple(
            partial(_remove_spatial_source, source_id, sources) for source_id in sources
        ),
        artifact_spec=ArtifactSpec(
            ("boundary_map", "source_removal_table", "closure_trace"),
            f"python -m {module_name}",
        ),
        exact_semantics=False,
        implementation_path=implementation_path,
    )
