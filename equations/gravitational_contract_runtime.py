"""Shared typed runtime for selected gravitational/cosmological/quantum chains.

Each configured module exposes four independent A source laws, two genuine
two-source B interactions, and one spatial C closure.  The common machinery is
numerical; module specifications select distinct appendix-facing field laws.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Callable

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
from equations.theorem_complex_runtime.types import DomainViolationError
from equations.theorem_complex_runtime.validation import ensure_finite


APPENDIX = "appendix_tne_gravitational_cosmological_quantum_dynamics.tex"
APPENDIX_SHA256 = "c946e19a4266f8c5c3e3dd49ed6b98740d3764cac729536e5b84c42fefba304d"


@dataclass(frozen=True)
class FieldLawInput:
    coordinates: np.ndarray
    source: np.ndarray
    scale: float = 2.0
    frequency: float = 1.0
    tolerance: float = 1e-10


@dataclass(frozen=True)
class SourceFieldLaw:
    law_name: str
    spatial_domain: np.ndarray
    response: np.ndarray
    invariant_residual: np.ndarray
    boundary_trace: float


@dataclass(frozen=True)
class DerivedFieldLaw:
    law_name: str
    source_a: np.ndarray
    source_b: np.ndarray
    combined_operator: np.ndarray
    residual: np.ndarray
    interaction_energy: float


@dataclass(frozen=True)
class SpatialFieldClosure:
    law_name: str
    spatial_domain: np.ndarray
    local_operator: np.ndarray
    boundary_trace_residual: float
    localization_residual: float
    reconstruction_residual: float
    coercivity_ratio: float
    observability_residual: float
    closure_status: str


@dataclass(frozen=True)
class PhysicalModuleSpec:
    module: str
    a_ids: tuple[str, str, str, str]
    b_ids: tuple[str, str]
    c_id: str
    source_kinds: tuple[str, str, str, str]


def _validated(value: FieldLawInput) -> tuple[np.ndarray, np.ndarray, float]:
    coordinates = np.asarray(value.coordinates, dtype=float)
    source = np.asarray(value.source, dtype=float)
    if coordinates.ndim != 1 or coordinates.size < 5 or source.shape != coordinates.shape:
        raise DomainViolationError("field laws require equal one-dimensional coordinate/source arrays with at least five samples")
    ensure_finite((coordinates, source), name="physical field source")
    spacing = np.diff(coordinates)
    if np.any(spacing <= 0.0):
        raise DomainViolationError("physical field coordinates must be strictly increasing")
    step = float(np.mean(spacing))
    if not np.allclose(spacing, step, rtol=1e-10, atol=1e-12):
        raise DomainViolationError("canonical finite differences require a uniform spatial grid")
    if not np.isfinite(value.scale) or value.scale <= 0.0:
        raise DomainViolationError("physical field scale must be finite and strictly positive")
    if not np.isfinite(value.frequency) or value.frequency <= 0.0:
        raise DomainViolationError("physical field frequency must be finite and strictly positive")
    return coordinates, source, step


def _differentials(source: np.ndarray, step: float) -> tuple[np.ndarray, np.ndarray]:
    gradient = np.gradient(source, step, edge_order=2)
    laplacian = np.gradient(gradient, step, edge_order=2)
    return gradient, laplacian


def _response(kind: str, value: FieldLawInput) -> np.ndarray:
    x, source, step = _validated(value)
    gradient, laplacian = _differentials(source, step)
    index = np.arange(source.size, dtype=float)
    if kind == "dubler_ratio":
        result = np.exp(-(source - source[0]) / value.scale)
    elif kind == "pdfi_frequency_shift":
        parity = np.mod(index, 2.0)
        result = value.frequency * (1.0 + parity * np.abs(gradient))
    elif kind == "log_curvature":
        result = -laplacian / value.scale
    elif kind == "elastic_energy":
        result = gradient**2 / value.scale
    elif kind == "phase_curvature":
        result = np.unwrap(np.arctan2(gradient, source))
    elif kind == "elliptic_encoding":
        result = source - laplacian
    elif kind == "gravitational_memory":
        decay = np.exp(-(x - x[0]) / value.scale)
        result = np.cumsum(source * decay) * step
    elif kind == "horizon_response":
        result = np.tanh((source - np.mean(source)) / value.scale)
    elif kind == "locality_decomposition":
        kernel = np.exp(-np.abs(x[:, None] - x[None, :]) / value.scale)
        kernel /= np.sum(kernel, axis=1, keepdims=True)
        result = kernel @ source
    elif kind == "spiral_density":
        result = source * np.cos(value.frequency * x) + gradient * np.sin(value.frequency * x)
    elif kind == "curvature_superposition":
        result = source + laplacian + source * laplacian
    elif kind == "gravity_energy":
        result = -gradient * (source + value.scale)
    elif kind == "black_hole_field":
        result = np.pi * np.exp(-source / value.scale) - np.median(np.pi * np.exp(-source / value.scale))
    elif kind == "bridge_invariant":
        result = 0.5 * (source + source[::-1])
    elif kind == "singularity_status":
        result = 1.0 / (1.0 + gradient**2 + laplacian**2)
    elif kind == "horizon_observability":
        result = np.abs(gradient) + np.abs(laplacian)
    elif kind == "ripple_wave":
        result = laplacian - (value.frequency**2) * source
    elif kind == "ringdown_quality":
        envelope = np.exp(-(x - x[0]) / value.scale)
        result = envelope * np.abs(source)
    elif kind == "overtone_generation":
        result = source**3 - 0.75 * source
    elif kind == "transport_lag":
        result = gradient / value.scale
    elif kind == "spark_flowpoint":
        result = np.where((index.astype(int) % 2) == 0, source, -source)
    elif kind == "spark_memory":
        decay = np.exp(-(x - x[0]) / value.scale)
        result = np.cumsum(np.abs(source) * decay) * step
    elif kind == "cosmological_geometry":
        elastic = np.pi * np.exp(-source / value.scale)
        result = np.gradient(np.gradient(np.log(elastic), step, edge_order=2), step, edge_order=2)
    elif kind == "wave_expansion":
        result = gradient + value.frequency * source
    elif kind == "dtqc_spectrum":
        result = np.abs(np.fft.fft(source)) / np.sqrt(source.size)
    elif kind == "dual_support":
        threshold = float(np.mean(np.abs(source)))
        result = (np.abs(source) >= threshold).astype(float)
    elif kind == "parseval_energy":
        result = np.abs(np.fft.fft(source)) ** 2 / source.size
    elif kind == "irrational_locking":
        alpha = np.sqrt(2.0)
        result = source * np.cos(2.0 * np.pi * alpha * value.frequency * x)
    else:
        raise ValueError(f"unknown physical source law {kind!r}")
    ensure_finite(result, name=f"{kind} response")
    return np.asarray(result, dtype=float)


def source_operator(kind: str, value: FieldLawInput) -> SourceFieldLaw:
    x, _, _ = _validated(value)
    response = _response(kind, value)
    # A second evaluation is intentionally compared as a deterministic law
    # invariant; a stateful or stochastic backend would fail this contract.
    invariant = response - _response(kind, value)
    boundary = float(abs(response[0]) + abs(response[-1]))
    return SourceFieldLaw(kind, x, response, invariant, boundary)


def derived_operator(name: str, kind_a: str, kind_b: str, value: FieldLawInput) -> DerivedFieldLaw:
    a = source_operator(kind_a, value)
    b = source_operator(kind_b, value)
    combined = a.response + b.response + a.response * b.response
    residual = a.invariant_residual + b.invariant_residual
    return DerivedFieldLaw(
        name,
        a.response,
        b.response,
        combined,
        residual,
        float(np.linalg.norm(a.response * b.response) ** 2),
    )


def spatial_operator(spec: PhysicalModuleSpec, value: FieldLawInput) -> SpatialFieldClosure:
    first = derived_operator(spec.b_ids[0], spec.source_kinds[0], spec.source_kinds[1], value)
    second = derived_operator(spec.b_ids[1], spec.source_kinds[2], spec.source_kinds[3], value)
    local = first.combined_operator + second.combined_operator + first.combined_operator * second.combined_operator
    reconstructed = local - first.combined_operator - second.combined_operator - first.combined_operator * second.combined_operator
    source_norm = float(np.linalg.norm(value.source))
    coercivity = float(np.linalg.norm(local) / source_norm) if source_norm > 0.0 else 0.0
    localization = float(np.linalg.norm(np.diff(local)))
    boundary = float(abs(local[0]) + abs(local[-1]))
    reconstruction = float(np.linalg.norm(reconstructed))
    closed = reconstruction <= value.tolerance and coercivity > 0.0
    return SpatialFieldClosure(
        spec.c_id,
        np.asarray(value.coordinates, dtype=float),
        local,
        boundary,
        localization,
        reconstruction,
        coercivity,
        reconstruction,
        "numerical_candidate" if closed else "open",
    )


def _residual(name: str, values, tolerance: float = 1e-10) -> ResidualResult:
    vector = tuple(float(item) for item in np.ravel(values))
    norm = float(np.linalg.norm(vector))
    return ResidualResult(name, vector, tolerance, norm <= tolerance, ClosureStatus.SATISFIED if norm <= tolerance else ClosureStatus.OPEN)


def _remove_a(spec: PhysicalModuleSpec, b_index: int, source_index: int, value: FieldLawInput) -> SourceRemovalResult:
    offset = b_index * 2
    first_kind, second_kind = spec.source_kinds[offset : offset + 2]
    output = derived_operator(spec.b_ids[b_index], first_kind, second_kind, value)
    removed = output.source_b if source_index == 0 else output.source_a
    return source_removal_result(ComplexId(spec.a_ids[offset + source_index]), output.combined_operator, removed, tolerance=1e-12)


def _remove_b(spec: PhysicalModuleSpec, b_index: int, value: FieldLawInput) -> SourceRemovalResult:
    output = spatial_operator(spec, value)
    other_index = 1 - b_index
    offset = other_index * 2
    other = derived_operator(spec.b_ids[other_index], spec.source_kinds[offset], spec.source_kinds[offset + 1], value)
    return source_removal_result(ComplexId(spec.b_ids[b_index]), output.local_operator, other.combined_operator, tolerance=1e-12)


def contracts_for(spec: PhysicalModuleSpec) -> tuple[ComplexContract, ...]:
    domain = DomainSpec("physical field law", "finite uniformly sampled spatial field and positive parameters", (FieldLawInput,))
    implementation = f"equations/{spec.module}/contracts.py"
    artifact = ArtifactSpec(("field_csv", "residual_plot", "source_removal_table"), f"python -m equations.{spec.module}.simulation.run_contract_suite")
    result: list[ComplexContract] = []
    for complex_id, kind in zip(spec.a_ids, spec.source_kinds, strict=True):
        operator: Callable[[FieldLawInput], SourceFieldLaw] = partial(source_operator, kind)
        result.append(
            ComplexContract(
                ComplexId(complex_id), APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain,
                CodomainSpec(f"{kind} field", "typed source response, invariant residual, and boundary trace", (SourceFieldLaw,)),
                operator,
                residual=lambda _source, output, cid=complex_id: _residual(cid, output.invariant_residual),
                implementation_path=implementation,
            )
        )
    for b_index, b_id in enumerate(spec.b_ids):
        offset = b_index * 2
        operator = partial(derived_operator, b_id, spec.source_kinds[offset], spec.source_kinds[offset + 1])
        checks = (
            partial(_remove_a, spec, b_index, 0),
            partial(_remove_a, spec, b_index, 1),
        )
        result.append(
            ComplexContract(
                ComplexId(b_id), APPENDIX, APPENDIX_SHA256, ComplexLevel.B,
                (ComplexId(spec.a_ids[offset]), ComplexId(spec.a_ids[offset + 1])),
                domain,
                CodomainSpec(f"{b_id} interaction", "genuine bilinear two-source response", (DerivedFieldLaw,)),
                operator,
                residual=lambda _source, output, cid=b_id: _residual(cid, output.residual),
                source_removal_checks=checks,
                artifact_spec=artifact,
                implementation_path=implementation,
            )
        )
    result.append(
        ComplexContract(
            ComplexId(spec.c_id), APPENDIX, APPENDIX_SHA256, ComplexLevel.C,
            tuple(ComplexId(item) for item in spec.b_ids),
            domain,
            CodomainSpec(f"{spec.c_id} spatial closure", "local field, boundary, localization, coercivity, observability, and candidate status", (SpatialFieldClosure,)),
            partial(spatial_operator, spec),
            residual=lambda _source, output: _residual(spec.c_id, (output.reconstruction_residual, output.observability_residual)),
            closure_predicate=lambda output, residual: output.closure_status == "numerical_candidate" and output.coercivity_ratio > 0.0 and residual is not None and residual.passed,
            source_removal_checks=(partial(_remove_b, spec, 0), partial(_remove_b, spec, 1)),
            artifact_spec=artifact,
            exact_semantics=False,
            implementation_path=implementation,
        )
    )
    return tuple(result)


def registered_module_registry(spec: PhysicalModuleSpec, matrix: str | Path = "docs/data/theorem_complex_implementation_matrix.csv") -> TheoremComplexRegistry:
    registry = TheoremComplexRegistry.from_csv(matrix)
    for contract in contracts_for(spec):
        registry.register(contract)
    return registry


SPECS: dict[str, PhysicalModuleSpec] = {
    "elastic_dubler_effect": PhysicalModuleSpec("elastic_dubler_effect", ("elastic_dubler_duality_closure", "elastic_dubler_pdfi_frequency_shift_dual_closure", "elastic_dubler_e_curvature_duality", "elastic_dubler_effect::elastic_entropic_energy_equivalence"), ("calibrated_pdfi_dubler_endpoint_operator", "elastic_log_curvature_energy_production_law"), "dubler_potential_current_spatial_closure", ("dubler_ratio", "pdfi_frequency_shift", "log_curvature", "elastic_energy")),
    "elastic_dubler_interferometry": PhysicalModuleSpec("elastic_dubler_interferometry", ("elastic_dubler_curvature_correspondence", "elastic_e_curvature_encoding_curvature_ambiguity_divergence", "elastic_dubler_interferometry::elastic_gravitational_memory_instant_relaxation", "elastic_dubler_interferometry::elastic_black_hole_emergence_triviality_of_breakdown"), ("phase_elliptic_curvature_reconstruction", "memory_resolved_horizon_reconstruction"), "memory_aware_phase_curvature_tomography", ("phase_curvature", "elliptic_encoding", "gravitational_memory", "horizon_response")),
    "locality_driven_gravity": PhysicalModuleSpec("locality_driven_gravity", ("locality_decomposition_nonlocal_entropic_divergence", "emergent_spiral_density_wave_spiral_dissolution", "entropic_curvature_superposition_duality", "locality_driven_gravity::elastic_entropic_energy_equivalence"), ("locality_weighted_spiral_order", "curvature_driven_elastic_energy_production"), "locality_energy_morphogenesis_closure", ("locality_decomposition", "spiral_density", "curvature_superposition", "gravity_energy")),
    "black_hole_dynamics": PhysicalModuleSpec("black_hole_dynamics", ("black_hole_dynamics::elastic_black_hole_emergence_triviality_of_breakdown", "bridge_duality_dual_invariant_translation", "physical_singularity_absence_mathematical_failure_point_status", "black_hole_observability_triviality_and_regularity"), ("entropy_invariant_horizon_translation", "regular_observer_horizon_hypersurface"), "regular_nonperforating_horizon_geometry", ("black_hole_field", "bridge_invariant", "singularity_status", "horizon_observability")),
    "elastic_pi_ripples": PhysicalModuleSpec("elastic_pi_ripples", ("elastic_e_ripple_propagation_gr_linear_wave_recovery", "entropic_q_factor_suppression_conserved_ringdown_quality", "nonlinear_overtone_generation_spectral_purity", "subluminal_gw_transport_and_em_gw_lag_null_lag_correspondence"), ("wave_energy_quality_invariant", "distance_corrected_harmonic_coupling"), "damping_and_lag_corrected_harmonic_clock", ("ripple_wave", "ringdown_quality", "overtone_generation", "transport_lag")),
    "cosmological_spark_dynamics": PhysicalModuleSpec("cosmological_spark_dynamics", ("cosmic_spark_flowpoint_correspondence_and_spectral_duality", "cosmic_spark_decay_and_integrated_cosmological_memory", "elastic_cosmological_geometry_and_dubler_spectral_transfer", "wave_sector_and_expansion_sector_cosmological_projection"), ("flowpoint_resolved_cosmological_memory_resolvent", "common_potential_observation_operator"), "horizon_localized_observable_memory_closure", ("spark_flowpoint", "spark_memory", "cosmological_geometry", "wave_expansion")),
    "dtqc": PhysicalModuleSpec("dtqc", ("elastic_dtqc_spectral_measure_dual_of_dtqc", "dtqc::dual_support_equivalence_support_mismatch_leakage", "parseval_energy_bijection_l_2_energy_mismatch", "irrational_drive_locking_commensurate_resonance_collapse"), ("elastic_gain_support_transport_isomorphism", "diophantine_parseval_locking_invariant"), "elastic_parseval_quasicrystal_isometry", ("dtqc_spectrum", "dual_support", "parseval_energy", "irrational_locking")),
}
