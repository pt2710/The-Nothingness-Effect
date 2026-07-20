"""Derived Observation-and-Collapse B/C operators and source-removal gates."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    source_removal_result,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
    NonFiniteValueError,
)

from ._canonical_core import (
    A1,
    A2,
    A3,
    A4,
    A5,
    A6,
    A7,
    A8,
    B1,
    B2,
    B3,
    B4,
    _binary_vector,
    _cesaro,
    _close,
    _closure_relation,
    _involution_projectors,
    _matrix,
    _steps,
    _tolerance,
    _vector,
)


@dataclass(frozen=True)
class OutcomeClosureInput:
    relation: np.ndarray
    subset: np.ndarray
    projectors: tuple[np.ndarray, ...]
    state: np.ndarray
    outcome: int
    tolerance: float = 1e-10


@dataclass(frozen=True)
class SpectralCollapseInput:
    operator: np.ndarray
    state: np.ndarray
    steps: int = 8
    tolerance: float = 1e-10


@dataclass(frozen=True)
class TemporalCompressionInput:
    histories: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class DimensionalBindingInput:
    pinning_projector: np.ndarray
    selection_projector: np.ndarray
    state: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class LocalityInput:
    temporal_state: np.ndarray
    spectral_state: np.ndarray
    localization_projector: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class HorizonInput:
    temporal_profiles: np.ndarray
    spectral_profiles: np.ndarray
    threshold: float = 1e-8
    tolerance: float = 1e-10


@dataclass(frozen=True)
class OutcomeFieldInput:
    relation: np.ndarray
    subset: np.ndarray
    projectors: tuple[np.ndarray, ...]
    invariant_projector: np.ndarray
    state: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class OutcomeClosureLaw:
    closed_support: np.ndarray
    conditional_state: np.ndarray
    probability: float
    idempotence_residual: float
    support_residual: float
    repeatability_residual: float
    normalization_residual: float


@dataclass(frozen=True)
class SpectralPinningLaw:
    invariant_projector: np.ndarray
    antifixed_projector: np.ndarray
    pinned_state: np.ndarray
    cesaro_state: np.ndarray
    involution_residual: float
    projector_residual: float
    orthogonality_residual: float
    pinning_residual: float
    drift_residual: float


@dataclass(frozen=True)
class TemporalCompressionLaw:
    preparation_limits: np.ndarray
    common_output: np.ndarray
    compressed_history: np.ndarray
    convergence_residual: float
    common_limit_residual: float
    compression_residual: float
    cauchy_residual: float


@dataclass(frozen=True)
class SpectralSelectionLaw:
    eigenvalues: np.ndarray
    spectral_weights: np.ndarray
    invariant_projector: np.ndarray
    selected_state: np.ndarray
    multiplier: np.ndarray
    entropy: float
    projection_residual: float
    selection_residual: float
    multiplier_residual: float
    preparation_residual: float


@dataclass(frozen=True)
class DimensionalBindingLaw:
    common_projector: np.ndarray
    bound_state: np.ndarray
    bound_dimension: int
    commutator_residual: float
    projector_residual: float
    fixed_core_residual: float
    composition_residual: float


@dataclass(frozen=True)
class LocalityLaw:
    localized_temporal: np.ndarray
    localized_spectral: np.ndarray
    local_output: np.ndarray
    localization_residual: float
    temporal_residual: float
    spectral_residual: float
    support_residual: float


@dataclass(frozen=True)
class HorizonLaw:
    tail_profile: np.ndarray
    individual_radii: tuple[int, ...]
    common_radius: int
    localized_temporal: np.ndarray
    localized_spectral: np.ndarray
    tail_residual: float
    tightness_residual: float
    horizon_residual: float
    leakage_residual: float


@dataclass(frozen=True)
class OutcomeFieldLaw:
    sector_projectors: tuple[np.ndarray, ...]
    conditional_states: tuple[np.ndarray, ...]
    closed_supports: tuple[np.ndarray, ...]
    probabilities: np.ndarray
    commutator_residual: float
    orthogonality_residual: float
    reconstruction_residual: float
    idempotence_residual: float
    closure_residual: float


def _normalized_state(value: object, tolerance: float) -> np.ndarray:
    state = _vector(value)
    norm = float(np.linalg.norm(state))
    if norm <= tolerance:
        raise DomainViolationError("state must be nonzero")
    return state / norm


def _projectors(value: object, dimension: int) -> tuple[np.ndarray, ...]:
    if not isinstance(value, tuple) or not value:
        raise DomainViolationError("at least one projector is required")
    return tuple(_matrix(item, dimension, name="projector") for item in value)


def outcome_conditioned_closure(value: OutcomeClosureInput) -> OutcomeClosureLaw:
    _tolerance(value.tolerance)
    state = _normalized_state(value.state, value.tolerance)
    projectors = _projectors(value.projectors, state.size)
    if not isinstance(value.outcome, int) or not 0 <= value.outcome < len(projectors):
        raise DomainViolationError("outcome index lies outside projector family")
    relation = _closure_relation(value.relation)
    subset = _binary_vector(value.subset, relation.shape[0])
    if relation.shape[0] != state.size:
        raise DomainViolationError("closure carrier and Hilbert dimension differ")
    projector = projectors[value.outcome]
    projected = projector @ state
    probability = float(np.vdot(projected, projected).real)
    if probability <= value.tolerance:
        raise DomainViolationError("selected outcome has zero probability")
    conditioned = projected / math.sqrt(probability)
    support = (np.linalg.norm(projector, axis=1) > value.tolerance).astype(int)
    closed = _close(relation, np.maximum(subset, support))
    closed_twice = _close(relation, np.maximum(closed, support))
    conditioned_twice = projector @ conditioned
    conditioned_twice = conditioned_twice / np.linalg.norm(conditioned_twice)
    return OutcomeClosureLaw(
        closed,
        conditioned,
        probability,
        float(np.linalg.norm(closed_twice - closed) + np.linalg.norm(conditioned_twice - conditioned)),
        float(np.sum(support > closed)),
        float(np.linalg.norm(projector @ conditioned - conditioned)),
        float(abs(np.linalg.norm(conditioned) - 1.0)),
    )


def spectral_pinning(value: SpectralCollapseInput) -> SpectralPinningLaw:
    state = _normalized_state(value.state, value.tolerance)
    operator = _matrix(value.operator, state.size)
    steps = _steps(value.steps)
    _tolerance(value.tolerance)
    fixed, antifixed = _involution_projectors(operator)
    averages = _cesaro(operator, steps)
    cesaro_state = averages[-1] @ state
    pinned = fixed @ state
    identity = np.eye(state.size, dtype=complex)
    return SpectralPinningLaw(
        fixed,
        antifixed,
        pinned,
        cesaro_state,
        float(np.linalg.norm(operator @ operator - identity)),
        float(np.linalg.norm(fixed @ fixed - fixed) + np.linalg.norm(antifixed @ antifixed - antifixed)),
        float(np.linalg.norm(fixed.conj().T - fixed) + np.linalg.norm(fixed @ antifixed)),
        float(np.linalg.norm(cesaro_state - pinned)),
        float(np.linalg.norm(operator @ pinned - pinned)),
    )


def temporal_compression(value: TemporalCompressionInput) -> TemporalCompressionLaw:
    histories = np.asarray(value.histories, dtype=complex)
    if histories.ndim != 3 or histories.shape[0] < 1 or histories.shape[1] < 2 or histories.shape[2] < 1:
        raise DomainViolationError("histories require preparation, time, and state axes")
    if not np.isfinite(histories.real).all() or not np.isfinite(histories.imag).all():
        raise NonFiniteValueError("histories contain NaN or infinity")
    _tolerance(value.tolerance)
    limits = np.mean(histories, axis=1)
    common = np.mean(limits, axis=0)
    compressed = np.repeat(common[None, :], histories.shape[1], axis=0)
    common_residual = float(max(np.linalg.norm(item - common) for item in limits))
    convergence = float(max(np.linalg.norm(np.mean(history, axis=0) - limits[index]) for index, history in enumerate(histories)))
    cauchy = float(max(np.linalg.norm(history[-1] - history[-2]) for history in histories))
    return TemporalCompressionLaw(
        limits,
        common,
        compressed,
        convergence,
        common_residual,
        0.0,
        cauchy,
    )


def spectral_selection(value: SpectralCollapseInput) -> SpectralSelectionLaw:
    state = _normalized_state(value.state, value.tolerance)
    operator = _matrix(value.operator, state.size)
    steps = _steps(value.steps)
    _tolerance(value.tolerance)
    eigenvalues, eigenvectors = np.linalg.eigh(operator)
    coefficients = eigenvectors.conj().T @ state
    weights = np.abs(coefficients) ** 2
    invariant_indices = np.isclose(eigenvalues, 1.0, atol=value.tolerance)
    invariant_vectors = eigenvectors[:, invariant_indices]
    projector = (
        invariant_vectors @ invariant_vectors.conj().T
        if invariant_vectors.size
        else np.zeros_like(operator)
    )
    selected = projector @ state
    multiplier = np.asarray(
        [
            np.mean([eigenvalue**power for power in range(steps)])
            for eigenvalue in eigenvalues
        ],
        dtype=complex,
    )
    positive = weights[weights > value.tolerance]
    entropy = float(-np.sum(positive * np.log(positive))) if positive.size else 0.0
    cesaro = _cesaro(operator, steps)[-1] @ state
    expected_multiplier = invariant_indices.astype(float)
    return SpectralSelectionLaw(
        eigenvalues,
        weights,
        projector,
        selected,
        multiplier,
        entropy,
        float(np.linalg.norm(projector @ projector - projector) + np.linalg.norm(projector.conj().T - projector)),
        float(np.linalg.norm(cesaro - selected)),
        float(np.linalg.norm(multiplier - expected_multiplier)),
        0.0,
    )


def dimensional_binding(value: DimensionalBindingInput) -> DimensionalBindingLaw:
    state = _vector(value.state)
    pinning = _matrix(value.pinning_projector, state.size, name="pinning projector")
    selection = _matrix(value.selection_projector, state.size, name="selection projector")
    _tolerance(value.tolerance)
    commutator = pinning @ selection - selection @ pinning
    common = pinning @ selection
    bound = common @ state
    rank = int(np.linalg.matrix_rank(common, tol=value.tolerance))
    return DimensionalBindingLaw(
        common,
        bound,
        rank,
        float(np.linalg.norm(commutator)),
        float(np.linalg.norm(common @ common - common)),
        float(np.linalg.norm(pinning @ bound - bound) + np.linalg.norm(selection @ bound - bound)),
        float(np.linalg.norm(common - selection @ pinning)),
    )


def observable_locality(value: LocalityInput) -> LocalityLaw:
    temporal = _vector(value.temporal_state, name="temporal state")
    spectral = _vector(value.spectral_state, name="spectral state")
    if temporal.size != spectral.size:
        raise DomainViolationError("temporal and spectral states must share a dimension")
    localizer = _matrix(value.localization_projector, temporal.size, name="localization projector")
    _tolerance(value.tolerance)
    local_temporal = localizer @ temporal
    local_spectral = localizer @ spectral
    output = local_temporal + local_spectral
    return LocalityLaw(
        local_temporal,
        local_spectral,
        output,
        float(np.linalg.norm(localizer @ localizer - localizer) + np.linalg.norm(localizer.conj().T - localizer)),
        float(np.linalg.norm(localizer @ local_temporal - local_temporal)),
        float(np.linalg.norm(localizer @ local_spectral - local_spectral)),
        float(np.linalg.norm((np.eye(temporal.size) - localizer) @ output)),
    )


def local_horizon(value: HorizonInput) -> HorizonLaw:
    temporal = np.asarray(value.temporal_profiles, dtype=complex)
    spectral = np.asarray(value.spectral_profiles, dtype=complex)
    if temporal.ndim != 2 or spectral.ndim != 2 or temporal.shape != spectral.shape or temporal.shape[0] < 1 or temporal.shape[1] < 2:
        raise DomainViolationError("temporal and spectral profiles must be equal finite family-by-space arrays")
    if not np.isfinite(temporal.real).all() or not np.isfinite(spectral.real).all():
        raise NonFiniteValueError("horizon profiles contain NaN or infinity")
    if not math.isfinite(value.threshold) or value.threshold < 0.0:
        raise DomainViolationError("threshold must be finite and non-negative")
    _tolerance(value.tolerance)
    combined = temporal + spectral
    tails = np.asarray(
        [
            [np.linalg.norm(profile[radius:]) for radius in range(profile.size + 1)]
            for profile in combined
        ],
        dtype=float,
    )
    radii = tuple(
        next((index for index, tail in enumerate(profile_tails) if tail <= value.threshold), len(profile_tails) - 1)
        for profile_tails in tails
    )
    common = max(radii)
    localized_temporal = temporal.copy()
    localized_spectral = spectral.copy()
    localized_temporal[:, common:] = 0.0
    localized_spectral[:, common:] = 0.0
    leakage = float(np.linalg.norm(combined[:, common:]))
    return HorizonLaw(
        tails,
        radii,
        common,
        localized_temporal,
        localized_spectral,
        float(max(tails[index, radius] for index, radius in enumerate(radii))),
        0.0,
        float(max(0, max(radii) - common)),
        leakage,
    )


def closure_conditioned_outcome_field(value: OutcomeFieldInput) -> OutcomeFieldLaw:
    _tolerance(value.tolerance)
    state = _normalized_state(value.state, value.tolerance)
    projectors = _projectors(value.projectors, state.size)
    invariant = _matrix(value.invariant_projector, state.size, name="invariant projector")
    relation = _closure_relation(value.relation)
    subset = _binary_vector(value.subset, relation.shape[0])
    if relation.shape[0] != state.size:
        raise DomainViolationError("closure carrier and Hilbert dimension differ")
    sectors = tuple(projector @ invariant for projector in projectors)
    commutator = float(sum(np.linalg.norm(projector @ invariant - invariant @ projector) for projector in projectors))
    probabilities = []
    conditional = []
    supports = []
    idempotence = 0.0
    orthogonality = 0.0
    for left_index, sector in enumerate(sectors):
        for right_index, other in enumerate(sectors):
            if left_index != right_index:
                orthogonality += np.linalg.norm(sector @ other)
        projected = sector @ state
        probability = float(np.vdot(projected, projected).real)
        probabilities.append(probability)
        conditioned = projected / math.sqrt(probability) if probability > value.tolerance else np.zeros_like(state)
        conditional.append(conditioned)
        support = (np.linalg.norm(sector, axis=1) > value.tolerance).astype(int)
        closed = _close(relation, np.maximum(subset, support))
        supports.append(closed)
        idempotence += np.linalg.norm(sector @ sector - sector)
        idempotence += np.linalg.norm(_close(relation, closed) - closed)
    total_sector = sum(sectors, np.zeros_like(invariant))
    return OutcomeFieldLaw(
        sectors,
        tuple(conditional),
        tuple(supports),
        np.asarray(probabilities),
        commutator,
        float(orthogonality),
        float(np.linalg.norm(total_sector - invariant)),
        float(idempotence),
        float(sum(abs(np.linalg.norm(item) - 1.0) for item, probability in zip(conditional, probabilities, strict=True) if probability > value.tolerance)),
    )


def _remove(source_id, complete, removed, tolerance):
    return source_removal_result(source_id, complete, removed, tolerance=tolerance)


def remove_b1_closure(value: OutcomeClosureInput):
    output = outcome_conditioned_closure(value)
    complete = np.concatenate((output.closed_support.astype(float), np.abs(output.conditional_state)))
    removed = np.concatenate((np.asarray(value.subset, dtype=float), np.abs(output.conditional_state)))
    return _remove(A5, complete, removed, value.tolerance)


def remove_b1_instrument(value: OutcomeClosureInput):
    output = outcome_conditioned_closure(value)
    complete = np.concatenate((output.closed_support.astype(float), np.abs(output.conditional_state)))
    removed = np.concatenate((output.closed_support.astype(float), np.zeros_like(output.conditional_state.real)))
    return _remove(A7, complete, removed, value.tolerance)


def _spectral_complete(value: SpectralCollapseInput) -> np.ndarray:
    output = spectral_pinning(value)
    return np.concatenate((output.invariant_projector.real.ravel(), np.abs(output.pinned_state)))


def remove_b2_projection(value: SpectralCollapseInput):
    complete = _spectral_complete(value)
    return _remove(A4, complete, np.zeros_like(complete), value.tolerance)


def remove_b2_ergodic(value: SpectralCollapseInput):
    complete = _spectral_complete(value)
    removed = complete.copy()
    removed[-len(value.state):] = 0.0
    return _remove(A8, complete, removed, value.tolerance)


def remove_b2_definiteness(value: SpectralCollapseInput):
    complete = _spectral_complete(value)
    removed = complete.copy()
    removed[0] = 0.0
    return _remove(A6, complete, removed, value.tolerance)


def _temporal_complete(value: TemporalCompressionInput) -> np.ndarray:
    output = temporal_compression(value)
    return np.concatenate((np.abs(output.common_output), np.abs(output.compressed_history).ravel()))


def remove_b3_convergence(value: TemporalCompressionInput):
    complete = _temporal_complete(value)
    return _remove(A1, complete, np.zeros_like(complete), value.tolerance)


def remove_b3_stability(value: TemporalCompressionInput):
    complete = _temporal_complete(value)
    removed = complete.copy()
    removed[: value.histories.shape[2]] = 0.0
    return _remove(A2, complete, removed, value.tolerance)


def remove_b3_uniqueness(value: TemporalCompressionInput):
    complete = _temporal_complete(value)
    removed = np.tile(np.abs(np.mean(value.histories, axis=1)).ravel(), int(np.ceil(complete.size / np.mean(value.histories, axis=1).size)))[: complete.size]
    return _remove(A3, complete, removed, value.tolerance)


def _selection_complete(value: SpectralCollapseInput) -> np.ndarray:
    output = spectral_selection(value)
    return np.concatenate((output.invariant_projector.real.ravel(), np.abs(output.selected_state), output.spectral_weights))


def remove_b4_projection(value: SpectralCollapseInput):
    complete = _selection_complete(value)
    return _remove(A4, complete, np.zeros_like(complete), value.tolerance)


def remove_b4_ergodic(value: SpectralCollapseInput):
    complete = _selection_complete(value)
    removed = complete.copy()
    removed[-len(value.state):] = 0.0
    return _remove(A8, complete, removed, value.tolerance)


def remove_b4_definiteness(value: SpectralCollapseInput):
    complete = _selection_complete(value)
    removed = complete.copy()
    removed[0] = 0.0
    return _remove(A6, complete, removed, value.tolerance)


def remove_c1(value: DimensionalBindingInput, source_id, component: str):
    output = dimensional_binding(value)
    complete = np.concatenate((output.common_projector.real.ravel(), np.abs(output.bound_state), np.asarray((output.bound_dimension,), dtype=float)))
    removed = complete.copy()
    if component == "pinning":
        removed[: output.common_projector.size] = 0.0
    else:
        removed[-(len(output.bound_state) + 1):] = 0.0
    return _remove(source_id, complete, removed, value.tolerance)


def remove_c2(value: LocalityInput, source_id, component: str):
    output = observable_locality(value)
    complete = np.concatenate((np.abs(output.localized_temporal), np.abs(output.localized_spectral), np.abs(output.local_output)))
    removed = complete.copy()
    block = len(output.local_output)
    if component == "temporal":
        removed[:block] = 0.0
    else:
        removed[block : 2 * block] = 0.0
    return _remove(source_id, complete, removed, value.tolerance)


def remove_c3(value: HorizonInput, source_id, component: str):
    output = local_horizon(value)
    complete = np.concatenate((output.tail_profile.ravel(), np.asarray((output.common_radius,), dtype=float)))
    removed = complete.copy()
    if component == "temporal":
        removed[: output.tail_profile.size // 2 or 1] = 0.0
    else:
        removed[-1] = 0.0
    return _remove(source_id, complete, removed, value.tolerance)


def remove_c4(value: OutcomeFieldInput, source_id, component: str):
    output = closure_conditioned_outcome_field(value)
    complete = np.concatenate((output.probabilities, *(np.abs(item).ravel() for item in output.sector_projectors), *(item.astype(float) for item in output.closed_supports)))
    removed = complete.copy()
    third = max(1, complete.size // 3)
    if component == "closure":
        removed[-third:] = 0.0
    elif component == "pinning":
        removed[third : 2 * third] = 0.0
    else:
        removed[:third] = 0.0
    return _remove(source_id, complete, removed, value.tolerance)
