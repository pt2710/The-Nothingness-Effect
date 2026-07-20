"""Typed finite contracts for the remaining Black-Hole Dynamics complexes.

The contracts expose executable residual witnesses for Hawking-like emission,
entropic relaxation, observer thresholds, and deformation memory. They do not
claim a GR/QFT derivation, physical black-hole realization, or empirical
validation.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import partial

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
    additive_derivation,
    boundary_leakage,
    coercivity_ratio,
    source_removal_result,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import DomainViolationError
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import ensure_finite

APPENDIX = "appendix_tne_gravitational_cosmological_quantum_dynamics.tex"
APPENDIX_SHA256 = "5cb9526f26767ca245f32a70a8f5a12138d374b3f4bb9821db155b9eece35062"
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
    "black_holes_hawking_radiation_and_observer_horizons/canonical_contracts.py"
)

A_IDS = (
    "elastic_hawking_emission_radiative_stasis",
    "hawking_radiation_as_entropic_relaxation_stasis",
    "observer_horizon_threshold_infinite_visibility",
    "black_hole_dynamics::elastic_gravitational_memory_instant_relaxation",
    "residual_deformation_memory_perfect_relaxation",
    "simulation_consistency_breakdown_and_non_equivalence",
    "appendix_wide_black_hole_hawking_observer_horizon_cross_complex_closure_and_computational_falsificat",
)
B_SPECS = (
    ("spatiotemporal_hawking_flux_density", (A_IDS[0], A_IDS[1])),
    ("observer_accessible_curvature_memory", (A_IDS[2], A_IDS[3])),
    ("certified_residual_memory_lower_bound", (A_IDS[4], A_IDS[5])),
)
C_ID = "observable_hawking_memory_certification"


@dataclass(frozen=True)
class BlackHoleInput:
    coordinate: np.ndarray
    entropy: np.ndarray
    mass: np.ndarray
    hawking_flux: np.ndarray
    relaxation_flux: np.ndarray
    observer_signal: np.ndarray
    visibility: np.ndarray
    deformation: np.ndarray
    gravitational_memory: np.ndarray
    residual_memory: np.ndarray
    simulation: np.ndarray
    reference: np.ndarray
    consistency_witness: np.ndarray
    elasticity: float
    observer_threshold: float
    tolerance: float = 1e-10


@dataclass(frozen=True)
class BlackHoleLaw:
    law_name: str
    response: np.ndarray
    residual: np.ndarray
    obstruction: float
    boundary_trace: float
    status: str


@dataclass(frozen=True)
class BlackHoleSynthesis:
    law_name: str
    source_responses: tuple[np.ndarray, ...]
    combined_operator: np.ndarray
    residual: np.ndarray
    interaction_energy: float
    status: str


@dataclass(frozen=True)
class BlackHoleSpatialClosure:
    law_name: str
    source_responses: tuple[np.ndarray, ...]
    local_field: np.ndarray
    boundary_residual: float
    reconstruction_residual: float
    localization_residual: float
    coercivity: float
    status: str


def _validated(value: BlackHoleInput) -> tuple[np.ndarray, ...]:
    arrays = tuple(
        np.asarray(item, dtype=float)
        for item in (
            value.coordinate,
            value.entropy,
            value.mass,
            value.hawking_flux,
            value.relaxation_flux,
            value.observer_signal,
            value.visibility,
            value.deformation,
            value.gravitational_memory,
            value.residual_memory,
            value.simulation,
            value.reference,
            value.consistency_witness,
        )
    )
    coordinate = arrays[0]
    if coordinate.ndim != 1 or coordinate.size < 5:
        raise DomainViolationError("Black-Hole contracts require at least five ordered samples")
    if any(item.shape != coordinate.shape for item in arrays[1:]):
        raise DomainViolationError("all Black-Hole fields must share the coordinate shape")
    ensure_finite(arrays, name="Black-Hole input")
    spacing = np.diff(coordinate)
    if np.any(spacing <= 0.0):
        raise DomainViolationError("Black-Hole coordinates must be strictly increasing")
    step = float(np.mean(spacing))
    if not np.allclose(spacing, step, rtol=1e-10, atol=1e-12):
        raise DomainViolationError("finite Black-Hole witnesses require a uniform grid")
    if np.any(arrays[2] <= 0.0):
        raise DomainViolationError("mass samples must be strictly positive")
    if any(np.any(item < 0.0) for item in (arrays[3], arrays[4], arrays[6], arrays[8], arrays[9])):
        raise DomainViolationError("flux, visibility, and memory magnitudes must be non-negative")
    if np.any((arrays[6] < 0.0) | (arrays[6] > 1.0)):
        raise DomainViolationError("visibility must lie in [0,1]")
    if not np.isfinite(value.elasticity) or value.elasticity <= 0.0:
        raise DomainViolationError("elasticity must be finite and strictly positive")
    if not np.isfinite(value.observer_threshold):
        raise DomainViolationError("observer threshold must be finite")
    if not np.isfinite(value.tolerance) or value.tolerance < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    return (*arrays, np.asarray(step))


def _law(law_id: str, value: BlackHoleInput) -> BlackHoleLaw:
    (
        coordinate,
        entropy,
        mass,
        hawking_flux,
        relaxation_flux,
        observer_signal,
        visibility,
        deformation,
        gravitational_memory,
        residual_memory,
        simulation,
        reference,
        consistency_witness,
        step_array,
    ) = _validated(value)
    step = float(step_array)
    if law_id == A_IDS[0]:
        response = np.exp(-entropy / value.elasticity) / mass**2
        residual = hawking_flux - response
    elif law_id == A_IDS[1]:
        response = np.maximum(-np.gradient(entropy, step, edge_order=2), 0.0)
        residual = relaxation_flux - response
    elif law_id == A_IDS[2]:
        response = 1.0 / (1.0 + np.exp(-(observer_signal - value.observer_threshold) / value.elasticity))
        residual = visibility - response
    elif law_id == A_IDS[3]:
        decay = np.exp(-(coordinate - coordinate[0]) / value.elasticity)
        response = np.cumsum(np.abs(deformation) * decay) * step
        residual = gravitational_memory - response
    elif law_id == A_IDS[4]:
        response = np.abs(deformation) * np.exp(-(coordinate - coordinate[0]) / value.elasticity)
        residual = residual_memory - response
    elif law_id == A_IDS[5]:
        response = simulation - reference
        residual = consistency_witness - response
    elif law_id == A_IDS[6]:
        channels = (
            hawking_flux,
            relaxation_flux,
            visibility,
            gravitational_memory,
            residual_memory,
            consistency_witness,
        )
        response = sum((np.abs(channel) for channel in channels), np.zeros_like(coordinate))
        residual = response - sum((np.abs(channel) for channel in channels), np.zeros_like(coordinate))
    else:
        raise ValueError(f"unknown Black-Hole law {law_id}")
    ensure_finite((response, residual), name=law_id)
    norm = float(np.linalg.norm(np.ravel(residual)))
    return BlackHoleLaw(
        law_id,
        np.asarray(response, dtype=float),
        np.asarray(residual, dtype=float),
        norm,
        float(abs(np.ravel(response)[0]) + abs(np.ravel(response)[-1])),
        "satisfied" if norm <= value.tolerance else "open",
    )


def _combine(responses: tuple[np.ndarray, ...]) -> np.ndarray:
    if not responses:
        raise ValueError("at least one Black-Hole source response is required")
    result = np.asarray(responses[0], dtype=float)
    for response in responses[1:]:
        result = additive_derivation(result, response)
    ensure_finite(result, name="Black-Hole additive synthesis")
    return result


def _b_sources(identifier: str) -> tuple[str, ...]:
    for b_id, source_ids in B_SPECS:
        if b_id == identifier:
            return source_ids
    raise ValueError(f"unknown Black-Hole synthesis {identifier}")


def _b_operator(b_id: str, source_ids: tuple[str, ...], value: BlackHoleInput) -> BlackHoleSynthesis:
    laws = tuple(_law(source_id, value) for source_id in source_ids)
    responses = tuple(item.response for item in laws)
    combined = _combine(responses)
    residual = sum((item.residual for item in laws), np.zeros_like(laws[0].residual))
    interaction = combined - sum(responses, np.zeros_like(responses[0]))
    energy = float(np.vdot(interaction.ravel(), interaction.ravel()).real)
    return BlackHoleSynthesis(
        b_id,
        responses,
        combined,
        np.asarray(residual, dtype=float),
        energy,
        "satisfied" if float(np.linalg.norm(residual)) <= value.tolerance else "open",
    )


def _c_operator(value: BlackHoleInput) -> BlackHoleSpatialClosure:
    syntheses = tuple(_b_operator(b_id, source_ids, value) for b_id, source_ids in B_SPECS)
    responses = tuple(item.combined_operator for item in syntheses)
    raw = _combine(responses)
    coordinate = np.asarray(value.coordinate, dtype=float)
    phase = (coordinate - coordinate[0]) / (coordinate[-1] - coordinate[0])
    window = np.sin(np.pi * phase) ** 2
    local = window * raw
    boundary = boundary_leakage(local)
    reconstruction = float(np.linalg.norm(local - window * raw))
    localization = float(np.linalg.norm(np.gradient(local, coordinate, edge_order=2)))
    coercivity = coercivity_ratio(local, raw)
    closed = boundary <= value.tolerance and reconstruction <= value.tolerance and coercivity > 0.0
    return BlackHoleSpatialClosure(
        C_ID,
        responses,
        local,
        boundary,
        reconstruction,
        localization,
        coercivity,
        "closed" if closed else "open",
    )


def _residual(name: str, values: np.ndarray | tuple[float, ...], tolerance: float) -> ResidualResult:
    vector = tuple(float(item) for item in np.ravel(values))
    passed = float(np.linalg.norm(vector)) <= tolerance
    return ResidualResult(name, vector, tolerance, passed, ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN)


def _remove_a(b_id: str, source_ids: tuple[str, ...], removed_index: int, value: BlackHoleInput) -> SourceRemovalResult:
    complete = _b_operator(b_id, source_ids, value)
    remaining = tuple(response for index, response in enumerate(complete.source_responses) if index != removed_index)
    return source_removal_result(
        ComplexId(source_ids[removed_index]),
        complete.combined_operator,
        _combine(remaining),
        tolerance=max(value.tolerance, 1e-12),
    )


def _remove_b(removed_index: int, value: BlackHoleInput) -> SourceRemovalResult:
    complete = _c_operator(value)
    remaining = tuple(response for index, response in enumerate(complete.source_responses) if index != removed_index)
    coordinate = np.asarray(value.coordinate, dtype=float)
    phase = (coordinate - coordinate[0]) / (coordinate[-1] - coordinate[0])
    removed_response = (np.sin(np.pi * phase) ** 2) * _combine(remaining)
    return source_removal_result(
        ComplexId(B_SPECS[removed_index][0]),
        complete.local_field,
        removed_response,
        tolerance=max(value.tolerance, 1e-12),
    )


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec(
        "Black-Hole finite observer-memory field",
        "uniform grid, positive mass and elasticity, finite fields, and bounded visibility",
        (BlackHoleInput,),
    )
    artifact = ArtifactSpec(
        ("hawking_field_csv", "observer_memory_plot", "source_removal_table"),
        "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.simulation.run_contract_suite",
    )
    result: list[ComplexContract] = []
    for identifier in A_IDS:
        result.append(
            ComplexContract(
                ComplexId(identifier), APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain,
                CodomainSpec(f"{identifier} certificate", "typed finite Black-Hole response and residual", (BlackHoleLaw,)),
                partial(_law, identifier),
                residual=lambda source, output, cid=identifier: _residual(cid, output.residual, source.tolerance),
                implementation_path=IMPLEMENTATION_PATH,
            )
        )
    for b_id, source_ids in B_SPECS:
        result.append(
            ComplexContract(
                ComplexId(b_id), APPENDIX, APPENDIX_SHA256, ComplexLevel.B,
                tuple(ComplexId(item) for item in source_ids), domain,
                CodomainSpec(f"{b_id} additive synthesis", "genuine two-source Black-Hole interaction", (BlackHoleSynthesis,)),
                partial(_b_operator, b_id, source_ids),
                residual=lambda source, output, cid=b_id: _residual(cid, output.residual, source.tolerance),
                source_removal_checks=tuple(partial(_remove_a, b_id, source_ids, index) for index in range(len(source_ids))),
                artifact_spec=artifact,
                implementation_path=IMPLEMENTATION_PATH,
            )
        )
    result.append(
        ComplexContract(
            ComplexId(C_ID), APPENDIX, APPENDIX_SHA256, ComplexLevel.C,
            tuple(ComplexId(item[0]) for item in B_SPECS), domain,
            CodomainSpec(C_ID, "boundary-closed observer-accessible Hawking-memory field", (BlackHoleSpatialClosure,)),
            _c_operator,
            residual=lambda source, output: _residual(
                C_ID, (output.boundary_residual, output.reconstruction_residual), source.tolerance
            ),
            closure_predicate=lambda output, residual: output.status == "closed"
            and output.coercivity > 0.0
            and residual is not None
            and residual.passed,
            source_removal_checks=tuple(partial(_remove_b, index) for index in range(len(B_SPECS))),
            artifact_spec=artifact,
            exact_semantics=True,
            implementation_path=IMPLEMENTATION_PATH,
        )
    )
    return tuple(result)
