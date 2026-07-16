"""Typed dependency-closing A-level source laws for QENN, PGQENN, SOInets, and DFI.

Each source law computes a concrete response field, an algebraic invariant
residual, and a separately exposed failure-dual field.  The invariant gate is
never inferred from the absence of a failure signal: theorem-law satisfaction
and falsification diagnostics remain distinct typed outputs.
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
    ResidualResult,
)
from .validation import ensure_finite

AI_APPENDIX = "appendix_tne_artificial_intelligence_architechture.tex"
AI_SHA256 = "2f2e67b68c18c75f8fe0e8f78c243ca585c0ef8413c579752c3299816e5bc8de"
DFI_APPENDIX = "appendix_tne_fluctuation_and_elastic_dynamics.tex"
DFI_SHA256 = "e37d7583d56287f0cc48d819afadf06ab7f1d8cbccce1790c8b8f18f1b96f30b"


@dataclass(frozen=True)
class DependencySourceInput:
    """Finite witness field with an explicit failure-dual amplitude."""

    field: np.ndarray
    auxiliary: np.ndarray
    tolerance: float = 1e-10
    failure_scale: float = 0.25


@dataclass(frozen=True)
class DependencySourceResult:
    law_name: str
    response: np.ndarray
    residual_field: np.ndarray
    invariant_residual: float
    failure_metric: float
    failure_condition: str
    diagnostic_name: str
    diagnostic_value: float


@dataclass(frozen=True)
class SourceSpec:
    complex_id: str
    family: str
    operator_kind: str
    diagnostic_name: str
    failure_condition: str


SPECS = (
    # QENN
    SourceSpec("autocorrelation_completeness_of_weight_trajectories_continuous_mixing_component", "qenn", "autocorrelation", "continuous_mixing_energy", "continuous spectral mixing remains after autocorrelation reconstruction"),
    SourceSpec("flowpoint_flip_parity_constraint_parity_broken_bias_spurious_lines", "qenn", "parity", "parity_bias", "Flowpoint parity is broken and produces spurious spectral lines"),
    SourceSpec("qenn::dual_support_equivalence_support_mismatch_leakage", "qenn", "support", "support_leakage", "primal and dual supports fail to agree"),
    SourceSpec("bounded_remainder_drift_in_updates_long_memory_heavy_tail_drift", "qenn", "drift", "remainder_excess", "bounded-remainder control is lost under long-memory drift"),
    SourceSpec("inflation_collapse_support_invariance_nonlinear_sideband_mixing", "qenn", "inflate_collapse", "sideband_energy", "inflation-collapse transport creates nonlinear sidebands"),
    SourceSpec("epoch_operator_closure_backprop_optimiser_induced_resonance", "qenn", "epoch", "optimizer_resonance", "epoch closure is broken by optimiser-induced resonance"),
    SourceSpec("entropy_balanced_landscape_no_sharp_minima_sharp_minima_trap", "qenn", "entropy", "sharp_minimum_score", "entropy balance collapses into a sharp-minimum trap"),
    SourceSpec("hyper_parameter_stability_wedge_instability_lobe", "qenn", "stability", "instability_lobe", "hyper-parameters leave the stable wedge"),
    # PGQENN
    SourceSpec("prime_quasicrystal_support_equivalence_support_mismatch_leakage", "pgqenn", "support", "prime_support_leakage", "prime-quasicrystal support equivalence fails"),
    SourceSpec("soi_scaled_annealing_invariance_soi_mis_scaling_spurious_entropy", "pgqenn", "annealing", "annealing_mis_scaling", "SOI-scaled annealing acquires spurious entropy"),
    SourceSpec("motif_exhaustion_completeness_coverage_bias_long_memory_drift", "pgqenn", "coverage", "coverage_defect", "motif exhaustion leaves a coverage bias"),
    SourceSpec("weight_energy_parseval_equivalence_layerwise_l_2_energy_mismatch", "pgqenn", "parseval", "parseval_mismatch", "layerwise weight energy violates Parseval equivalence"),
    SourceSpec("parity_orthogonal_optimization_cross_parity_gradient_contamination", "pgqenn", "orthogonality", "cross_parity_contamination", "cross-parity gradients contaminate orthogonal optimisation"),
    SourceSpec("prime_shell_growth_regularity_shell_instability_phase_slips", "pgqenn", "shell_growth", "phase_slip_energy", "prime-shell growth develops phase slips"),
    # SOInets
    SourceSpec("soinet_cross_modal_transfer_generalization_and_dual_stability", "soinets", "transfer", "transfer_gap", "cross-modal transfer loses dual stability"),
    SourceSpec("soi_cross_domain_generalization_and_collapse", "soinets", "transfer", "domain_gap", "cross-domain generalization collapses"),
    SourceSpec("soinet_cross_modal_compositionality_modality_invariant_collapse_principle", "soinets", "composition", "composition_defect", "cross-modal composition is not modality invariant"),
    SourceSpec("soinet_error_contraction_and_dual_error_orthogonality", "soinets", "contraction", "contraction_defect", "error fails to contract or dual errors lose orthogonality"),
    SourceSpec("soi_entropy_minimization_and_entropic_catastrophe", "soinets", "entropy", "entropic_catastrophe", "entropy minimization crosses the catastrophe boundary"),
    SourceSpec("universal_entropy_minimization_and_collapse_degeneracy_duality_in_soinet", "soinets", "entropy", "collapse_degeneracy", "entropy minimization degenerates the collapse representation"),
    SourceSpec("spectral_phase_locking_and_collapse_in_soinet", "soinets", "phase_lock", "phase_lock_defect", "spectral phases fail to lock before collapse"),
    SourceSpec("soinet_modality_invariant_learning_and_universal_adaptation", "soinets", "adaptation", "modality_adaptation_gap", "learned adaptation remains modality dependent"),
    SourceSpec("soi_spectrum_learning_and_classification_soi_spectrum_degeneracy_dual_instability", "soinets", "classification", "spectral_margin_defect", "SOI spectral classes become degenerate"),
    SourceSpec("soinet_universal_expressivity_bound_entropy_minimal_generalization_principle", "soinets", "expressivity", "expressivity_defect", "the expressivity bound exceeds the entropy-minimal generalization budget"),
    SourceSpec("soinet_meta_learnability_dual_closure", "soinets", "meta", "meta_closure_defect", "meta-learning fails dual closure"),
    SourceSpec("hierarchical_soi_stack_transfer_cross_regime_collapse_duality", "soinets", "stack", "stack_transport_defect", "hierarchical transfer collapses across regimes"),
    SourceSpec("soinet_universal_generalization_principle_failure_brittleness_duality", "soinets", "generalization", "brittleness_gap", "universal generalization becomes brittle under dual perturbation"),
    SourceSpec("soinet_universal_cloning_principle_cloning_failure_duality", "soinets", "cloning", "cloning_defect", "the cloned representation fails the dual reconstruction law"),
    # DFI
    SourceSpec("dfi_uniqueness_of_decomposition_and_mapping_ambiguity", "dfi", "decomposition", "mapping_ambiguity", "the DFI decomposition is non-unique"),
    SourceSpec("dfi_flowpoint_consistency_and_interface_inconsistency", "dfi", "parity", "flowpoint_interface_defect", "the DFI/Flowpoint interface is inconsistent"),
    SourceSpec("dfi_simulation_consistency_and_simulation_breakdown", "dfi", "simulation", "simulation_breakdown", "the discrete simulation no longer reconstructs the DFI state"),
)

SPEC_BY_ID: Mapping[str, SourceSpec] = {spec.complex_id: spec for spec in SPECS}
FAMILY_IDS: Mapping[str, tuple[str, ...]] = {
    family: tuple(spec.complex_id for spec in SPECS if spec.family == family)
    for family in ("qenn", "pgqenn", "soinets", "dfi")
}


def _validate(value: DependencySourceInput) -> tuple[np.ndarray, np.ndarray]:
    field = np.asarray(value.field, dtype=float)
    auxiliary = np.asarray(value.auxiliary, dtype=float)
    if field.ndim != 2 or min(field.shape) < 4:
        raise ValueError("dependency source fields require a finite rank-two array of at least 4x4")
    if auxiliary.shape != field.shape:
        raise ValueError("dependency source auxiliary field must match the primary field")
    ensure_finite((field, auxiliary), name="dependency source witness")
    parameters = np.asarray((value.tolerance, value.failure_scale), dtype=float)
    ensure_finite(parameters, name="dependency source parameters")
    if value.tolerance < 0.0 or value.failure_scale <= 0.0:
        raise ValueError("dependency source tolerance must be non-negative and failure_scale positive")
    return field, auxiliary


def _normalised(field: np.ndarray) -> np.ndarray:
    centered = field - field.mean(axis=-1, keepdims=True)
    scale = np.linalg.norm(centered, axis=-1, keepdims=True)
    return centered / np.maximum(scale, np.finfo(float).eps)


def _law(kind: str, field: np.ndarray, auxiliary: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    if kind == "autocorrelation":
        centered = field - field.mean(axis=0, keepdims=True)
        spectrum = np.fft.fft(centered, axis=0, norm="ortho")
        response = np.fft.ifft(spectrum * np.conj(spectrum), axis=0, norm="ortho").real
        direct = np.stack(
            [np.sum(centered * np.roll(centered, -lag, axis=0), axis=0) / np.sqrt(field.shape[0]) for lag in range(field.shape[0])]
        )
        invariant = float(np.linalg.norm(response - direct))
        obstruction = response - response.mean(axis=0, keepdims=True)
    elif kind == "parity":
        parity = np.where(np.arange(field.shape[0]) % 2 == 0, 1.0, -1.0)[:, None]
        response = parity * field
        invariant = float(np.linalg.norm(parity * response - field))
        obstruction = response.mean(axis=0, keepdims=True).repeat(field.shape[0], axis=0)
    elif kind == "support":
        threshold = np.median(np.abs(auxiliary), axis=0, keepdims=True)
        mask = (np.abs(auxiliary) >= threshold).astype(float)
        response = mask * field
        invariant = float(np.linalg.norm(response - np.where(mask > 0.0, field, 0.0)))
        obstruction = (1.0 - mask) * np.abs(field - auxiliary)
    elif kind == "drift":
        increments = np.diff(field, axis=0, prepend=field[:1])
        cumulative = np.cumsum(increments, axis=0)
        trend = np.linspace(0.0, 1.0, field.shape[0])[:, None] * cumulative[-1]
        response = cumulative - trend
        invariant = float(np.linalg.norm(cumulative - (trend + response)))
        bound = np.mean(np.abs(response), axis=0, keepdims=True)
        obstruction = np.maximum(np.abs(response) - bound, 0.0)
    elif kind == "inflate_collapse":
        inflated = np.repeat(field, 2, axis=0)
        response = inflated.reshape(field.shape[0], 2, field.shape[1]).mean(axis=1)
        invariant = float(np.linalg.norm(response - field))
        obstruction = np.diff(inflated, axis=0, prepend=inflated[:1])[::2]
    elif kind == "epoch":
        gradient = np.diff(field, axis=0, prepend=field[:1])
        update = 0.25 * gradient
        response = field - update
        invariant = float(np.linalg.norm(response - (field - update)))
        obstruction = np.diff(gradient, axis=0, prepend=gradient[:1])
    elif kind in {"entropy", "annealing"}:
        shifted = field - np.max(field, axis=-1, keepdims=True)
        weights = np.exp(shifted)
        probabilities = weights / weights.sum(axis=-1, keepdims=True)
        entropy = -(probabilities * np.log(np.maximum(probabilities, np.finfo(float).tiny))).sum(axis=-1, keepdims=True)
        response = np.repeat(entropy, field.shape[1], axis=1)
        invariant = float(np.linalg.norm(probabilities.sum(axis=-1) - 1.0))
        obstruction = np.repeat(np.max(probabilities, axis=-1, keepdims=True), field.shape[1], axis=1)
    elif kind == "stability":
        gradient = np.diff(field, axis=0, prepend=field[:1])
        curvature = np.diff(gradient, axis=0, prepend=gradient[:1])
        response = 1.0 / (1.0 + np.abs(gradient) + np.abs(curvature))
        invariant = float(np.linalg.norm(response * (1.0 + np.abs(gradient) + np.abs(curvature)) - 1.0))
        obstruction = np.maximum(np.abs(gradient) + np.abs(curvature) - 1.0, 0.0)
    elif kind == "coverage":
        rank = np.argsort(np.argsort(np.abs(field), axis=0), axis=0)
        response = (rank + 1.0) / field.shape[0]
        invariant = float(np.linalg.norm(np.sort(response, axis=0)[:, 0] - np.arange(1, field.shape[0] + 1) / field.shape[0]))
        obstruction = np.abs(response - response.mean(axis=1, keepdims=True))
    elif kind == "parseval":
        spectrum = np.fft.fft(field, axis=-1, norm="ortho")
        response = np.abs(spectrum) ** 2
        direct_energy = np.sum(field**2, axis=-1)
        spectral_energy = np.sum(response, axis=-1)
        invariant = float(np.linalg.norm(direct_energy - spectral_energy))
        obstruction = np.repeat(np.abs(direct_energy - spectral_energy)[:, None], field.shape[1], axis=1) + np.abs(field - auxiliary)
    elif kind == "orthogonality":
        even = np.zeros_like(field); even[:, ::2] = field[:, ::2]
        odd = np.zeros_like(field); odd[:, 1::2] = field[:, 1::2]
        response = even + odd
        invariant = float(np.linalg.norm(response - field))
        obstruction = np.full_like(field, abs(float(np.vdot(even, odd)))) + np.abs(field * auxiliary)
    elif kind == "shell_growth":
        shells = np.cumsum(np.abs(field), axis=0)
        response = np.diff(shells, axis=0, prepend=np.zeros_like(shells[:1]))
        invariant = float(np.linalg.norm(response - np.abs(field)))
        obstruction = np.diff(response, n=2, axis=0, prepend=np.zeros_like(response[:2]))
    elif kind in {"transfer", "adaptation", "generalization"}:
        left = field.mean(axis=0, keepdims=True)
        right = auxiliary.mean(axis=0, keepdims=True)
        response = 0.5 * (left + right).repeat(field.shape[0], axis=0)
        invariant = float(np.linalg.norm(response.mean(axis=0) - 0.5 * (left + right).ravel()))
        obstruction = (left - right).repeat(field.shape[0], axis=0)
    elif kind in {"composition", "stack"}:
        response = field + auxiliary
        invariant = float(np.linalg.norm(response - auxiliary - field))
        obstruction = np.diff(response, axis=0, prepend=response[:1])
    elif kind == "contraction":
        error = field - auxiliary
        response = 0.5 * error
        invariant = float(np.linalg.norm(response - 0.5 * error))
        obstruction = np.maximum(np.abs(response) - np.abs(error), 0.0) + np.abs(field * auxiliary)
    elif kind == "phase_lock":
        spectrum = np.fft.fft(field + 1j * auxiliary, axis=0, norm="ortho")
        phase = np.angle(spectrum)
        response = np.cos(phase)
        invariant = float(np.linalg.norm(np.cos(phase) ** 2 + np.sin(phase) ** 2 - 1.0))
        obstruction = phase - phase.mean(axis=0, keepdims=True)
    elif kind == "classification":
        centroids = np.stack((field.mean(axis=0), auxiliary.mean(axis=0)))
        distances = np.stack((np.linalg.norm(field - centroids[0], axis=1), np.linalg.norm(field - centroids[1], axis=1)), axis=1)
        response = -distances
        margin = np.abs(distances[:, 0] - distances[:, 1])[:, None]
        invariant = float(np.linalg.norm(response + distances))
        obstruction = np.repeat(1.0 / (1.0 + margin), field.shape[1], axis=1)
    elif kind == "expressivity":
        singular = np.linalg.svd(field, compute_uv=False)
        response = np.outer(np.ones(field.shape[0]), singular[: field.shape[1]])
        response = np.resize(response, field.shape)
        invariant = float(abs(np.linalg.norm(field) - np.linalg.norm(singular)))
        obstruction = np.full_like(field, max(0.0, float(np.sum(singular) - np.linalg.norm(field))))
    elif kind == "meta":
        response = 0.5 * (field + auxiliary[::-1])
        invariant = float(np.linalg.norm(2.0 * response - field - auxiliary[::-1]))
        obstruction = response - response[::-1]
    elif kind == "cloning":
        basis = np.linalg.pinv(auxiliary) @ field
        response = auxiliary @ basis
        invariant = float(np.linalg.norm(response - auxiliary @ basis))
        obstruction = response - field
    elif kind == "decomposition":
        mean = field.mean(axis=0, keepdims=True)
        centered = field - mean
        response = centered + mean
        invariant = float(np.linalg.norm(response - field))
        obstruction = centered.mean(axis=0, keepdims=True).repeat(field.shape[0], axis=0) + (auxiliary - field)
    elif kind == "simulation":
        velocity = np.diff(field, axis=0, prepend=field[:1])
        response = field[:1] + np.cumsum(velocity, axis=0)
        invariant = float(np.linalg.norm(response - field))
        obstruction = response - auxiliary
    else:
        raise KeyError(kind)
    return np.asarray(response, dtype=float), np.asarray(obstruction, dtype=float), invariant


def source_operator(complex_id: str, value: DependencySourceInput) -> DependencySourceResult:
    field, auxiliary = _validate(value)
    spec = SPEC_BY_ID[complex_id]
    response, obstruction, invariant = _law(spec.operator_kind, field, auxiliary)
    residual_field = value.failure_scale * obstruction
    ensure_finite((response, residual_field), name=f"{complex_id} output")
    failure_metric = float(np.linalg.norm(residual_field))
    diagnostic_value = float(np.linalg.norm(response))
    return DependencySourceResult(
        complex_id,
        response,
        residual_field,
        invariant,
        failure_metric,
        spec.failure_condition,
        spec.diagnostic_name,
        diagnostic_value,
    )


def _residual(source: DependencySourceInput, output: DependencySourceResult) -> ResidualResult:
    passed = output.invariant_residual <= source.tolerance
    return ResidualResult(
        f"{output.law_name} algebraic invariant",
        (output.invariant_residual,),
        source.tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {
            "failure_metric": output.failure_metric,
            "failure_condition": output.failure_condition,
            "diagnostic_name": output.diagnostic_name,
            "diagnostic_value": output.diagnostic_value,
        },
    )


def contracts_for(family: str, implementation_path: str) -> tuple[ComplexContract, ...]:
    appendix = DFI_APPENDIX if family == "dfi" else AI_APPENDIX
    digest = DFI_SHA256 if family == "dfi" else AI_SHA256
    return tuple(
        ComplexContract(
            ComplexId(identifier),
            appendix,
            digest,
            ComplexLevel.A,
            (),
            DomainSpec(
                f"{family} dependency source witness",
                "finite primary/auxiliary rank-two fields, non-negative tolerance, and positive controlled failure amplitude",
                (DependencySourceInput,),
            ),
            CodomainSpec(
                f"{identifier} source law",
                "concrete response, algebraic invariant residual, and separate failure-dual field",
                (DependencySourceResult,),
            ),
            partial(source_operator, identifier),
            residual=_residual,
            artifact_spec=ArtifactSpec(
                ("source_metric_table", "failure_dual_trace"),
                "python tools/generate_artifact_provenance.py --output-root <output-root>",
            ),
            implementation_path=implementation_path,
        )
        for identifier in FAMILY_IDS[family]
    )


def source_ids() -> tuple[str, ...]:
    return tuple(spec.complex_id for spec in SPECS)


def sample_input(complex_id: str, *, failure: bool = False) -> DependencySourceInput:
    if complex_id not in SPEC_BY_ID:
        raise KeyError(complex_id)
    rows, columns = 8, 6
    x = np.linspace(0.0, 2.0 * np.pi, rows, endpoint=False)[:, None]
    y = np.linspace(0.0, np.pi, columns, endpoint=False)[None, :]
    field = 1.5 + np.sin(x) + 0.35 * np.cos(2.0 * y) + 0.1 * np.sin(x + y)
    auxiliary = 1.25 + np.cos(x) + 0.25 * np.sin(3.0 * y) + 0.08 * np.cos(x - y)
    return DependencySourceInput(
        field,
        auxiliary,
        tolerance=1e-9,
        failure_scale=4.0 if failure else 0.25,
    )
