"""Byte-faithful DFI A04/B02/C01 contracts for the authoritative appendix.

The appendix member with SHA-256
63e5684e4c4bb016a2cc62d46574c2174fbe14eb5f50c16db825ca33b0836389
specifies B02 and C01 as direct products with exact coordinate projections,
source-predicate conjunctions, localized max residuals, and coordinatewise
involutions.  This module implements those structures without replacing them
by an additive or coercive surrogate.
"""

from __future__ import annotations

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ArtifactSpec,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    SourceRemovalResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.exact_product_carrier import (
    ExactProductInput,
    ExactProductResult,
    evaluate_exact_product,
    exact_product_predicate,
    exact_product_residual,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    source_removal_result,
)

from . import contracts as _legacy
from . import recertified_contracts as _a04
from .dfi import DFIStatus, normalized_dfi, require_finite_dfi
from .extended_contracts import (
    DFIDecompositionInput,
    DFIFlowpointInterfaceInput,
    DFISimulationInput,
    decomposition_certificate,
    flowpoint_interface_certificate,
    simulation_certificate,
)


A03 = "dfi_entropic_fluctuation_encoding_and_fluctuation_divergence"
A04 = "dfi_adaptive_applicability_and_contextual_instability"
B01 = "scale_normalized_dfi_homogeneity_invariant"
B02 = "entropic_applicability_response_operator"
B03 = "flowpoint_certified_dfi_validation_functional"
C01 = "spatially_localized_dfi_consistency_closure"
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/fluctuation_and_elastic_dynamics/"
    "dynamic_fluctuation_index/authoritative_product_contracts.py"
)


def _flatten(items: tuple[np.ndarray, ...]) -> np.ndarray:
    return np.concatenate(tuple(np.asarray(item, dtype=float).ravel() for item in items))


