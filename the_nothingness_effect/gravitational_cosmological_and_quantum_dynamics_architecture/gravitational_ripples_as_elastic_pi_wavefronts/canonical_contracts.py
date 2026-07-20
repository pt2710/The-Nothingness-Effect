"""Typed finite contracts for the remaining Elastic-pi Ripple complexes.

The contracts expose executable witnesses for memory transfer, mode conversion,
shock onset, stochastic tilt, environmental transport, and inverse detection.
They do not replace the appendix proofs or constitute gravitational-wave
phenomenology or observational validation.
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
    "gravitational_ripples_as_elastic_pi_wavefronts/canonical_contracts.py"
)

A_IDS = (
    "dfi_memory_kernel_in_waveforms_no_extra_memory_imprint",
    "flowpoint_boundary_mode_conversion_pure_mode_propagation",
    "shock_onset_self_steepening_threshold_no_shock_propagation",
    "stochastic_background_tilt_n_e_standard_gr_tilt_n_t",
    "environment_dependent_group_velocity_mapping_uniform_propagation",
    "invertible_source_transport_detection_map_non_invertible_degeneracy",
    "appendix_wide_gravitational_ripples_cross_complex_closure_and_computational_falsification_interface",
)
B_SPECS = (
    ("flowpoint_resolved_dfi_memory_transfer", (A_IDS[0], A_IDS[1])),
    ("shock_gated_stochastic_tilt_production", (A_IDS[2], A_IDS[3])),
    ("environment_tomography_information_metric", (A_IDS[4], A_IDS[5])),
)
C_ID = "memory_shock_environmental_reconstruction"


@dataclass(frozen=True)
class RippleInput:
    coordinate: np.ndarray
    waveform: np.ndarray
    memory_kernel: np.ndarray
    memory_imprint: np.ndarray
    flowpoint_parity: np.ndarray
    boundary_mode: np.ndarray
    conversion_gain: np.ndarray
    converted_mode: np.ndarray
    amplitude: np.ndarray
    shock_indicator: np.ndarray
    frequency: np.ndarray
    stochastic_spectrum: np.ndarray
    stochastic_tilt: np.ndarray
    environment: np.ndarray
    base_velocity: float
    group_velocity: np.ndarray
    source: np.ndarray
    transport_matrix: np.ndarray
    detected: np.ndarray
    shock_threshold: float
    tolerance: float = 1e-10


@dataclass(frozen=True)
class RippleLaw:
    law_name: str
    response: np.ndarray
    residual: np.ndarray
    obstruction: float
    boundary_trace: float
    status: str


@dataclass(frozen=True)
class RippleSynthesis:
    law_name: str
    source_responses: tuple[np.ndarray, ...]
    combined_operator: np.ndarray
    residual: np.ndarray
    interaction_energy: float
    status: str


@dataclass(frozen=True)
class RippleSpatialClosure:
    law_name: str
    source_responses: tuple[np.ndarray, ...]
    local_field: np.ndarray
    boundary_residual: float
    reconstruction_residual: float
    localization_residual: float
    coercivity: float
    status: str


def _validated(value: RippleInput) -> tuple[np.ndarray, ...]:
    fields = tuple(
        np.asarray(item, dtype=float)
        for item in (
            value.coordinate,
            value.waveform,
            value.memory_kernel,
            value.memory_imprint,
            value.flowpoint_parity,
            value.boundary_mode,
            value.conversion_gain,
            value.converted_mode,
            value.amplitude,
            value.shock_indicator,
            value.frequency,
            value.stochastic_spectrum,
            value.stochastic_tilt,
            value.environment,
            value.group_velocity,
            value.source,
            value.detected,
        )
    )
    coordinate = fields[0]
    if coordinate.ndim != 1 or coordinate.size < 5:
        raise DomainViolationError("Ripple contracts require at least five ordered samples")
    if any(item.shape != coordinate.shape for item in fields[1:]):
        raise DomainViolationError("all Ripple fields must share the coordinate shape")
    matrix = np.asarray(value.transport_matrix, dtype=float)
    if matrix.shape != (coordinate.size, coordinate.size):
        raise DomainViolationError("transport matrix must be square on the sampled source space")
    ensure_finite((*fields, matrix), name="Elastic-pi Ripple input")
    spacing = np.diff(coordinate)
    if np.any(spacing <= 0.0):
        raise DomainViolationError("Ripple coordinates must be strictly increasing")
    step = float(np.mean(spacing))
    if not np.allclose(spacing, step, rtol=1e-10, atol=1e-12):
        raise DomainViolationError("finite Ripple witnesses require a uniform grid")
    parity = fields[4]
    if np.any(np.abs(parity - np.rint(parity)) > value.tolerance) or np.any((parity < 0.0) | (parity > 1.0)):
        raise DomainViolationError("Flowpoint parity must be binary")
    if np.any(fields[2] < 0.0) or float(np.sum(fields[2])) <= 0.0:
        raise DomainViolationError("memory kernel must be non-negative and non-zero")
    if np.any(fields[6] < 0.0) or np.any(fields[9] < 0.0):
        raise DomainViolationError("conversion gain and shock indicator must be non-negative")
    if np.any(fields[10] <= 0.0) or np.any(fields[11] <= 0.0):
        raise DomainViolationError("frequency and stochastic spectrum must be strictly positive")
    if np.any(fields[13] < 0.0) or np.any(fields[14] <= 0.0):
        raise DomainViolationError("environment must be non-negative and group velocity positive")
    if not np.isfinite(value.base_velocity) or value.base_velocity <= 0.0:
        raise DomainViolationError("base velocity must be finite and strictly positive")
    if not np.isfinite(value.shock_threshold) or value.shock_threshold < 0.0:
        raise DomainViolationError("shock threshold must be finite and non-negative")
    if not np.isfinite(value.tolerance) or value.tolerance < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    return (*fields, matrix, np.asarray(step))


def _law(law_id: str, value: RippleInput) -> RippleLaw:
    (
        coordinate,
        waveform,
        memory_kernel,
        memory_imprint,
        parity,
        boundary_mode,
        conversion_gain,
        converted_mode,
        amplitude,
        shock_indicator,
        frequency,
        spectrum,
        stochastic_tilt,
        environment,
        group_velocity,
        source,
        detected,
        transport,
        step_array,
    ) = _validated(value)
    step = float(step_array)
    obstruction = 0.0
    if law_id == A_IDS[0]:
        kernel = memory_kernel / float(np.sum(memory_kernel))
        response = np.convolve(waveform, kernel, mode="same") * step
        residual = memory_imprint - response
    elif law_id == A_IDS[1]:
        sign = 1.0 - 2.0 * parity
        response = sign * conversion_gain * boundary_mode
        residual = converted_mode - response
    elif law_id == A_IDS[2]:
        response = np.maximum(np.abs(np.gradient(amplitude, step, edge_order=2)) - value.shock_threshold, 0.0)
        residual = shock_indicator - response
    elif law_id == A_IDS[3]:
        response = np.gradient(np.log(spectrum), np.log(frequency), edge_order=2)
        residual = stochastic_tilt - response
    elif law_id == A_IDS[4]:
        response = value.base_velocity / (1.0 + environment)
        residual = group_velocity - response
    elif law_id == A_IDS[5]:
        response = transport @ source
        residual = detected - response
        obstruction = float(np.min(np.linalg.svd(transport, compute_uv=False)))
    elif law_id == A_IDS[6]:
        channels = (memory_imprint, converted_mode, shock_indicator, stochastic_tilt, group_velocity, detected)
        response = sum((np.abs(channel) for channel in channels), np.zeros_like(coordinate))
        residual = response - sum((np.abs(channel) for channel in channels), np.zeros_like(coordinate))
    else:
        raise ValueError(f"unknown Ripple law {law_id}")
    ensure_finite((response, residual, obstruction), name=law_id)
    norm = float(np.linalg.norm(np.ravel(residual)))
    status = "degenerate" if law_id == A_IDS[5] and obstruction <= value.tolerance else ("satisfied" if norm <= value.tolerance else "open")
    return RippleLaw(
        law_id,
        np.asarray(response, dtype=float),
        np.asarray(residual, dtype=float),
        obstruction if law_id == A_IDS[5] else norm,
        float(abs(np.ravel(response)[0]) + abs(np.ravel(response)[-1])),
        status,
    )


def _combine(responses: tuple[np.ndarray, ...]) -> np.ndarray:
    if not responses:
        raise ValueError("at least one Ripple source response is required")
    result = np.asarray(responses[0], dtype=float)
    for response in responses[1:]:
        result = additive_derivation(result, response)
    ensure_finite(result, name="Ripple additive synthesis")
    return result


def _b_sources(identifier: str) -> tuple[str, ...]:
    for b_id, source_ids in B_SPECS:
        if b_id == identifier:
            return source_ids
    raise ValueError(f"unknown Ripple synthesis {identifier}")


def _b_operator(b_id: str, source_ids: tuple[str, ...], value: RippleInput) -> RippleSynthesis:
    laws = tuple(_law(source_id, value) for source_id in source_ids)
    responses = tuple(item.response for item in laws)
    combined = _combine(responses)
    residual = sum((item.residual for item in laws), np.zeros_like(laws[0].residual))
    interaction = combined - sum(responses, np.zeros_like(responses[0]))
    energy = float(np.vdot(interaction.ravel(), interaction.ravel()).real)
    return RippleSynthesis(
        b_id,
        responses,
        combined,
        np.asarray(residual, dtype=float),
        energy,
        "satisfied" if float(np.linalg.norm(residual)) <= value.tolerance else "open",
    )


def _c_operator(value: RippleInput) -> RippleSpatialClosure:
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
    return RippleSpatialClosure(C_ID, responses, local, boundary, reconstruction, localization, coercivity, "closed" if closed else "open")


def _residual(name: str, values: np.ndarray | tuple[float, ...], tolerance: float) -> ResidualResult:
    vector = tuple(float(item) for item in np.ravel(values))
    passed = float(np.linalg.norm(vector)) <= tolerance
    return ResidualResult(name, vector, tolerance, passed, ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN)


def _remove_a(b_id: str, source_ids: tuple[str, ...], removed_index: int, value: RippleInput) -> SourceRemovalResult:
    complete = _b_operator(b_id, source_ids, value)
    remaining = tuple(response for index, response in enumerate(complete.source_responses) if index != removed_index)
    return source_removal_result(
        ComplexId(source_ids[removed_index]), complete.combined_operator, _combine(remaining), tolerance=max(value.tolerance, 1e-12)
    )


def _remove_b(removed_index: int, value: RippleInput) -> SourceRemovalResult:
    complete = _c_operator(value)
    remaining = tuple(response for index, response in enumerate(complete.source_responses) if index != removed_index)
    coordinate = np.asarray(value.coordinate, dtype=float)
    phase = (coordinate - coordinate[0]) / (coordinate[-1] - coordinate[0])
    removed_response = (np.sin(np.pi * phase) ** 2) * _combine(remaining)
    return source_removal_result(
        ComplexId(B_SPECS[removed_index][0]), complete.local_field, removed_response, tolerance=max(value.tolerance, 1e-12)
    )


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec(
        "Elastic-pi Ripple finite wave field",
        "uniform grid, binary Flowpoint parity, positive spectral/transport domains, and finite fields",
        (RippleInput,),
    )
    artifact = ArtifactSpec(
        ("ripple_field_csv", "memory_transport_plot", "source_removal_table"),
        "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts.simulation.run_contract_suite",
    )
    result: list[ComplexContract] = []
    for identifier in A_IDS:
        result.append(
            ComplexContract(
                ComplexId(identifier), APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain,
                CodomainSpec(f"{identifier} certificate", "typed finite Ripple response and obstruction residual", (RippleLaw,)),
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
                CodomainSpec(f"{b_id} additive synthesis", "genuine two-source Ripple interaction", (RippleSynthesis,)),
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
            CodomainSpec(C_ID, "boundary-closed memory-shock-environment reconstruction", (RippleSpatialClosure,)),
            _c_operator,
            residual=lambda source, output: _residual(C_ID, (output.boundary_residual, output.reconstruction_residual), source.tolerance),
            closure_predicate=lambda output, residual: output.status == "closed" and output.coercivity > 0.0 and residual is not None and residual.passed,
            source_removal_checks=tuple(partial(_remove_b, index) for index in range(len(B_SPECS))),
            artifact_spec=artifact,
            exact_semantics=True,
            implementation_path=IMPLEMENTATION_PATH,
        )
    )
    return tuple(result)
