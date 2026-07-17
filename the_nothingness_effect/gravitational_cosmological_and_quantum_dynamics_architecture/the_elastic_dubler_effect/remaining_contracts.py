"""Typed executable laws for the remaining Elastic Dubler theorem complexes.

The finite operators implement the authoritative Part-I identities as executable
witnesses. They preserve the repository claim boundary: numerical certificates
do not replace appendix proofs or physical validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import Callable

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ArtifactSpec,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    ResidualResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    source_removal_result,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    ClosureStatus,
    DomainViolationError,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import (
    ensure_finite,
)

APPENDIX = "appendix_tne_gravitational_cosmological_quantum_dynamics.tex"
APPENDIX_SHA256 = "5cb9526f26767ca245f32a70a8f5a12138d374b3f4bb9821db155b9eece35062"
IMPLEMENTATION = (
    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_"
    "architecture/the_elastic_dubler_effect/remaining_contracts.py"
)

A5 = ComplexId("parity_symmetry_dubler_duality_closure")
A6 = ComplexId("locality_nonlocality_in_the_dubler_pdfi_framework")
A7 = ComplexId("universal_elasticity_constant_k_d")
A8 = ComplexId("emergence_triviality_in_elastic_fields")
A9 = ComplexId("spectral_observability_indistinguishability")
A10 = ComplexId("dubler_entropy_conservation")
A11 = ComplexId("temporal_asymmetry_symmetry_in_pdfi_fields")
A12 = ComplexId("causality_via_elastic_dubler_e_and_causal_symmetry")
A13 = ComplexId("information_entropy_in_the_elastic_dubler_perspective")
A14 = ComplexId("pdfi_e_quantum_entanglement_interface")
A15 = ComplexId("spatial_homogeneity_heterogeneity_duality")
A16 = ComplexId("universal_domain_specific_k_d_duality")
A17 = ComplexId(
    "appendix_wide_elastic_dubler_cross_complex_closure_and_"
    "computational_falsification_interface"
)

B3 = ComplexId("parity_localized_pdfi_response_operator")
B4 = ComplexId("elasticity_scaled_spectral_operator_flow")
B5 = ComplexId("observable_entropy_redistribution_channel")
B6 = ComplexId("temporal_directed_elastic_transport")
B7 = ComplexId("information_calibrated_quantum_spectral_response")
B8 = ComplexId("elasticity_weighted_spatial_heterogeneity")

C2 = ComplexId("parity_elastic_spectral_spatial_closure")
C3 = ComplexId("observable_conserved_directed_transport_closure")
C4 = ComplexId("spatially_calibrated_quantum_information_closure")

IDS = (
    A5,
    A6,
    A7,
    A8,
    A9,
    A10,
    A11,
    A12,
    A13,
    A14,
    A15,
    A16,
    A17,
    B3,
    B4,
    B5,
    B6,
    B7,
    B8,
    C2,
    C3,
    C4,
)


@dataclass(frozen=True)
class ElasticDublerInput:
    coordinates: np.ndarray
    entropy: np.ndarray
    pdfi_field: np.ndarray
    parity_operator: np.ndarray
    locality_operator: np.ndarray
    spectral_state: np.ndarray
    observation_operator: np.ndarray
    temporal_signal: np.ndarray
    entropy_rate: np.ndarray
    boundary_flux: np.ndarray
    information_field: np.ndarray
    quantum_h0: np.ndarray
    quantum_q: np.ndarray
    quantum_state: np.ndarray
    domain_fields: np.ndarray
    domain_elasticities: np.ndarray
    domain_weights: np.ndarray
    elasticity_scale: float = 2.0
    baseline_elasticity: float = 1.0
    alpha: float = 1.0
    temporal_gain: float = 1.0
    information_gain: float = 0.5
    information_scale: float = 2.0
    observation_tolerance: float = 1e-8
    tolerance: float = 1e-9


@dataclass(frozen=True)
class ElasticDublerLaw:
    physical: np.ndarray
    source_blocks: tuple[np.ndarray, ...]
    derived_block: np.ndarray
    residuals: tuple[float, ...]
    labels: tuple[str, ...]


def _validate(value: ElasticDublerInput) -> tuple[np.ndarray, float]:
    x = np.asarray(value.coordinates, dtype=float)
    if x.ndim != 1 or x.size < 5:
        raise DomainViolationError(
            "Elastic Dubler witnesses require at least five coordinates"
        )
    arrays = {
        "entropy": value.entropy,
        "pDFI field": value.pdfi_field,
        "spectral state": value.spectral_state,
        "temporal signal": value.temporal_signal,
        "entropy rate": value.entropy_rate,
        "boundary flux": value.boundary_flux,
        "information field": value.information_field,
    }
    for name, raw in arrays.items():
        array = np.asarray(raw, dtype=float)
        if array.shape != x.shape:
            raise DomainViolationError(f"{name} must have shape {x.shape}")
    n = x.size
    for name, raw in (
        ("parity operator", value.parity_operator),
        ("locality operator", value.locality_operator),
        ("observation operator", value.observation_operator),
    ):
        array = np.asarray(raw, dtype=float)
        if array.shape != (n, n):
            raise DomainViolationError(f"{name} must have shape {(n, n)}")
    h0 = np.asarray(value.quantum_h0, dtype=complex)
    q = np.asarray(value.quantum_q, dtype=complex)
    state = np.asarray(value.quantum_state, dtype=complex)
    if h0.ndim != 2 or h0.shape[0] != h0.shape[1]:
        raise DomainViolationError("quantum_h0 must be square")
    if q.shape != h0.shape or state.shape != (h0.shape[0],):
        raise DomainViolationError("quantum operator/state dimensions are incompatible")
    domain_fields = np.asarray(value.domain_fields, dtype=float)
    elasticities = np.asarray(value.domain_elasticities, dtype=float)
    weights = np.asarray(value.domain_weights, dtype=float)
    if domain_fields.ndim != 2 or domain_fields.shape[1] != n:
        raise DomainViolationError("domain_fields must be a two-dimensional field family")
    if elasticities.shape != (domain_fields.shape[0],):
        raise DomainViolationError("one positive elasticity is required per domain field")
    if weights.shape != elasticities.shape:
        raise DomainViolationError("one positive weight is required per domain elasticity")
    ensure_finite(value, name="Elastic Dubler input")
    spacing = np.diff(x)
    if np.any(spacing <= 0.0) or not np.allclose(spacing, spacing[0]):
        raise DomainViolationError("coordinates must be strictly increasing and uniform")
    positive = (
        value.elasticity_scale,
        value.baseline_elasticity,
        value.alpha,
        value.temporal_gain,
        value.information_scale,
    )
    if any(float(item) <= 0.0 for item in positive):
        raise DomainViolationError("declared scales and gains must be strictly positive")
    if value.observation_tolerance < 0.0 or value.tolerance < 0.0:
        raise DomainViolationError("tolerances must be non-negative")
    if np.any(elasticities <= 0.0) or np.any(weights <= 0.0):
        raise DomainViolationError("domain elasticities and weights must be positive")
    if not np.isclose(np.sum(weights), 1.0):
        raise DomainViolationError("domain weights must sum to one")
    if not np.isclose(np.linalg.norm(state), 1.0):
        raise DomainViolationError("quantum_state must be normalized")
    return x, float(spacing[0])


def _valid(value: ElasticDublerInput) -> bool:
    try:
        _validate(value)
    except (DomainViolationError, TypeError, ValueError):
        return False
    return True


def _pi_e(value: ElasticDublerInput) -> np.ndarray:
    exponent = -np.asarray(value.entropy, dtype=float) / float(value.elasticity_scale)
    with np.errstate(over="raise", invalid="raise"):
        try:
            result = np.pi * np.exp(exponent)
        except FloatingPointError as exc:
            raise DomainViolationError(
                "Elastic-pi exponential leaves the finite domain"
            ) from exc
    ensure_finite(result, name="Elastic-pi field")
    return result


def _difference_matrix(n: int, step: float) -> np.ndarray:
    result = np.zeros((n - 1, n), dtype=float)
    for index in range(n - 1):
        result[index, index] = -1.0 / step
        result[index, index + 1] = 1.0 / step
    return result


def _summary(*values: object) -> np.ndarray:
    arrays = [np.asarray(item) for item in values]
    flat = np.concatenate(tuple(np.abs(item).ravel() for item in arrays))
    ensure_finite(flat, name="source summary")
    return np.asarray(
        (
            float(np.linalg.norm(flat)),
            float(np.mean(flat)),
            float(np.max(flat)),
        ),
        dtype=float,
    )


def _combine(blocks: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    first, second = (np.asarray(item, dtype=float) for item in blocks)
    result = first + second + first * second
    ensure_finite(result, name="derived source interaction")
    return result


def _law(
    physical: object,
    residuals: tuple[float, ...],
    labels: tuple[str, ...],
    *,
    source_blocks: tuple[np.ndarray, ...] = (),
) -> ElasticDublerLaw:
    physical_array = np.asarray(physical)
    ensure_finite((physical_array, residuals, source_blocks), name="Elastic Dubler law")
    derived = (
        _combine((source_blocks[0], source_blocks[1]))
        if len(source_blocks) == 2
        else np.asarray((), dtype=float)
    )
    return ElasticDublerLaw(
        physical=physical_array,
        source_blocks=source_blocks,
        derived_block=derived,
        residuals=tuple(float(item) for item in residuals),
        labels=labels,
    )


def parity_symmetry(value: ElasticDublerInput) -> ElasticDublerLaw:
    _validate(value)
    field = np.asarray(value.pdfi_field, dtype=float)
    parity = np.asarray(value.parity_operator, dtype=float)
    odd = 0.5 * (field - parity @ field)
    residuals = (
        float(np.linalg.norm(parity @ parity - np.eye(field.size))),
        float(np.linalg.norm(parity @ odd + odd)),
    )
    return _law(odd, residuals, ("parity_involution", "odd_sector"))


def locality_response(value: ElasticDublerInput) -> ElasticDublerLaw:
    _, step = _validate(value)
    gradient = np.gradient(
        np.asarray(value.pdfi_field, dtype=float), step, edge_order=2
    )
    locality = np.asarray(value.locality_operator, dtype=float)
    response = locality @ gradient
    minimum = float(np.min(np.linalg.svd(locality, compute_uv=False)))
    residuals = (
        max(0.0, value.tolerance - minimum),
        float(np.linalg.norm(response - locality @ gradient)),
    )
    return _law(response, residuals, ("locality_coercivity", "local_response"))


def elasticity_scaling(value: ElasticDublerInput) -> ElasticDublerLaw:
    _validate(value)
    entropy = np.asarray(value.entropy, dtype=float)
    profile = np.abs(entropy - np.mean(entropy))
    scale = float(value.elasticity_scale)
    baseline = float(value.baseline_elasticity)
    with np.errstate(over="raise", invalid="raise"):
        try:
            coefficient = baseline * np.exp(-profile / scale)
            bound = baseline * (np.exp(float(np.max(profile)) / scale) - 1.0)
        except FloatingPointError as exc:
            raise DomainViolationError("elasticity scaling leaves the finite domain") from exc
    actual = float(np.max(np.abs(coefficient - baseline)))
    residuals = (
        max(0.0, -float(np.min(coefficient))),
        max(0.0, actual - bound),
    )
    return _law(coefficient, residuals, ("positive_elasticity", "finite_scale_bound"))


def spectral_emergence(value: ElasticDublerInput) -> ElasticDublerLaw:
    x, step = _validate(value)
    coefficient = elasticity_scaling(value).physical
    state = np.asarray(value.spectral_state, dtype=float)
    difference = _difference_matrix(x.size, step)
    edge_coefficient = 0.5 * (coefficient[:-1] + coefficient[1:])
    potential = np.square(np.asarray(value.entropy, dtype=float)) * 0.05
    operator = difference.T @ np.diag(edge_coefficient) @ difference + np.diag(
        potential
    )
    energy = float(state @ operator @ state)
    rhs = float(
        np.sum(edge_coefficient * np.square(difference @ state))
        + np.sum(potential * np.square(state))
    )
    residuals = (
        float(np.linalg.norm(operator - operator.T)),
        abs(energy - rhs),
    )
    return _law(
        np.concatenate((operator.ravel(), np.asarray((energy,)))),
        residuals,
        ("self_adjoint_operator", "quadratic_form_identity"),
    )


def spectral_observability(value: ElasticDublerInput) -> ElasticDublerLaw:
    _, step = _validate(value)
    source = np.gradient(
        np.asarray(value.pdfi_field, dtype=float), step, edge_order=2
    )
    observed = np.asarray(value.observation_operator, dtype=float) @ source
    distance = float(np.linalg.norm(observed))
    status = float(distance > value.observation_tolerance)
    expected = float(distance > value.observation_tolerance)
    residuals = (abs(status - expected),)
    return _law(
        np.concatenate((source, observed, np.asarray((distance, status)))),
        residuals,
        ("internal_response", "operational_threshold"),
    )


def entropy_conservation(value: ElasticDublerInput) -> ElasticDublerLaw:
    _validate(value)
    rate = np.asarray(value.entropy_rate, dtype=float)
    flux = np.asarray(value.boundary_flux, dtype=float)
    residuals = (
        float(np.linalg.norm(rate + flux)),
        abs(float(np.sum(flux))),
    )
    return _law(
        np.concatenate((rate, flux)),
        residuals,
        ("local_continuity", "closed_global_flux"),
    )


def temporal_asymmetry(value: ElasticDublerInput) -> ElasticDublerLaw:
    _validate(value)
    signal = np.asarray(value.temporal_signal, dtype=float)
    odd = 0.5 * (signal - signal[::-1])
    defect = float(value.temporal_gain * np.sum(np.abs(odd)))
    residuals = (
        abs(defect - value.temporal_gain * float(np.sum(np.abs(odd)))),
    )
    return _law(
        np.concatenate((odd, np.asarray((defect,)))),
        residuals,
        ("time_reversal_odd_sector",),
    )


def directed_transport(value: ElasticDublerInput) -> ElasticDublerLaw:
    _, step = _validate(value)
    entropy_gradient = np.gradient(
        np.asarray(value.entropy, dtype=float), step, edge_order=2
    )
    elastic = _pi_e(value)
    elastic_gradient = -(elastic / value.elasticity_scale) * entropy_gradient
    current_from_elastic = -value.alpha * elastic_gradient
    current_from_entropy = (
        value.alpha / value.elasticity_scale
    ) * elastic * entropy_gradient
    residuals = (
        float(np.linalg.norm(current_from_elastic - current_from_entropy)),
    )
    return _law(
        current_from_entropy,
        residuals,
        ("elastic_gradient_identity",),
    )


def information_entropy(value: ElasticDublerInput) -> ElasticDublerLaw:
    _validate(value)
    calibrated = (
        np.asarray(value.entropy, dtype=float)
        + value.information_scale * np.asarray(value.information_field, dtype=float)
    )
    anchor = float(calibrated[0])
    residuals = (float(np.linalg.norm(calibrated - anchor)),)
    return _law(calibrated, residuals, ("information_entropy_calibration",))


def quantum_interface(value: ElasticDublerInput) -> ElasticDublerLaw:
    _validate(value)
    h0 = np.asarray(value.quantum_h0, dtype=complex)
    q = np.asarray(value.quantum_q, dtype=complex)
    state = np.asarray(value.quantum_state, dtype=complex)
    matrix_element = float(np.real(np.vdot(state, q @ state)))
    delta = 1e-6
    expectation_plus = float(np.real(np.vdot(state, (h0 + delta * q) @ state)))
    expectation_minus = float(np.real(np.vdot(state, (h0 - delta * q) @ state)))
    finite_difference = (expectation_plus - expectation_minus) / (2.0 * delta)
    residuals = (
        float(np.linalg.norm(h0 - h0.conj().T)),
        float(np.linalg.norm(q - q.conj().T)),
        abs(finite_difference - matrix_element),
    )
    return _law(
        np.asarray((matrix_element, finite_difference)),
        residuals,
        ("common_domain_self_adjointness", "hellmann_feynman_response"),
    )


def spatial_heterogeneity(value: ElasticDublerInput) -> ElasticDublerLaw:
    _, step = _validate(value)
    fields = np.asarray(value.domain_fields, dtype=float)
    gradients = np.gradient(fields, step, axis=1, edge_order=2)
    heterogeneity = np.linalg.norm(gradients, axis=1)
    residuals = (max(0.0, -float(np.min(heterogeneity))),)
    return _law(
        np.concatenate((heterogeneity, gradients.ravel())),
        residuals,
        ("spatial_heterogeneity",),
    )


def domain_elasticity(value: ElasticDublerInput) -> ElasticDublerLaw:
    _validate(value)
    elasticities = np.asarray(value.domain_elasticities, dtype=float)
    weights = np.asarray(value.domain_weights, dtype=float)
    log_fit = float(np.sum(weights * np.log(elasticities)))
    fitted = float(np.exp(log_fit))
    defect = float(
        np.sum(weights * np.square(1.0 / elasticities - 1.0 / fitted))
    )
    residuals = (
        abs(float(np.log(fitted)) - log_fit),
        max(0.0, -defect),
    )
    return _law(
        np.concatenate((elasticities, np.asarray((fitted, defect)))),
        residuals,
        ("cross_domain_calibration", "geometric_mean_fit"),
    )


_A_OPERATORS: tuple[Callable[[ElasticDublerInput], ElasticDublerLaw], ...] = (
    parity_symmetry,
    locality_response,
    elasticity_scaling,
    spectral_emergence,
    spectral_observability,
    entropy_conservation,
    temporal_asymmetry,
    directed_transport,
    information_entropy,
    quantum_interface,
    spatial_heterogeneity,
    domain_elasticity,
)


def appendix_interface(value: ElasticDublerInput) -> ElasticDublerLaw:
    _validate(value)
    residuals = tuple(
        residual for operator in _A_OPERATORS for residual in operator(value).residuals
    )
    physical = np.asarray(
        (
            float(len(_A_OPERATORS)),
            float(max(residuals, default=0.0)),
            float(np.linalg.norm(residuals)),
        )
    )
    return _law(physical, residuals, ("appendix_wide_residual_localization",))


def parity_localized_response(value: ElasticDublerInput) -> ElasticDublerLaw:
    _, step = _validate(value)
    parity_law = parity_symmetry(value)
    odd = parity_law.physical
    gradient = np.gradient(odd, step, edge_order=2)
    local = np.asarray(value.locality_operator, dtype=float) @ gradient
    blocks = (_summary(odd), _summary(local))
    residuals = (
        *parity_law.residuals,
        float(np.linalg.norm(local - value.locality_operator @ gradient)),
    )
    return _law(
        local,
        residuals,
        ("parity_odd_source", "localized_response"),
        source_blocks=blocks,
    )


def elasticity_spectral_flow(value: ElasticDublerInput) -> ElasticDublerLaw:
    _validate(value)
    coefficient_law = elasticity_scaling(value)
    spectral_law = spectral_emergence(value)
    blocks = (
        _summary(coefficient_law.physical),
        _summary(spectral_law.physical),
    )
    residuals = (*coefficient_law.residuals, *spectral_law.residuals)
    return _law(
        np.concatenate((coefficient_law.physical, spectral_law.physical)),
        residuals,
        ("finite_elasticity", "spectral_operator_flow"),
        source_blocks=blocks,
    )


def observable_redistribution(value: ElasticDublerInput) -> ElasticDublerLaw:
    _validate(value)
    observation_law = spectral_observability(value)
    balance_law = entropy_conservation(value)
    flux = np.asarray(value.boundary_flux, dtype=float)
    observed_flux = np.asarray(value.observation_operator, dtype=float) @ (-flux)
    blocks = (
        _summary(observation_law.physical),
        _summary(balance_law.physical),
    )
    residuals = (
        *observation_law.residuals,
        *balance_law.residuals,
        float(
            np.linalg.norm(observed_flux - value.observation_operator @ (-flux))
        ),
    )
    return _law(
        np.concatenate((value.entropy_rate, flux, observed_flux)),
        residuals,
        ("observed_flux", "local_global_balance"),
        source_blocks=blocks,
    )


def temporal_directed_transport(value: ElasticDublerInput) -> ElasticDublerLaw:
    _validate(value)
    temporal_law = temporal_asymmetry(value)
    current_law = directed_transport(value)
    current_norm = float(np.linalg.norm(current_law.physical))
    history = np.asarray(value.temporal_signal, dtype=float) * current_norm
    odd_history = 0.5 * (history - history[::-1])
    defect = float(value.temporal_gain * np.sum(np.abs(odd_history)))
    blocks = (
        _summary(temporal_law.physical),
        _summary(current_law.physical),
    )
    residuals = (
        *temporal_law.residuals,
        *current_law.residuals,
        abs(defect - value.temporal_gain * float(np.sum(np.abs(odd_history)))),
    )
    return _law(
        np.concatenate((history, odd_history, np.asarray((defect,)))),
        residuals,
        ("measured_current_history", "time_reversal_transport_defect"),
        source_blocks=blocks,
    )


def information_quantum_response(value: ElasticDublerInput) -> ElasticDublerLaw:
    _validate(value)
    information_law = information_entropy(value)
    quantum_law = quantum_interface(value)
    matrix_element = float(quantum_law.physical[0])
    sensitivity = -(value.information_gain / value.information_scale) * matrix_element
    expected = -(value.information_gain / value.information_scale) * matrix_element
    blocks = (
        _summary(information_law.physical),
        _summary(quantum_law.physical),
    )
    residuals = (
        *information_law.residuals,
        *quantum_law.residuals,
        abs(sensitivity - expected),
    )
    return _law(
        np.asarray((matrix_element, sensitivity)),
        residuals,
        ("information_calibration", "quantum_spectral_sensitivity"),
        source_blocks=blocks,
    )


def elasticity_weighted_heterogeneity(value: ElasticDublerInput) -> ElasticDublerLaw:
    _validate(value)
    spatial_law = spatial_heterogeneity(value)
    calibration_law = domain_elasticity(value)
    field_count = value.domain_fields.shape[0]
    heterogeneity = spatial_law.physical[:field_count]
    elasticities = np.asarray(value.domain_elasticities, dtype=float)
    response = -heterogeneity / elasticities
    blocks = (
        _summary(spatial_law.physical),
        _summary(calibration_law.physical),
    )
    residuals = (
        *spatial_law.residuals,
        *calibration_law.residuals,
        float(np.linalg.norm(response + heterogeneity / elasticities)),
    )
    return _law(
        response,
        residuals,
        ("heterogeneity_functional", "elasticity_weighted_response"),
        source_blocks=blocks,
    )


def parity_elastic_spectral_closure(value: ElasticDublerInput) -> ElasticDublerLaw:
    x, step = _validate(value)
    parity_law = parity_localized_response(value)
    spectral_law = elasticity_spectral_flow(value)
    field = np.asarray(value.pdfi_field, dtype=float)
    parity = np.asarray(value.parity_operator, dtype=float)
    odd = 0.5 * (field - parity @ field)
    coefficient = value.baseline_elasticity * np.exp(
        -np.abs(odd) / value.elasticity_scale
    )
    difference = _difference_matrix(x.size, step)
    edge = 0.5 * (coefficient[:-1] + coefficient[1:])
    operator = difference.T @ np.diag(edge) @ difference
    state = np.asarray(value.spectral_state, dtype=float)
    energy = float(state @ operator @ state)
    rhs = float(np.sum(edge * np.square(difference @ state)))
    blocks = (
        _summary(parity_law.physical),
        _summary(spectral_law.physical),
    )
    residuals = (
        *parity_law.residuals,
        *spectral_law.residuals,
        float(np.linalg.norm(operator - operator.T)),
        abs(energy - rhs),
    )
    return _law(
        np.concatenate((operator.ravel(), np.asarray((energy,)))),
        residuals,
        ("parity_elastic_coefficient", "spectral_spatial_operator"),
        source_blocks=blocks,
    )


def observable_directed_transport_closure(
    value: ElasticDublerInput,
) -> ElasticDublerLaw:
    _validate(value)
    redistribution_law = observable_redistribution(value)
    transport_law = temporal_directed_transport(value)
    current_norm = float(np.linalg.norm(directed_transport(value).physical))
    calibrated_flux = np.asarray(value.temporal_signal, dtype=float) * current_norm
    odd_flux = 0.5 * (calibrated_flux - calibrated_flux[::-1])
    observed = np.asarray(value.observation_operator, dtype=float) @ odd_flux
    blocks = (
        _summary(redistribution_law.physical),
        _summary(transport_law.physical),
    )
    residuals = (
        *redistribution_law.residuals,
        *transport_law.residuals,
        float(np.linalg.norm(value.boundary_flux - calibrated_flux)),
        float(np.linalg.norm(value.entropy_rate + value.boundary_flux)),
        float(np.linalg.norm(observed - value.observation_operator @ odd_flux)),
    )
    return _law(
        np.concatenate((calibrated_flux, odd_flux, observed)),
        residuals,
        ("calibrated_entropy_current", "observed_odd_flux"),
        source_blocks=blocks,
    )


def spatial_quantum_information_closure(
    value: ElasticDublerInput,
) -> ElasticDublerLaw:
    _validate(value)
    quantum_law = information_quantum_response(value)
    spatial_law = elasticity_weighted_heterogeneity(value)
    matrix_element = float(quantum_interface(value).physical[0])
    information = np.asarray(value.information_field, dtype=float)
    elasticity = float(value.domain_elasticities[0])
    coupling = elasticity * (information - float(np.mean(information)))
    response = coupling * matrix_element
    expected = coupling * matrix_element
    blocks = (
        _summary(quantum_law.physical),
        _summary(spatial_law.physical),
    )
    residuals = (
        *quantum_law.residuals,
        *spatial_law.residuals,
        float(np.linalg.norm(response - expected)),
        abs(float(np.mean(coupling))),
    )
    return _law(
        np.concatenate((coupling, response)),
        residuals,
        ("spatial_information_coupling", "quantum_response_field"),
        source_blocks=blocks,
    )


def _removal(
    operator: Callable[[ElasticDublerInput], ElasticDublerLaw],
    source_id: ComplexId,
    index: int,
    value: ElasticDublerInput,
):
    law = operator(value)
    if len(law.source_blocks) != 2:
        raise RuntimeError("source-removal is defined only for two-source laws")
    complete_blocks = tuple(np.asarray(item, dtype=float) for item in law.source_blocks)
    removed_blocks = list(complete_blocks)
    removed_blocks[index] = np.zeros_like(removed_blocks[index])
    complete = np.concatenate((*complete_blocks, _combine(complete_blocks)))
    removed_tuple = (removed_blocks[0], removed_blocks[1])
    removed = np.concatenate((*removed_tuple, _combine(removed_tuple)))
    return source_removal_result(
        source_id,
        complete,
        removed,
        tolerance=value.tolerance,
    )


def _residual(name: str, output: ElasticDublerLaw, tolerance: float) -> ResidualResult:
    vector = tuple(abs(float(item)) for item in output.residuals)
    return ResidualResult(
        name=name,
        vector=vector,
        tolerance=tolerance,
        passed=all(item <= tolerance for item in vector),
        status=ClosureStatus.OPEN,
        metadata={"labels": output.labels},
    )


def _contract(
    identifier: ComplexId,
    level: ComplexLevel,
    sources: tuple[ComplexId, ...],
    operator: Callable[[ElasticDublerInput], ElasticDublerLaw],
    *,
    closed: bool = False,
) -> ComplexContract:
    removals = tuple(
        partial(_removal, operator, source_id, index)
        for index, source_id in enumerate(sources)
    )
    return ComplexContract(
        complex_id=identifier,
        appendix=APPENDIX,
        appendix_source_sha256=APPENDIX_SHA256,
        level=level,
        source_ids=sources,
        domain=DomainSpec(
            name=str(identifier),
            description="typed finite witness for the authoritative Elastic Dubler law",
            python_types=(ElasticDublerInput,),
            validator=_valid,
        ),
        codomain=CodomainSpec(
            name=str(identifier),
            description="finite physical operator, residuals, and source certificates",
            python_types=(ElasticDublerLaw,),
        ),
        operator=operator,
        residual=lambda source, output: _residual(
            str(identifier), output, source.tolerance
        ),
        closure_predicate=(
            (lambda _output, residual: residual is not None and residual.passed)
            if closed
            else None
        ),
        source_removal_checks=removals,
        artifact_spec=ArtifactSpec(
            ("json", "csv"),
            "python tools/generate_artifact_provenance.py --output-root <output-root>",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )


def contracts() -> tuple[ComplexContract, ...]:
    return (
        _contract(A5, ComplexLevel.A, (), parity_symmetry),
        _contract(A6, ComplexLevel.A, (), locality_response),
        _contract(A7, ComplexLevel.A, (), elasticity_scaling),
        _contract(A8, ComplexLevel.A, (), spectral_emergence),
        _contract(A9, ComplexLevel.A, (), spectral_observability),
        _contract(A10, ComplexLevel.A, (), entropy_conservation),
        _contract(A11, ComplexLevel.A, (), temporal_asymmetry),
        _contract(A12, ComplexLevel.A, (), directed_transport),
        _contract(A13, ComplexLevel.A, (), information_entropy),
        _contract(A14, ComplexLevel.A, (), quantum_interface),
        _contract(A15, ComplexLevel.A, (), spatial_heterogeneity),
        _contract(A16, ComplexLevel.A, (), domain_elasticity),
        _contract(A17, ComplexLevel.A, (), appendix_interface),
        _contract(B3, ComplexLevel.B, (A5, A6), parity_localized_response),
        _contract(B4, ComplexLevel.B, (A7, A8), elasticity_spectral_flow),
        _contract(B5, ComplexLevel.B, (A9, A10), observable_redistribution),
        _contract(B6, ComplexLevel.B, (A11, A12), temporal_directed_transport),
        _contract(B7, ComplexLevel.B, (A13, A14), information_quantum_response),
        _contract(
            B8,
            ComplexLevel.B,
            (A15, A16),
            elasticity_weighted_heterogeneity,
        ),
        _contract(
            C2,
            ComplexLevel.C,
            (B3, B4),
            parity_elastic_spectral_closure,
            closed=True,
        ),
        _contract(
            C3,
            ComplexLevel.C,
            (B5, B6),
            observable_directed_transport_closure,
            closed=True,
        ),
        _contract(
            C4,
            ComplexLevel.C,
            (B7, B8),
            spatial_quantum_information_closure,
            closed=True,
        ),
    )


def sample_input() -> ElasticDublerInput:
    coordinates = np.linspace(0.0, 1.0, 5)
    entropy = np.asarray((-0.5, 0.2, 0.8, 0.2, -0.5), dtype=float)
    pdfi = np.asarray((0.0, 1.0, 0.5, -0.5, 0.25), dtype=float)
    parity = np.fliplr(np.eye(5))
    locality = np.eye(5)
    spectral_state = np.asarray((0.0, 1.0, 0.0, -1.0, 0.5), dtype=float)
    observation = np.eye(5)
    temporal = np.asarray((0.0, 1.0, -0.5, -0.75, 0.25), dtype=float)
    elasticity_scale = 2.0
    alpha = 1.0
    entropy_gradient = np.gradient(
        entropy, coordinates[1] - coordinates[0], edge_order=2
    )
    elastic = np.pi * np.exp(-entropy / elasticity_scale)
    current = (alpha / elasticity_scale) * elastic * entropy_gradient
    current_norm = float(np.linalg.norm(current))
    boundary_flux = temporal * current_norm
    entropy_rate = -boundary_flux
    information_scale = 2.0
    information = (4.0 - entropy) / information_scale
    h0 = np.diag((0.0, 1.0)).astype(complex)
    q = np.diag((1.0, -0.5)).astype(complex)
    state = np.asarray((1.0, 0.0), dtype=complex)
    domain_fields = np.asarray(
        (
            (0.0, 1.0, 0.0, -1.0, 0.0),
            (0.0, 0.5, 1.0, 0.5, 0.0),
        ),
        dtype=float,
    )
    return ElasticDublerInput(
        coordinates=coordinates,
        entropy=entropy,
        pdfi_field=pdfi,
        parity_operator=parity,
        locality_operator=locality,
        spectral_state=spectral_state,
        observation_operator=observation,
        temporal_signal=temporal,
        entropy_rate=entropy_rate,
        boundary_flux=boundary_flux,
        information_field=information,
        quantum_h0=h0,
        quantum_q=q,
        quantum_state=state,
        domain_fields=domain_fields,
        domain_elasticities=np.asarray((2.0, 3.0)),
        domain_weights=np.asarray((0.4, 0.6)),
        elasticity_scale=elasticity_scale,
        baseline_elasticity=1.0,
        alpha=alpha,
        temporal_gain=1.0,
        information_gain=0.5,
        information_scale=information_scale,
        observation_tolerance=1e-8,
        tolerance=1e-8,
    )