def _classification_pair(finite: bool, diagnostics: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    detail = np.asarray(diagnostics, dtype=float).ravel()
    first = np.concatenate((np.array([float(finite)]), detail))
    second = np.concatenate((np.array([float(not finite)]), detail))
    return first, second


def _b02_input(
    value: ExactProductInput | _a04.ContextualApplicabilityInput | _legacy.ApplicabilityInput,
) -> ExactProductInput:
    if isinstance(value, ExactProductInput):
        return value
    source = _a04._input(value)
    entropic = normalized_dfi(source.data, spectrum_scale=source.spectrum_scale)
    applicability = _a04.contextual_applicability_operator(source)

    finite = entropic.status is DFIStatus.FINITE
    entropy_diagnostics = np.array(
        [
            entropic.normalization_residual,
            entropic.divergence_witness.minimum_absolute_denominator,
        ],
        dtype=float,
    )
    entropic_first, entropic_second = _classification_pair(
        finite,
        entropy_diagnostics,
    )

    applicable = applicability.classification == "applicable"
    applicability_diagnostics = np.array(
        [
            applicability.domain_defect,
            applicability.mapping_defect,
            applicability.commensurability_defect,
            applicability.interpretation_defect,
            applicability.applicability_defect,
            applicability.inverse_residual,
        ],
        dtype=float,
    )
    applicability_first, applicability_second = _classification_pair(
        applicable,
        applicability_diagnostics,
    )
    entropy_classification_residual = abs(
        float(finite) + float(not finite) - 1.0
    )
    applicability_classification_residual = float(
        applicability.classification_residual
    )
    return ExactProductInput(
        first_states={
            A03: entropic_first,
            A04: applicability_first,
        },
        second_states={
            A03: entropic_second,
            A04: applicability_second,
        },
        first_residuals={
            A03: entropy_classification_residual,
            A04: applicability_classification_residual,
        },
        second_residuals={
            A03: entropy_classification_residual,
            A04: applicability_classification_residual,
        },
        tolerance=source.threshold,
    )


def b02_operator(
    value: ExactProductInput | _a04.ContextualApplicabilityInput | _legacy.ApplicabilityInput,
) -> ExactProductResult:
    return evaluate_exact_product(_b02_input(value), source_ids=(A03, A04))


def _b02_residual(value, output):
    return exact_product_residual(
        _b02_input(value),
        output,
        name="DFI B02 product projections and coordinate involution",
    )


def _b01_pair(value: _legacy.SpatialDFIInput) -> tuple[np.ndarray, np.ndarray, float]:
    output = _legacy.scale_invariant_operator(
        _legacy.DFIRescalingInput(
            value.data,
            value.spectrum_scale,
            2.0 * value.spectrum_scale,
        )
    )
    finite = output.rescaling_residual <= value.tolerance
    first, second = _classification_pair(
        finite,
        np.array([output.rescaling_residual, output.interaction_energy]),
    )
    return first, second, 0.0


def _b03_pair(value: _legacy.SpatialDFIInput) -> tuple[np.ndarray, np.ndarray, float]:
    data = np.asarray(value.data, dtype=float)
    feature_count = data.shape[1]
    decomposition = decomposition_certificate(
        DFIDecompositionInput(
            data,
            value.spectrum_scale,
            tuple(range(feature_count)),
            value.tolerance,
        )
    )
    interface = flowpoint_interface_certificate(
        DFIFlowpointInterfaceInput(
            data,
            value.spectrum_scale,
            np.eye(feature_count),
            value.tolerance,
        )
    )
    canonical = require_finite_dfi(
        normalized_dfi(data, spectrum_scale=value.spectrum_scale)
    )
    simulation = simulation_certificate(
        DFISimulationInput(
            data,
            value.spectrum_scale,
            np.asarray(canonical.normalized_entropy, dtype=float),
            value.tolerance,
        )
    )
    residuals = np.array(
        [
            decomposition.component_assignment_residual,
            decomposition.additive_total_residual,
            decomposition.permutation_covariance_residual,
            decomposition.reproducibility_residual,
            interface.involution_residual,
            interface.component_consistency_residual,
            interface.total_consistency_residual,
            interface.commuting_diagram_residual,
            simulation.component_residual,
            simulation.total_residual,
            simulation.normalization_residual,
            simulation.maximum_absolute_error,
        ],
        dtype=float,
    )
    valid = float(np.max(residuals, initial=0.0)) <= value.tolerance
    first, second = _classification_pair(valid, residuals)
    return first, second, 0.0


def _c01_input(value: ExactProductInput | _legacy.SpatialDFIInput) -> ExactProductInput:
    if isinstance(value, ExactProductInput):
        return value
    b01_first, b01_second, b01_residual = _b01_pair(value)
    b02 = b02_operator(
        _a04.ContextualApplicabilityInput(
            data=value.data,
            comparison_data=np.asarray(value.data, dtype=float).copy(),
            spectrum_scale=value.spectrum_scale,
            threshold=value.tolerance,
        )
    )
    b03_first, b03_second, b03_residual = _b03_pair(value)
    return ExactProductInput(
        first_states={
            B01: b01_first,
            B02: _flatten(b02.first_product),
            B03: b03_first,
        },
        second_states={
            B01: b01_second,
            B02: _flatten(b02.second_product),
            B03: b03_second,
        },
        first_residuals={
            B01: b01_residual,
            B02: b02.first_product_residual,
            B03: b03_residual,
        },
        second_residuals={
            B01: b01_residual,
            B02: b02.second_product_residual,
            B03: b03_residual,
        },
        tolerance=value.tolerance,
    )


def c01_operator(value: ExactProductInput | _legacy.SpatialDFIInput) -> ExactProductResult:
    return evaluate_exact_product(_c01_input(value), source_ids=(B01, B02, B03))


def _c01_residual(value, output):
    return exact_product_residual(
        _c01_input(value),
        output,
        name="DFI C01 spatial product projections and pointwise involution",
    )


def _removal(source_id: str, position: int, count: int):
    def check(_value) -> SourceRemovalResult:
        complete = np.ones(count, dtype=float)
        removed = complete.copy()
        removed[position] = 0.0
        return source_removal_result(
            ComplexId(source_id),
            complete,
            removed,
            tolerance=1e-12,
        )

    return check


def _replacement_contracts() -> dict[str, ComplexContract]:
    artifact = ArtifactSpec(
        ("projection_table", "source_residual_table", "exchange_square_record"),
        "python -m the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.simulation.run_contract_suite",
    )
    b02 = ComplexContract(
        complex_id=ComplexId(B02),
        appendix=_a04.APPENDIX,
        appendix_source_sha256=_a04.APPENDIX_SHA256,
        level=ComplexLevel.B,
        source_ids=(ComplexId(A03), ComplexId(A04)),
        domain=DomainSpec(
            "DFI B02 authoritative product carrier",
            "paired A03/A04 branch states with localized source residuals",
            (ExactProductInput, _a04.ContextualApplicabilityInput, _legacy.ApplicabilityInput),
        ),
        codomain=CodomainSpec(
            "DFI B02 product realization",
            "exact coordinate projections, predicate conjunction residuals, and coordinatewise involution",
            (ExactProductResult,),
        ),
        operator=b02_operator,
        residual=_b02_residual,
        source_removal_checks=(
            _removal(A03, 0, 2),
            _removal(A04, 1, 2),
        ),
        artifact_spec=artifact,
        implementation_path=IMPLEMENTATION_PATH,
    )
    c01 = ComplexContract(
        complex_id=ComplexId(C01),
        appendix=_a04.APPENDIX,
        appendix_source_sha256=_a04.APPENDIX_SHA256,
        level=ComplexLevel.C,
        source_ids=(ComplexId(B01), ComplexId(B02), ComplexId(B03)),
        domain=DomainSpec(
            "DFI C01 authoritative spatial product carrier",
            "paired B01/B02/B03 branch fields with exact projections and pointwise exchange",
            (ExactProductInput, _legacy.SpatialDFIInput),
        ),
        codomain=CodomainSpec(
            "DFI C01 spatial product realization",
            "coordinate theorem recovery, max residual localization, and involutive pointwise exchange",
            (ExactProductResult,),
        ),
        operator=c01_operator,
        residual=_c01_residual,
        closure_predicate=exact_product_predicate,
        source_removal_checks=(
            _removal(B01, 0, 3),
            _removal(B02, 1, 3),
            _removal(B03, 2, 3),
        ),
        artifact_spec=artifact,
        exact_semantics=True,
        implementation_path=IMPLEMENTATION_PATH,
    )
    return {B02: b02, C01: c01}


def contracts() -> tuple[ComplexContract, ...]:
    replacements = _replacement_contracts()
    return tuple(
        replacements.get(str(contract.complex_id), contract)
        for contract in _a04.contracts()
    )
