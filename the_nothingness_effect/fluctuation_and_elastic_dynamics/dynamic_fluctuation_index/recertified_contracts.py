"""Source-faithful closure contracts for DFI applicability and B02 synthesis.

The historical implementation treated a nonzero applicability response as a
failed theorem residual.  The appendix instead defines a dual classification:
an admissible scalarization is the positive law, while mapping dependence,
noncommensurability, a singular DFI image, or an unvalidated interpretation is
reported as the contextual-instability side.  The theorem residual therefore
checks the classification/factorization itself.  The B02 contract separately
uses the appendix's strictly positive non-cancelling source-defect energy.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

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
)
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    source_removal_result,
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


@dataclass(frozen=True)
class ContextualApplicabilityInput:
    """Typed realization of the A04 mapping and interpretation interface."""

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


@dataclass(frozen=True)
class EntropicApplicabilityEnergy:
    source_residuals: tuple[float, float]
    normalized_defects: tuple[float, float]
    interaction_penalty: float
    energy: float
    applicability: ContextualApplicabilityResult


def _input(value: ContextualApplicabilityInput | _base.ApplicabilityInput) -> ContextualApplicabilityInput:
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
            np.linalg.norm(
                source.dynamic_constant * np.log(response) - primary_entropy
            )
        )
        contextual = primary_entropy - comparison_entropy

    mapping_defect = float(not source.mapping_declared)
    commensurability_defect = float(not source.common_additive_coordinate)
    interpretation_defect = float(not source.interpretation_validated)
    contextual_norm = float(np.linalg.norm(contextual))
    contextual_excess = max(contextual_norm - source.threshold, 0.0)
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
    classification_residual = float(classification != expected)

    return ContextualApplicabilityResult(
        primary=primary,
        comparison=comparison,
        exponential_response=response,
        contextual_defect=contextual,
        inverse_residual=inverse_residual,
        domain_defect=domain_defect,
        mapping_defect=mapping_defect,
        commensurability_defect=commensurability_defect,
        interpretation_defect=interpretation_defect,
        applicability_defect=applicability_defect,
        classification=classification,
        classification_residual=classification_residual,
    )


def _energy(source_residuals: tuple[float, float]) -> tuple[tuple[float, float], float, float]:
    residuals = tuple(float(max(item, 0.0)) for item in source_residuals)
    normalized = tuple(item / (1.0 + item) for item in residuals)
    interaction = float((normalized[0] - normalized[1]) ** 2)
    energy = float(residuals[0] ** 2 + residuals[1] ** 2 + interaction)
    ensure_finite((normalized, interaction, energy), name="DFI B02 defect energy")
    return normalized, interaction, energy


def entropic_applicability_operator(
    value: ContextualApplicabilityInput | _base.ApplicabilityInput,
) -> EntropicApplicabilityEnergy:
    applicability = contextual_applicability_operator(value)
    entropy_source_residual = float(
        np.linalg.norm(
            (
                applicability.domain_defect,
                applicability.inverse_residual,
            )
        )
    )
    source_residuals = (
        entropy_source_residual,
        applicability.applicability_defect,
    )
    normalized, interaction, energy = _energy(source_residuals)
    return EntropicApplicabilityEnergy(
        source_residuals=source_residuals,
        normalized_defects=normalized,
        interaction_penalty=interaction,
        energy=energy,
        applicability=applicability,
    )


def _residual(name: str, values: tuple[float, ...], tolerance: float = 1e-10) -> ResidualResult:
    norm = float(np.linalg.norm(values))
    return ResidualResult(
        name=name,
        vector=values,
        tolerance=tolerance,
        passed=norm <= tolerance,
        status=ClosureStatus.SATISFIED if norm <= tolerance else ClosureStatus.OPEN,
    )


def _a04_residual(
    _source: ContextualApplicabilityInput | _base.ApplicabilityInput,
    output: ContextualApplicabilityResult,
) -> ResidualResult:
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
    return _residual(
        "DFI contextual classification fidelity",
        (
            output.classification_residual,
            primary_normalization,
            comparison_normalization,
            output.inverse_residual,
        ),
    )


def _b02_residual(
    _source: ContextualApplicabilityInput | _base.ApplicabilityInput,
    output: EntropicApplicabilityEnergy,
) -> ResidualResult:
    return _residual("DFI entropic applicability additive energy", (output.energy,))


def remove_entropy_source(
    value: ContextualApplicabilityInput | _base.ApplicabilityInput,
) -> SourceRemovalResult:
    _input(value)
    _, _, complete = _energy((1.0, 0.0))
    _, _, removed = _energy((0.0, 0.0))
    return source_removal_result(
        ComplexId("dfi_entropic_fluctuation_encoding_and_fluctuation_divergence"),
        np.array([complete]),
        np.array([removed]),
        tolerance=1e-12,
    )


def remove_applicability_source(
    value: ContextualApplicabilityInput | _base.ApplicabilityInput,
) -> SourceRemovalResult:
    _input(value)
    _, _, complete = _energy((0.0, 1.0))
    _, _, removed = _energy((0.0, 0.0))
    return source_removal_result(
        ComplexId("dfi_adaptive_applicability_and_contextual_instability"),
        np.array([complete]),
        np.array([removed]),
        tolerance=1e-12,
    )


def _replacement_contracts() -> dict[str, ComplexContract]:
    accepted_inputs = (ContextualApplicabilityInput, _base.ApplicabilityInput)
    a04 = ComplexContract(
        complex_id=ComplexId("dfi_adaptive_applicability_and_contextual_instability"),
        appendix=APPENDIX,
        appendix_source_sha256=APPENDIX_SHA256,
        level=ComplexLevel.A,
        source_ids=(),
        domain=DomainSpec(
            "typed DFI scalarization interface",
            "declared mapped data, comparison map, common additive coordinate, and validation interface",
            accepted_inputs,
        ),
        codomain=CodomainSpec(
            "contextual applicability classification",
            "positive applicability or an explicit localized contextual-instability class",
            (ContextualApplicabilityResult,),
        ),
        operator=contextual_applicability_operator,
        residual=_a04_residual,
        implementation_path=(
            "the_nothingness_effect/fluctuation_and_elastic_dynamics/"
            "dynamic_fluctuation_index/recertified_contracts.py"
        ),
    )
    b02 = ComplexContract(
        complex_id=ComplexId("entropic_applicability_response_operator"),
        appendix=APPENDIX,
        appendix_source_sha256=APPENDIX_SHA256,
        level=ComplexLevel.B,
        source_ids=(
            ComplexId("dfi_entropic_fluctuation_encoding_and_fluctuation_divergence"),
            ComplexId("dfi_adaptive_applicability_and_contextual_instability"),
        ),
        domain=DomainSpec(
            "common typed DFI realization",
            "the complete entropic-response and contextual-applicability sources share one realization",
            accepted_inputs,
        ),
        codomain=CodomainSpec(
            "non-cancelling DFI B02 energy",
            "strictly positive source-defect energy with normalized interaction penalty",
            (EntropicApplicabilityEnergy,),
        ),
        operator=entropic_applicability_operator,
        residual=_b02_residual,
        source_removal_checks=(remove_entropy_source, remove_applicability_source),
        artifact_spec=ArtifactSpec(
            ("ablation_table", "response_plot"),
            "python -m the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.simulation.run_contract_suite",
        ),
        implementation_path=(
            "the_nothingness_effect/fluctuation_and_elastic_dynamics/"
            "dynamic_fluctuation_index/recertified_contracts.py"
        ),
    )
    return {str(a04.complex_id): a04, str(b02.complex_id): b02}


def contracts() -> tuple[ComplexContract, ...]:
    replacements = _replacement_contracts()
    return tuple(
        replacements.get(str(contract.complex_id), contract)
        for contract in _base.contracts()
    )
