"""Typed finite contracts for the remaining Locality-Driven Gravity complexes."""
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
    "locality_driven_gravity/canonical_contracts.py"
)

A_IDS = (
    "locality_driven_rotation_curve_duality",
    "spiral_pitch_angle_gradient_duality",
    "entropic_screening_nonlocal_curvature_mixing",
    "halo_structure_formation_duality",
    "entropic_gradient_filament_formation_duality",
    "locality_confinement_stability_duality",
    "entropic_localization_cluster_stability_duality",
    "localized_curvature_information_preservation_duality",
    "cosmic_web_emergence_homogenization_duality",
    "appendix_wide_locality_driven_gravity_cross_complex_closure_and_computational_falsification_interfac",
)
B_SPECS = (
    ("rotation_pitch_coupling_invariant", (A_IDS[0], A_IDS[1])),
    ("screened_halo_response", (A_IDS[2], A_IDS[3])),
    ("confined_filament_persistence", (A_IDS[4], A_IDS[5])),
    ("information_bearing_cluster_web_stability", (A_IDS[6], A_IDS[7], A_IDS[8])),
)
C_SPECS = (
    ("screened_rotation_halo_geometry", B_SPECS[0][0], B_SPECS[1][0]),
    ("information_preserving_cosmic_network_closure", B_SPECS[2][0], B_SPECS[3][0]),
)


@dataclass(frozen=True)
class LocalityGravityInput:
    radius: np.ndarray
    entropy: np.ndarray
    potential: np.ndarray
    density: np.ndarray
    rotation_velocity: np.ndarray
    pitch_angle: np.ndarray
    halo_density: np.ndarray
    filament: np.ndarray
    confinement: np.ndarray
    cluster: np.ndarray
    information: np.ndarray
    cosmic_web: np.ndarray
    screening_mass: float
    elasticity: float
    tolerance: float = 1e-10


@dataclass(frozen=True)
class LocalityGravityLaw:
    law_name: str
    response: np.ndarray
    residual: np.ndarray
    obstruction: float
    boundary_trace: float
    status: str


@dataclass(frozen=True)
class LocalityGravitySynthesis:
    law_name: str
    source_responses: tuple[np.ndarray, ...]
    combined_operator: np.ndarray
    residual: np.ndarray
    interaction_energy: float
    status: str


@dataclass(frozen=True)
class LocalityGravitySpatialClosure:
    law_name: str
    source_a: np.ndarray
    source_b: np.ndarray
    local_field: np.ndarray
    boundary_residual: float
    reconstruction_residual: float
    localization_residual: float
    coercivity: float
    status: str


def _validated(value: LocalityGravityInput) -> tuple[np.ndarray, ...]:
    arrays = tuple(
        np.asarray(item, dtype=float)
        for item in (
            value.radius,
            value.entropy,
            value.potential,
            value.density,
            value.rotation_velocity,
            value.pitch_angle,
            value.halo_density,
            value.filament,
            value.confinement,
            value.cluster,
            value.information,
            value.cosmic_web,
        )
    )
    radius = arrays[0]
    if radius.ndim != 1 or radius.size < 5:
        raise DomainViolationError("Locality-Driven Gravity requires at least five radial samples")
    if np.any(radius <= 0.0):
        raise DomainViolationError("radial samples must be strictly positive")
    if any(item.shape != radius.shape for item in arrays[1:]):
        raise DomainViolationError("all Locality-Driven Gravity fields must share the radial shape")
    ensure_finite(arrays, name="Locality-Driven Gravity input")
    spacing = np.diff(radius)
    if np.any(spacing <= 0.0):
        raise DomainViolationError("radius must be strictly increasing")
    step = float(np.mean(spacing))
    if not np.allclose(spacing, step, rtol=1e-10, atol=1e-12):
        raise DomainViolationError("finite Locality witnesses require a uniform radial grid")
    if not np.isfinite(value.screening_mass) or value.screening_mass < 0.0:
        raise DomainViolationError("screening mass must be finite and non-negative")
    if not np.isfinite(value.elasticity) or value.elasticity <= 0.0:
        raise DomainViolationError("elasticity must be finite and strictly positive")
    if any(np.any(item < 0.0) for item in arrays[3:]):
        raise DomainViolationError("density, velocity, pitch, halo, and structural fields must be non-negative")
    if not np.isfinite(value.tolerance) or value.tolerance < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    return (*arrays, np.asarray(step))


