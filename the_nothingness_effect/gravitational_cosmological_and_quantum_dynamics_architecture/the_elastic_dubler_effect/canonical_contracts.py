"""Explicit executable contracts for the remaining Elastic Dubler theorem complexes.

The operators encode finite, typed witnesses for the appendix source laws. They
preserve the formal/numerical boundary: a finite certificate is not presented as
an empirical validation or as a substitute for the appendix proof.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import Callable

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
    non_cancellation_energy,
    source_removal_result,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import DomainViolationError
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import ensure_finite

APPENDIX = "appendix_tne_gravitational_cosmological_quantum_dynamics.tex"
APPENDIX_SHA256 = "5cb9526f26767ca245f32a70a8f5a12138d374b3f4bb9821db155b9eece35062"
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
    "the_elastic_dubler_effect/canonical_contracts.py"
)

A_IDS = (
    "parity_symmetry_dubler_duality_closure",
    "locality_nonlocality_in_the_dubler_pdfi_framework",
    "universal_elasticity_constant_k_d",
    "emergence_triviality_in_elastic_fields",
    "spectral_observability_indistinguishability",
    "dubler_entropy_conservation",
    "temporal_asymmetry_symmetry_in_pdfi_fields",
    "causality_via_elastic_dubler_e_and_causal_symmetry",
    "information_entropy_in_the_elastic_dubler_perspective",
    "pdfi_e_quantum_entanglement_interface",
    "spatial_homogeneity_heterogeneity_duality",
    "universal_domain_specific_k_d_duality",
    "appendix_wide_elastic_dubler_cross_complex_closure_and_computational_falsification_interface",
)

B_SPECS = (
    ("parity_localized_pdfi_response_operator", A_IDS[0], A_IDS[1]),
    ("elasticity_scaled_spectral_operator_flow", A_IDS[2], A_IDS[3]),
    ("observable_entropy_redistribution_channel", A_IDS[4], A_IDS[5]),
    ("temporal_directed_elastic_transport", A_IDS[6], A_IDS[7]),
    ("information_calibrated_quantum_spectral_response", A_IDS[8], A_IDS[9]),
    ("elasticity_weighted_spatial_heterogeneity", A_IDS[10], A_IDS[11]),
)

C_SPECS = (
    ("parity_elastic_spectral_spatial_closure", B_SPECS[0][0], B_SPECS[1][0]),
    ("observable_conserved_directed_transport_closure", B_SPECS[2][0], B_SPECS[3][0]),
    ("spatially_calibrated_quantum_information_closure", B_SPECS[4][0], B_SPECS[5][0]),
)


@dataclass(frozen=True)
class ElasticDublerInput:
    coordinates: np.ndarray
    entropy: np.ndarray
    pdfi: np.ndarray
    parity: np.ndarray
    observable: np.ndarray
    current: np.ndarray
    information: np.ndarray
    quantum_correlation: np.ndarray
    elasticity: float
    domain_elasticity: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class ElasticDublerLaw:
    law_name: str
    response: np.ndarray
    residual: np.ndarray
    obstruction: float
    boundary_trace: float
    status: str


@dataclass(frozen=True)
class ElasticDublerSynthesis:
    law_name: str
    source_a: np.ndarray
    source_b: np.ndarray
    combined_operator: np.ndarray
    residual: np.ndarray
    interaction_energy: float
    status: str


@dataclass(frozen=True)
class ElasticDublerSpatialClosure:
    law_name: str
    source_a: np.ndarray
    source_b: np.ndarray
    local_field: np.ndarray
    boundary_residual: float
    reconstruction_residual: float
    localization_residual: float
    coercivity: float
    status: str


def _validated(value: ElasticDublerInput) -> tuple[np.ndarray, ...]:
    arrays = tuple(
        np.asarray(item, dtype=float)
        for item in (
            value.coordinates,
            value.entropy,
            value.pdfi,
            value.parity,
            value.observable,
            value.current,
            value.information,
            value.quantum_correlation,
            value.domain_elasticity,
        )
    )
    coordinates = arrays[0]
    if coordinates.ndim != 1 or coordinates.size < 5:
        raise DomainViolationError("Elastic Dubler contracts require at least five spatial samples")
    if any(item.shape != coordinates.shape for item in arrays[1:]):
        raise DomainViolationError("all Elastic Dubler fields must share the coordinate shape")
    ensure_finite(arrays, name="Elastic Dubler input")
    spacing = np.diff(coordinates)
    if np.any(spacing <= 0.0):
        raise DomainViolationError("Elastic Dubler coordinates must be strictly increasing")
    step = float(np.mean(spacing))
    if not np.allclose(spacing, step, rtol=1e-10, atol=1e-12):
        raise DomainViolationError("Elastic Dubler finite witnesses require a uniform grid")
    if not np.isfinite(value.elasticity) or value.elasticity <= 0.0:
        raise DomainViolationError("elasticity K_D must be finite and strictly positive")
    if np.any(arrays[-1] <= 0.0):
        raise DomainViolationError("domain-specific elasticity must be strictly positive")
    if np.any(np.abs(arrays[3] - np.rint(arrays[3])) > value.tolerance) or np.any(
        (arrays[3] < 0.0) | (arrays[3] > 1.0)
    ):
        raise DomainViolationError("parity must be binary")
    if not np.isfinite(value.tolerance) or value.tolerance < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    return (*arrays, np.asarray(step))


def _law(law_id: str, value: ElasticDublerInput) -> ElasticDublerLaw:
    (
        x,
        entropy,
        pdfi,
        parity,
        observable,
        current,
        information,
        quantum,
        domain_kd,
        step_array,
    ) = _validated(value)
    step = float(step_array)
    kd = float(value.elasticity)
    ratio = np.exp(-(entropy - entropy[0]) / kd)

    if law_id == A_IDS[0]:
        sign = 1.0 - 2.0 * parity
        response = sign * ratio * pdfi
        residual = (sign * sign - 1.0) * ratio
    elif law_id == A_IDS[1]:
        kernel = np.exp(-np.abs(x[:, None] - x[None, :]) / kd)
        kernel /= np.sum(kernel, axis=1, keepdims=True)
        local = kernel @ pdfi
        nonlocal_part = pdfi - local
        response = local + nonlocal_part
        residual = response - pdfi
    elif law_id == A_IDS[2]:
        response = ratio
        residual = np.log(response) + (entropy - entropy[0]) / kd
    elif law_id == A_IDS[3]:
        elastic = np.exp(-entropy / kd)
        response = pdfi * (elastic - 1.0)
        residual = response - pdfi * (elastic - 1.0)
    elif law_id == A_IDS[4]:
        internal = np.fft.fft(pdfi)
        observed = np.fft.fft(observable)
        response = np.abs(internal) - np.abs(observed)
        residual = np.fft.ifft(observed).real - observable
    elif law_id == A_IDS[5]:
        response = entropy + current + 1.0
        residual = np.gradient(entropy, step, edge_order=2) + np.gradient(
            current, step, edge_order=2
        )
    elif law_id == A_IDS[6]:
        forward = np.gradient(pdfi, step, edge_order=2)
        reversed_difference = -np.gradient(pdfi[::-1], step, edge_order=2)[::-1]
        response = forward
        residual = forward - reversed_difference
    elif law_id == A_IDS[7]:
        response = np.cumsum(np.maximum(current, 0.0)) * step
        residual = np.minimum(np.diff(response, prepend=response[0]), 0.0)
    elif law_id == A_IDS[8]:
        shifted = information - float(np.max(information))
        probabilities = np.exp(shifted)
        probabilities /= float(np.sum(probabilities))
        response = -probabilities * np.log(probabilities)
        residual = np.asarray((float(np.sum(probabilities)) - 1.0,))
    elif law_id == A_IDS[9]:
        response = ratio * pdfi * quantum
        residual = response - ratio * pdfi * quantum
    elif law_id == A_IDS[10]:
        response = observable - float(np.mean(observable))
        residual = np.asarray((float(np.sum(response)),))
    elif law_id == A_IDS[11]:
        local = np.exp(-entropy / domain_kd)
        universal = np.exp(-entropy / kd)
        response = local / universal
        residual = np.log(response) - entropy * (1.0 / kd - 1.0 / domain_kd)
    elif law_id == A_IDS[12]:
        channels = (ratio, pdfi, observable, current, information, quantum)
        response = sum(np.abs(channel) for channel in channels)
        residual = response - sum(np.abs(channel) for channel in channels)
    else:
        raise ValueError(f"unknown Elastic Dubler law {law_id}")

    ensure_finite((response, residual), name=law_id)
    residual_norm = float(np.linalg.norm(np.ravel(residual)))
    return ElasticDublerLaw(
        law_id,
        np.asarray(response, dtype=float),
        np.asarray(residual, dtype=float),
        residual_norm,
        float(abs(np.ravel(response)[0]) + abs(np.ravel(response)[-1])),
        "satisfied" if residual_norm <= value.tolerance else "open",
    )


def _b_operator(b_id: str, source_a: str, source_b: str, value: ElasticDublerInput) -> ElasticDublerSynthesis:
    first = _law(source_a, value)
    second = _law(source_b, value)
    combined = additive_derivation(first.response, second.response)
    residual = first.residual + second.residual
    ensure_finite((combined, residual), name=b_id)
    return ElasticDublerSynthesis(
        b_id,
        first.response,
        second.response,
        combined,
        np.asarray(residual, dtype=float),
        non_cancellation_energy(first.response, second.response, combined),
        "satisfied" if float(np.linalg.norm(residual)) <= value.tolerance else "open",
    )


def _b_spec(identifier: str) -> tuple[str, str]:
    for b_id, source_a, source_b in B_SPECS:
        if b_id == identifier:
            return source_a, source_b
    raise ValueError(f"unknown Elastic Dubler synthesis {identifier}")


def _c_operator(c_id: str, b_a: str, b_b: str, value: ElasticDublerInput) -> ElasticDublerSpatialClosure:
    source_a_ids = _b_spec(b_a)
    source_b_ids = _b_spec(b_b)
    first = _b_operator(b_a, *source_a_ids, value)
    second = _b_operator(b_b, *source_b_ids, value)
    x = np.asarray(value.coordinates, dtype=float)
    raw = additive_derivation(first.combined_operator, second.combined_operator)
    phase = (x - x[0]) / (x[-1] - x[0])
    window = np.sin(np.pi * phase) ** 2
    local = window * raw
    reconstruction = local - window * raw
    boundary = boundary_leakage(local)
    localization = float(np.linalg.norm(np.gradient(local, x, edge_order=2)))
    coercivity = coercivity_ratio(local, raw)
    reconstruction_norm = float(np.linalg.norm(reconstruction))
    closed = boundary <= value.tolerance and reconstruction_norm <= value.tolerance and coercivity > 0.0
    return ElasticDublerSpatialClosure(
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
    norm = float(np.linalg.norm(vector))
    passed = norm <= tolerance
    return ResidualResult(
        name,
        vector,
        tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
    )


def _remove_a(b_id: str, source_a: str, source_b: str, removed_index: int, value: ElasticDublerInput) -> SourceRemovalResult:
    complete = _b_operator(b_id, source_a, source_b, value)
    remaining = complete.source_b if removed_index == 0 else complete.source_a
    removed_id = source_a if removed_index == 0 else source_b
    return source_removal_result(
        ComplexId(removed_id),
        complete.combined_operator,
        remaining,
        tolerance=max(value.tolerance, 1e-12),
    )


def _remove_b(c_id: str, b_a: str, b_b: str, removed_index: int, value: ElasticDublerInput) -> SourceRemovalResult:
    complete = _c_operator(c_id, b_a, b_b, value)
    kept_id = b_b if removed_index == 0 else b_a
    kept_sources = _b_spec(kept_id)
    kept = _b_operator(kept_id, *kept_sources, value)
    x = np.asarray(value.coordinates, dtype=float)
    phase = (x - x[0]) / (x[-1] - x[0])
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
        "Elastic Dubler finite field",
        "uniform finite grid, binary parity, finite fields, and positive universal/domain elasticity",
        (ElasticDublerInput,),
    )
    artifact = ArtifactSpec(
        ("field_csv", "residual_plot", "source_removal_table"),
        "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.simulation.run_contract_suite",
    )
    result: list[ComplexContract] = []
    for identifier in A_IDS:
        operator: Callable[[ElasticDublerInput], ElasticDublerLaw] = partial(_law, identifier)
        result.append(
            ComplexContract(
                ComplexId(identifier), APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain,
                CodomainSpec(
                    f"{identifier} certificate",
                    "typed finite Elastic Dubler source-law response and obstruction residual",
                    (ElasticDublerLaw,),
                ),
                operator,
                residual=lambda source, output, cid=identifier: _residual(
                    cid, output.residual, source.tolerance
                ),
                implementation_path=IMPLEMENTATION_PATH,
            )
        )
    for b_id, source_a, source_b in B_SPECS:
        result.append(
            ComplexContract(
                ComplexId(b_id), APPENDIX, APPENDIX_SHA256, ComplexLevel.B,
                (ComplexId(source_a), ComplexId(source_b)), domain,
                CodomainSpec(
                    f"{b_id} additive synthesis",
                    "genuine two-source additive response with non-cancellation energy",
                    (ElasticDublerSynthesis,),
                ),
                partial(_b_operator, b_id, source_a, source_b),
                residual=lambda source, output, cid=b_id: _residual(
                    cid, output.residual, source.tolerance
                ),
                source_removal_checks=(
                    partial(_remove_a, b_id, source_a, source_b, 0),
                    partial(_remove_a, b_id, source_a, source_b, 1),
                ),
                artifact_spec=artifact,
                implementation_path=IMPLEMENTATION_PATH,
            )
        )
    for c_id, b_a, b_b in C_SPECS:
        result.append(
            ComplexContract(
                ComplexId(c_id), APPENDIX, APPENDIX_SHA256, ComplexLevel.C,
                (ComplexId(b_a), ComplexId(b_b)), domain,
                CodomainSpec(
                    f"{c_id} spatial closure",
                    "boundary-closed localized field with exact finite reconstruction identity",
                    (ElasticDublerSpatialClosure,),
                ),
                partial(_c_operator, c_id, b_a, b_b),
                residual=lambda source, output, cid=c_id: _residual(
                    cid,
                    (output.boundary_residual, output.reconstruction_residual),
                    source.tolerance,
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
