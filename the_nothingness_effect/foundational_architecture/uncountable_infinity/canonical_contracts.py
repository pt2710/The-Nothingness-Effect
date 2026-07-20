"""Canonical executable Uncountable-Infinity contract registry."""

from __future__ import annotations

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ArtifactSpec,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
)

from ._canonical_core import *  # noqa: F401,F403
from ._canonical_core import APPENDIX, APPENDIX_SHA256, IMPLEMENTATION, _residual
from ._canonical_derived import *  # noqa: F401,F403
from ._canonical_derived import (
    _b1_remove_a1,
    _b1_remove_a2,
    _b2_remove_a3,
    _b2_remove_a4,
    _b3_remove_a5,
    _b3_remove_a6,
    _b4_remove_a7,
    _b4_remove_a8,
    _b5_remove_a9,
    _b5_remove_a10,
    _c1_remove_b1,
    _c1_remove_b2,
    _c2_remove,
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
            "typed finite witness for the authoritative law",
            (input_type,),
        ),
        CodomainSpec(
            str(identifier),
            "finite exact law certificate and residuals",
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
        _contract(
            A1,
            ComplexLevel.A,
            (),
            TrajectoryInput,
            TrajectoryLaw,
            continuum_trajectory,
            ("trajectory_residual", "phase_residual", "coding_residual"),
        ),
        _contract(
            A2,
            ComplexLevel.A,
            (),
            PowerSetInput,
            PowerSetLaw,
            power_set_atomicity,
            ("characteristic_residual", "trajectory_residual", "atom_residual"),
        ),
        _contract(
            A3,
            ComplexLevel.A,
            (),
            DenseTraceInput,
            DenseTraceLaw,
            dense_trace,
            ("trace_residual", "quantization_residual", "nowhere_dense_residual"),
        ),
        _contract(
            A4,
            ComplexLevel.A,
            (),
            PrefixInput,
            PrefixLaw,
            cantor_prefix_universality,
            ("convergence_residual", "coherence_residual", "finite_resolution_residual"),
        ),
        _contract(
            A5,
            ComplexLevel.A,
            (),
            PrefixInput,
            FractalLaw,
            fractal_self_similarity,
            ("self_similarity_residual", "complement_residual", "depth_residual"),
        ),
        _contract(
            A6,
            ComplexLevel.A,
            (),
            PrefixInput,
            CompletionLaw,
            duality_completion,
            ("coherence_residual", "density_bound_residual", "decoder_residual"),
        ),
        _contract(
            A7,
            ComplexLevel.A,
            (),
            BooleanInput,
            BooleanLaw,
            boolean_completion,
            ("de_morgan_residual", "distributive_residual", "complement_residual"),
        ),
        _contract(
            A8,
            ComplexLevel.A,
            (),
            OperationalInput,
            OperationalLaw,
            operational_coarse_graining,
            ("factorization_residual", "extension_residual", "unresolved_residual"),
        ),
        _contract(
            A9,
            ComplexLevel.A,
            (),
            CoverageInput,
            CoverageLaw,
            adic_coverage,
            ("decoder_residual", "adic_residual", "collapse_residual"),
        ),
        _contract(
            A10,
            ComplexLevel.A,
            (),
            DualRepairInput,
            DualRepairLaw,
            dual_repair,
            ("involution_residual", "closure_residual", "repair_residual"),
        ),
        _contract(
            B1,
            ComplexLevel.B,
            (A1, A2),
            SuperpositionInput,
            SuperpositionLaw,
            binary_superposition,
            ("valuation_residual", "peak_decoder_residual", "translation_residual"),
            (_b1_remove_a1, _b1_remove_a2),
        ),
        _contract(
            B2,
            ComplexLevel.B,
            (A3, A4),
            PrefixInput,
            PrefixReconstructionLaw,
            prefix_tree_reconstruction,
            ("convergence_residual", "tower_coherence_residual", "decoder_residual"),
            (_b2_remove_a3, _b2_remove_a4),
        ),
        _contract(
            B3,
            ComplexLevel.B,
            (A5, A6),
            PrefixInput,
            FractalSkeletonLaw,
            fractal_skeleton_completion,
            ("completion_residual", "complement_residual", "exchange_residual"),
            (_b3_remove_a5, _b3_remove_a6),
        ),
        _contract(
            B4,
            ComplexLevel.B,
            (A7, A8),
            OperationalInput,
            DecisionConsensusLaw,
            boolean_decision_consensus,
            ("extension_residual", "consensus_residual", "involution_residual"),
            (_b4_remove_a7, _b4_remove_a8),
        ),
        _contract(
            B5,
            ComplexLevel.B,
            (A9, A10),
            AdicRepairInput,
            AdicRepairLaw,
            adic_domain_repair,
            ("canonical_residual", "coverage_residual", "dual_repair_residual"),
            (_b5_remove_a9, _b5_remove_a10),
        ),
        _contract(
            C1,
            ComplexLevel.C,
            (B1, B2),
            PrefixInput,
            EndFieldLaw,
            end_compactified_field,
            ("center_residual", "tail_residual", "convergence_residual"),
            (_c1_remove_b1, _c1_remove_b2),
            closed=True,
        ),
        _contract(
            C2,
            ComplexLevel.C,
            (B3, B4, B5),
            CoverageFieldInput,
            CoverageRepairFieldLaw,
            coverage_repair_field,
            (
                "real_coverage_residual",
                "klein_group_residual",
                "consensus_residual",
                "repair_residual",
            ),
            (
                lambda value: _c2_remove(value, B3, "fractal"),
                lambda value: _c2_remove(value, B4, "decision"),
                lambda value: _c2_remove(value, B5, "coverage"),
            ),
            closed=True,
        ),
    )