def _law(law_id: str, value: LocalityGravityInput) -> LocalityGravityLaw:
    (
        radius,
        entropy,
        potential,
        density,
        velocity,
        pitch,
        halo,
        filament,
        confinement,
        cluster,
        information,
        web,
        step_array,
    ) = _validated(value)
    step = float(step_array)
    grad_s = np.gradient(entropy, step, edge_order=2)
    grad_phi = np.gradient(potential, step, edge_order=2)
    curvature = np.gradient(grad_phi, step, edge_order=2)

    if law_id == A_IDS[0]:
        response = radius * grad_phi
        residual = velocity**2 - response
    elif law_id == A_IDS[1]:
        response = np.abs(grad_s) / (1.0 + np.abs(grad_phi))
        residual = np.tan(pitch) - response
    elif law_id == A_IDS[2]:
        kernel = np.exp(-value.screening_mass * np.abs(radius[:, None] - radius[None, :]))
        kernel /= np.sum(kernel, axis=1, keepdims=True)
        local = kernel @ curvature
        nonlocal_part = curvature - local
        response = np.exp(-value.screening_mass * radius) * local + nonlocal_part
        residual = local + nonlocal_part - curvature
    elif law_id == A_IDS[3]:
        response = np.exp(-value.screening_mass * radius) * halo
        residual = response - np.exp(-value.screening_mass * radius) * halo
    elif law_id == A_IDS[4]:
        response = np.abs(grad_s) * density
        residual = response - np.abs(grad_s) * density
    elif law_id == A_IDS[5]:
        response = confinement * np.exp(-(radius - radius[0]) / value.elasticity)
        residual = np.minimum(response, 0.0)
    elif law_id == A_IDS[6]:
        response = cluster * np.exp(-entropy / value.elasticity)
        residual = np.minimum(response, 0.0)
    elif law_id == A_IDS[7]:
        weight = 1.0 + np.abs(curvature)
        response = information * weight
        residual = response / weight - information
    elif law_id == A_IDS[8]:
        response = web - float(np.mean(web))
        residual = np.full_like(response, float(np.sum(response)) / response.size)
    elif law_id == A_IDS[9]:
        channels = (velocity, pitch, halo, filament, confinement, cluster, information, web)
        response = sum((np.abs(channel) for channel in channels), np.zeros_like(radius))
        residual = response - sum((np.abs(channel) for channel in channels), np.zeros_like(radius))
    else:
        raise ValueError(f"unknown Locality-Driven Gravity law {law_id}")

    ensure_finite((response, residual), name=law_id)
    norm = float(np.linalg.norm(np.ravel(residual)))
    return LocalityGravityLaw(
        law_id,
        np.asarray(response, dtype=float),
        np.asarray(residual, dtype=float),
        norm,
        float(abs(np.ravel(response)[0]) + abs(np.ravel(response)[-1])),
        "satisfied" if norm <= value.tolerance else "open",
    )


def _combine(responses: tuple[np.ndarray, ...]) -> np.ndarray:
    if not responses:
        raise ValueError("at least one source response is required")
    combined = np.asarray(responses[0], dtype=float)
    for response in responses[1:]:
        combined = additive_derivation(combined, response)
    ensure_finite(combined, name="Locality additive synthesis")
    return combined


def _b_sources(identifier: str) -> tuple[str, ...]:
    for b_id, source_ids in B_SPECS:
        if b_id == identifier:
            return source_ids
    raise ValueError(f"unknown Locality synthesis {identifier}")


def _b_operator(b_id: str, source_ids: tuple[str, ...], value: LocalityGravityInput) -> LocalityGravitySynthesis:
    laws = tuple(_law(source_id, value) for source_id in source_ids)
    responses = tuple(item.response for item in laws)
    combined = _combine(responses)
    residual = sum((item.residual for item in laws), np.zeros_like(laws[0].residual))
    interaction = combined - sum(responses, np.zeros_like(responses[0]))
    energy = float(np.vdot(interaction.ravel(), interaction.ravel()).real)
    norm = float(np.linalg.norm(residual))
    return LocalityGravitySynthesis(
        b_id,
        responses,
        combined,
        np.asarray(residual, dtype=float),
        energy,
        "satisfied" if norm <= value.tolerance else "open",
    )


