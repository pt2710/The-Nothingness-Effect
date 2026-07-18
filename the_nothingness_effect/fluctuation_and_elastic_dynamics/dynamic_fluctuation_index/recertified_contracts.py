"""Typed authoritative realization of DFI A04 applicability classification.

B02 is intentionally not implemented here.  Its authoritative direct-product
law is defined in ``authoritative_product_contracts.py``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ClosureStatus,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    ResidualResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
    NonFiniteValueError,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import (
    ensure_finite,
)

from . import contracts as _base
from .dfi import DFIStatus, NormalizedDFIResult, normalized_dfi


APPENDIX = _base.APPENDIX
APPENDIX_SHA256 = _base.APPENDIX_SHA256
A04 = "dfi_adaptive_applicability_and_contextual_instability"
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/fluctuation_and_elastic_dynamics/"
    "dynamic_fluctuation_index/recertified_contracts.py"
)


@dataclass(frozen=True)
class ContextualApplicabilityInput:
    data: np.ndarray
    spectrum_scale: float
    threshold: float = 1e-10
    comparison_data: np.ndarray | None = None
    dynamic_constant: float = 1.0
    mapping_declared: bool = True
    common_additive_coordinate: bool = True
    interpretation_validated: bool = True


@dataclass(frozen=True)
class ContextualApplicabilityResult:
    primary: NormalizedDFIResult
    comparison: NormalizedDFIResult
    exponential_response: np.ndarray
    contextual_defect: np.ndarray
    inverse_residual: float
    domain_defect: float
    mapping_defect: float
    commensurability_defect: float
    interpretation_defect: float
    applicability_defect: float
    classification: str
    classification_residual: float


def _input(
    value: ContextualApplicabilityInput | _base.ApplicabilityInput,
) -> ContextualApplicabilityInput:
    if isinstance(value, ContextualApplicabilityInput):
        return value
    if isinstance(value, _base.ApplicabilityInput):
        return ContextualApplicabilityInput(
            data=value.data,
            spectrum_scale=value.spectrum_scale,
            threshold=value.threshold,
            comparison_data=value.data,
        )
    raise DomainViolationError(
        "DFI contextual applicability requires ContextualApplicabilityInput "
        "or the legacy ApplicabilityInput"
    )


def _entropy(result: NormalizedDFIResult) -> np.ndarray:
    if result.status is not DFIStatus.FINITE or result.normalized_entropy is None:
        return np.empty(0, dtype=float)
    return result.spectrum_scale * np.asarray(result.normalized_entropy, dtype=float)


def contextual_applicability_operator(
    value: ContextualApplicabilityInput | _base.ApplicabilityInput,
) -> ContextualApplicabilityResult:
    source = _input(value)
    if not np.isfinite(source.threshold) or source.threshold < 0.0:
        raise DomainViolationError("threshold must be finite and non-negative")
    if not np.isfinite(source.dynamic_constant) or source.dynamic_constant <= 0.0:
        raise DomainViolationError("dynamic_constant must be finite and strictly positive")

    comparison_data = source.data if source.comparison_data is None else source.comparison_data
    primary = normalized_dfi(source.data, spectrum_scale=source.spectrum_scale)
    comparison = normalized_dfi(comparison_data, spectrum_scale=source.spectrum_scale)
    primary_entropy = _entropy(primary)
    comparison_entropy = _entropy(comparison)
    domain_defect = float(
        primary.status is not DFIStatus.FINITE
        or comparison.status is not DFIStatus.FINITE
        or primary_entropy.shape != comparison_entropy.shape
    )

    if domain_defect:
        response = np.empty(0, dtype=float)
        contextual = np.empty(0, dtype=float)
        inverse_residual = 0.0
    else:
        with np.errstate(over="raise", invalid="raise"):
            try:
                response = np.exp(primary_entropy / source.dynamic_constant)
            except FloatingPointError as error:
                raise NonFiniteValueError("DFI exponential response overflow") from error
        ensure_finite(response, name="DFI exponential response")
        inverse_residual = float(
            np.linalg.norm(source.dynamic_constant * np.log(response) - primary_entropy)
        )
        contextual = primary_entropy - comparison_entropy

    mapping_defect = float(not source.mapping_declared)
    commensurability_defect = float(not source.common_additive_coordinate)
    interpretation_defect = float(not source.interpretation_validated)
    contextual_excess = max(float(np.linalg.norm(contextual)) - source.threshold, 0.0)
    applicability_defect = float(
        np.linalg.norm(
            (
                domain_defect,
                mapping_defect,
                commensurability_defect,
                interpretation_defect,
                contextual_excess,
                inverse_residual,
            )
        )
    )

    if mapping_defect or commensurability_defect:
        classification = "mapping_invalid"
    elif domain_defect:
        classification = "domain_singular"
    elif contextual_excess > 0.0:
        classification = "contextually_unstable"
    elif interpretation_defect:
        classification = "interpretation_unvalidated"
    else:
        classification = "applicable"

    expected = (
        "mapping_invalid"
        if mapping_defect or commensurability_defect
        else "domain_singular"
        if domain_defect
        else "contextually_unstable"
        if contextual_excess > 0.0
        else "interpretation_unvalidated"
        if interpretation_defect
        else "applicable"
    )
    return ContextualApplicabilityResult(
        primary,
        comparison,
        response,
        contextual,
        inverse_residual,
        domain_defect,
        mapping_defect,
        commensurability_defect,
        interpretation_defect,
        applicability_defect,
        classification,
        float(classification != expected),
    )


def _residual(source, output: ContextualApplicabilityResult) -> ResidualResult:
    value = _input(source)
    primary_normalization = (
        output.primary.normalization_residual
        if output.primary.status is DFIStatus.FINITE
        else 0.0
    )
    comparison_normalization = (
        output.comparison.normalization_residual
        if output.comparison.status is DFIStatus.FINITE
        else 0.0
    )
    vector = (
        output.classification_residual,
        primary_normalization,
        comparison_normalization,
        output.inverse_residual,
    )
    norm = float(np.linalg.norm(vector))
    return ResidualResult(
        "DFI A04 mapping, classification, and factorization",
        vector,
        value.threshold,
        norm <= value.threshold,
        ClosureStatus.SATISFIED if norm <= value.threshold else ClosureStatus.OPEN,
    )


def _replacement() -> ComplexContract:
    accepted = (ContextualApplicabilityInput, _base.ApplicabilityInput)
    return ComplexContract(
        complex_id=ComplexId(A04),
        appendix=APPENDIX,
        appendix_source_sha256=APPENDIX_SHA256,
        level=ComplexLevel.A,
        source_ids=(),
        domain=DomainSpec(
            "admissibly mapped DFI system",
            "measurable scalarization, common additive codomain, finite denominator-admissible values, and declared interpretation",
            accepted,
        ),
        codomain=CodomainSpec(
            "conditional adaptive applicability classification",
            "applicable mapped sector or an explicit localized contextual-instability class",
            (ContextualApplicabilityResult,),
        ),
        operator=contextual_applicability_operator,
        residual=_residual,
        implementation_path=IMPLEMENTATION_PATH,
    )


def contracts() -> tuple[ComplexContract, ...]:
    replacement = _replacement()
    return tuple(
        replacement if str(contract.complex_id) == A04 else contract
        for contract in _base.contracts()
    )
