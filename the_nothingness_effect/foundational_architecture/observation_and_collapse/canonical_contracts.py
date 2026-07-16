"""Canonical executable Observation-and-Collapse contract registry."""

from __future__ import annotations

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ArtifactSpec,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    source_removal_result,
)

from ._canonical_core import *  # noqa: F401,F403
from ._canonical_core import APPENDIX, APPENDIX_SHA256, IMPLEMENTATION, _residual
from ._canonical_derived import *  # noqa: F401,F403
from ._canonical_derived import (
    _temporal_complete,
    remove_b1_closure,
    remove_b1_instrument,
    remove_b2_definiteness,
    remove_b2_ergodic,
    remove_b2_projection,
    remove_b3_convergence,
    remove_b3_stability,
    remove_b4_definiteness,
    remove_b4_ergodic,
    remove_b4_projection,
    remove_c1,
    remove_c2,
    remove_c3,
    remove_c4,
)


def _remove_temporal_uniqueness(value: TemporalCompressionInput):
    complete = _temporal_complete(value)
    return source_removal_result(
        A3,
        complete,
        np.zeros_like(complete),
        tolerance=value.tolerance,
    )


def _remove_field_pinning(value: OutcomeFieldInput):
    output = closure_conditioned_outcome_field(value)
    projector_block = np.concatenate(
        tuple(np.abs(item).ravel() for item in output.sector_projectors)
    )
    support_block = np.concatenate(
        tuple(item.astype(float) for item in output.closed_supports)
    )
    complete = np.concatenate(
        (output.probabilities, projector_block, support_block)
    )
    removed = complete.copy()
    start = len(output.probabilities)
    removed[start : start + len(projector_block)] = 0.0
    return source_removal_result(
        B2,
        complete,
        removed,
        tolerance=value.tolerance,
    )


def _contract(
    identifier: ComplexId,
    level: ComplexLevel,
    sources: tuple[ComplexId, ...],
    input_type: type,
    output_type: type,
    operator,
    residual_fields: tuple[str, ...],
    removal_checks=(),
    *,
    closed: bool = False,
) -> ComplexContract:
    artifact = ArtifactSpec(
        ("json", "csv"),
        "python tools/generate_artifact_provenance.py --output-root <output-root>",
    )
    return ComplexContract(
        identifier,
        APPENDIX,
        APPENDIX_SHA256,
        level,
        sources,
        DomainSpec(
            str(identifier),
            "typed finite witness for the authoritative observation law",
            (input_type,),
        ),
        CodomainSpec(
            str(identifier),
            "finite operator certificate, obstruction residuals, and closure data",
            (output_type,),
        ),
        operator,
        residual=lambda source, output: _residual(
            str(identifier),
            tuple(getattr(output, field) for field in residual_fields),
            source.tolerance,
        ),
        closure_predicate=(
            (lambda _output, residual: residual is not None and residual.passed)
            if closed
            else None
        ),
        source_removal_checks=tuple(removal_checks),
        artifact_spec=artifact,
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )


def contracts() -> tuple[ComplexContract, ...]:
    return (
        _contract(A1, ComplexLevel.A, (), MeanErgodicInput, MeanErgodicLaw, mean_ergodic_collapse, ("operator_involution_residual", "fixed_residual", "convergence_residual", "cauchy_residual")),
        _contract(A2, ComplexLevel.A, (), AttractorInput, AttractorLaw, attractor_stability, ("zero_mean_residual", "attractor_residual", "stability_bound_residual")),
        _contract(A3, ComplexLevel.A, (), UniquenessInput, UniquenessLaw, uniqueness_classification, ("pathwise_residual", "singleton_residual", "ensemble_residual")),
        _contract(A4, ComplexLevel.A, (), MeanErgodicInput, ProjectionLaw, hilbert_projection, ("involution_residual", "unitary_residual", "idempotence_residual", "orthogonality_residual", "convergence_residual")),
        _contract(A5, ComplexLevel.A, (), ClosureInput, ClosureLaw, closure_consistency, ("monotonicity_residual", "extensivity_residual", "idempotence_residual", "output_fixed_residual")),
        _contract(A6, ComplexLevel.A, (), StabilizationInput, StabilizationLaw, stabilization_classification, ("output_fixed_residual", "eventual_idempotence_residual", "partition_residual")),
        _contract(A7, ComplexLevel.A, (), InstrumentInput, InstrumentLaw, instrument_realization, ("completeness_residual", "orthogonality_residual", "probability_residual", "repeatability_residual", "state_normalization_residual")),
        _contract(A8, ComplexLevel.A, (), MeanErgodicInput, ErgodicProjectionLaw, ergodic_projection, ("involution_residual", "idempotence_residual", "fixed_range_residual", "orthogonality_residual", "convergence_residual")),
        _contract(B1, ComplexLevel.B, (A5, A7), OutcomeClosureInput, OutcomeClosureLaw, outcome_conditioned_closure, ("idempotence_residual", "support_residual", "repeatability_residual", "normalization_residual"), (remove_b1_closure, remove_b1_instrument)),
        _contract(B2, ComplexLevel.B, (A4, A8, A6), SpectralCollapseInput, SpectralPinningLaw, spectral_pinning, ("involution_residual", "projector_residual", "orthogonality_residual", "pinning_residual", "drift_residual"), (remove_b2_projection, remove_b2_ergodic, remove_b2_definiteness)),
        _contract(B3, ComplexLevel.B, (A1, A2, A3), TemporalCompressionInput, TemporalCompressionLaw, temporal_compression, ("convergence_residual", "common_limit_residual", "compression_residual", "cauchy_residual"), (remove_b3_convergence, remove_b3_stability, _remove_temporal_uniqueness)),
        _contract(B4, ComplexLevel.B, (A4, A8, A6), SpectralCollapseInput, SpectralSelectionLaw, spectral_selection, ("projection_residual", "selection_residual", "multiplier_residual", "preparation_residual"), (remove_b4_projection, remove_b4_ergodic, remove_b4_definiteness)),
        _contract(C1, ComplexLevel.C, (B2, B4), DimensionalBindingInput, DimensionalBindingLaw, dimensional_binding, ("commutator_residual", "projector_residual", "fixed_core_residual", "composition_residual"), (lambda value: remove_c1(value, B2, "pinning"), lambda value: remove_c1(value, B4, "selection")), closed=True),
        _contract(C2, ComplexLevel.C, (B3, B4), LocalityInput, LocalityLaw, observable_locality, ("localization_residual", "temporal_residual", "spectral_residual", "support_residual"), (lambda value: remove_c2(value, B3, "temporal"), lambda value: remove_c2(value, B4, "spectral")), closed=True),
        _contract(C3, ComplexLevel.C, (B3, B4), HorizonInput, HorizonLaw, local_horizon, ("tail_residual", "tightness_residual", "horizon_residual", "leakage_residual"), (lambda value: remove_c3(value, B3, "temporal"), lambda value: remove_c3(value, B4, "spectral")), closed=True),
        _contract(C4, ComplexLevel.C, (B1, B2, B4), OutcomeFieldInput, OutcomeFieldLaw, closure_conditioned_outcome_field, ("commutator_residual", "orthogonality_residual", "reconstruction_residual", "idempotence_residual", "closure_residual"), (lambda value: remove_c4(value, B1, "closure"), _remove_field_pinning, lambda value: remove_c4(value, B4, "selection")), closed=True),
    )