def _c_operator(c_id: str, b_a: str, b_b: str, value: LocalityGravityInput) -> LocalityGravitySpatialClosure:
    first = _b_operator(b_a, _b_sources(b_a), value)
    second = _b_operator(b_b, _b_sources(b_b), value)
    radius = np.asarray(value.radius, dtype=float)
    raw = additive_derivation(first.combined_operator, second.combined_operator)
    phase = (radius - radius[0]) / (radius[-1] - radius[0])
    window = np.sin(np.pi * phase) ** 2
    local = window * raw
    reconstruction = local - window * raw
    boundary = boundary_leakage(local)
    localization = float(np.linalg.norm(np.gradient(local, radius, edge_order=2)))
    coercivity = coercivity_ratio(local, raw)
    reconstruction_norm = float(np.linalg.norm(reconstruction))
    closed = boundary <= value.tolerance and reconstruction_norm <= value.tolerance and coercivity > 0.0
    return LocalityGravitySpatialClosure(
        c_id,
        first.combined_operator,
        second.combined_operator,
        local,
        boundary,
        reconstruction_norm,
        localization,
        coercivity,
        "closed" if closed else "open",
    )


def _residual(name: str, values: np.ndarray | tuple[float, ...], tolerance: float) -> ResidualResult:
    vector = tuple(float(item) for item in np.ravel(values))
    passed = float(np.linalg.norm(vector)) <= tolerance
    return ResidualResult(name, vector, tolerance, passed, ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN)


def _remove_a(b_id: str, source_ids: tuple[str, ...], removed_index: int, value: LocalityGravityInput) -> SourceRemovalResult:
    complete = _b_operator(b_id, source_ids, value)
    remaining = tuple(response for index, response in enumerate(complete.source_responses) if index != removed_index)
    return source_removal_result(
        ComplexId(source_ids[removed_index]),
        complete.combined_operator,
        _combine(remaining),
        tolerance=max(value.tolerance, 1e-12),
    )


def _remove_b(c_id: str, b_a: str, b_b: str, removed_index: int, value: LocalityGravityInput) -> SourceRemovalResult:
    complete = _c_operator(c_id, b_a, b_b, value)
    kept_id = b_b if removed_index == 0 else b_a
    kept = _b_operator(kept_id, _b_sources(kept_id), value)
    radius = np.asarray(value.radius, dtype=float)
    phase = (radius - radius[0]) / (radius[-1] - radius[0])
    removed_response = (np.sin(np.pi * phase) ** 2) * kept.combined_operator
    removed_id = b_a if removed_index == 0 else b_b
    return source_removal_result(
        ComplexId(removed_id),
        complete.local_field,
        removed_response,
        tolerance=max(value.tolerance, 1e-12),
    )


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec(
        "Locality-Driven Gravity finite radial field",
        "uniform positive radial grid, finite non-negative structural fields, non-negative screening, and positive elasticity",
        (LocalityGravityInput,),
    )
    artifact = ArtifactSpec(
        ("radial_field_csv", "residual_plot", "source_removal_table"),
        "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.simulation.run_contract_suite",
    )
    result: list[ComplexContract] = []
    for identifier in A_IDS:
        result.append(
            ComplexContract(
                ComplexId(identifier), APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain,
                CodomainSpec(f"{identifier} certificate", "typed finite Locality response and obstruction residual", (LocalityGravityLaw,)),
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
                CodomainSpec(f"{b_id} additive synthesis", "genuine multi-source Locality interaction", (LocalityGravitySynthesis,)),
                partial(_b_operator, b_id, source_ids),
                residual=lambda source, output, cid=b_id: _residual(cid, output.residual, source.tolerance),
                source_removal_checks=tuple(partial(_remove_a, b_id, source_ids, index) for index in range(len(source_ids))),
                artifact_spec=artifact,
                implementation_path=IMPLEMENTATION_PATH,
            )
        )
    for c_id, b_a, b_b in C_SPECS:
        result.append(
            ComplexContract(
                ComplexId(c_id), APPENDIX, APPENDIX_SHA256, ComplexLevel.C,
                (ComplexId(b_a), ComplexId(b_b)), domain,
                CodomainSpec(f"{c_id} spatial closure", "boundary-closed localized Locality field", (LocalityGravitySpatialClosure,)),
                partial(_c_operator, c_id, b_a, b_b),
                residual=lambda source, output, cid=c_id: _residual(
                    cid, (output.boundary_residual, output.reconstruction_residual), source.tolerance
                ),
                closure_predicate=lambda output, residual: output.status == "closed"
                and output.coercivity > 0.0
                and residual is not None
                and residual.passed,
                source_removal_checks=(
                    partial(_remove_b, c_id, b_a, b_b, 0),
                    partial(_remove_b, c_id, b_a, b_b, 1),
                ),
                artifact_spec=artifact,
                exact_semantics=True,
                implementation_path=IMPLEMENTATION_PATH,
            )
        )
    return tuple(result)
