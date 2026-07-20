"""Canonical A-level operators for Observation and Collapse.

The module implements finite typed witnesses for the eight authoritative
A-level laws. Cesaro, projection, closure, stabilization, and instrument
identities are evaluated exactly on finite carriers. These witnesses support
runtime verification and do not replace the appendix's asymptotic or
measure-theoretic proofs.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ClosureStatus,
    ComplexId,
    ResidualResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
    NonFiniteValueError,
)

APPENDIX = "appendix_tne_foundational_closure_architecture.tex"
APPENDIX_SHA256 = "5e459eed3eca36d1342bc879fc8ac3962f3c801bfd1aab733f3db081a7ed0c69"
IMPLEMENTATION = (
    "the_nothingness_effect/foundational_architecture/observation_and_collapse/"
    "canonical_contracts.py"
)

A1 = ComplexId("observation_induced_collapse_and_collapse_divergence")
A2 = ComplexId("collapse_attractor_stability_and_attractor_instability")
A3 = ComplexId("uniqueness_and_non_uniqueness_of_collapse")
A4 = ComplexId("hilbert_projection_realization_and_projection_breakdown")
A5 = ComplexId("fixed_point_consistency_and_trivial_collapse_failure")
A6 = ComplexId("observation_definiteness_equivalence_and_closure_failure")
A7 = ComplexId("definite_state_projection_and_state_ambiguity")
A8 = ComplexId("ergodic_collapse_projection_and_non_convergence")
B1 = ComplexId("outcome_conditioned_closure_instrument")
B2 = ComplexId("involutive_collapse_spectral_pinning_and_spectral_drift")
B3 = ComplexId("temporal_compression_and_frozen_time_obstruction")
B4 = ComplexId("collapse_spectral_selection_and_spectral_ambiguity")
C1 = ComplexId("observation_dimensional_binding_and_dimensional_non_binding")
C2 = ComplexId("observable_locality_and_collapse_inaccessibility")
C3 = ComplexId("local_horizon_boundary_and_non_locality_divergence")
C4 = ComplexId("closure_conditioned_spectral_outcome_field")


@dataclass(frozen=True)
class MeanErgodicInput:
    operator: np.ndarray
    state: np.ndarray
    steps: int = 8
    tolerance: float = 1e-10


@dataclass(frozen=True)
class AttractorInput:
    attractor: np.ndarray
    perturbations: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class UniquenessInput:
    histories: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class ClosureInput:
    relation: np.ndarray
    subset: np.ndarray
    comparison_subset: np.ndarray
    tolerance: float = 0.0


@dataclass(frozen=True)
class StabilizationInput:
    transition: tuple[int, ...]
    initial_states: tuple[int, ...]
    max_steps: int = 16
    tolerance: float = 0.0


@dataclass(frozen=True)
class InstrumentInput:
    projectors: tuple[np.ndarray, ...]
    state: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class MeanErgodicLaw:
    averages: np.ndarray
    collapse: np.ndarray
    fixed_projector: np.ndarray
    fixed_component: np.ndarray
    operator_involution_residual: float
    fixed_residual: float
    convergence_residual: float
    cauchy_residual: float


@dataclass(frozen=True)
class AttractorLaw:
    empirical_averages: np.ndarray
    terminal_average: np.ndarray
    shifted_attractor: np.ndarray
    zero_mean_residual: float
    attractor_residual: float
    stability_bound_residual: float


@dataclass(frozen=True)
class UniquenessLaw:
    preparation_limits: np.ndarray
    cluster_diameter: float
    unique_limit: np.ndarray
    pathwise_residual: float
    singleton_residual: float
    ensemble_residual: float


@dataclass(frozen=True)
class ProjectionLaw:
    fixed_projector: np.ndarray
    antifixed_projector: np.ndarray
    cesaro_operator: np.ndarray
    selected_state: np.ndarray
    involution_residual: float
    unitary_residual: float
    idempotence_residual: float
    orthogonality_residual: float
    convergence_residual: float


@dataclass(frozen=True)
class ClosureLaw:
    closed_subset: np.ndarray
    comparison_closed_subset: np.ndarray
    fixed_points: tuple[tuple[int, ...], ...]
    monotonicity_residual: float
    extensivity_residual: float
    idempotence_residual: float
    output_fixed_residual: float


@dataclass(frozen=True)
class StabilizationLaw:
    terminal_states: tuple[int, ...]
    stabilization_depths: tuple[int, ...]
    failure_states: tuple[int, ...]
    output_fixed_residual: float
    eventual_idempotence_residual: float
    partition_residual: float


@dataclass(frozen=True)
class InstrumentLaw:
    probabilities: np.ndarray
    conditional_states: tuple[np.ndarray, ...]
    completeness_residual: float
    orthogonality_residual: float
    probability_residual: float
    repeatability_residual: float
    state_normalization_residual: float


@dataclass(frozen=True)
class ErgodicProjectionLaw:
    algebraic_projector: np.ndarray
    averages: np.ndarray
    selected_state: np.ndarray
    involution_residual: float
    idempotence_residual: float
    fixed_range_residual: float
    orthogonality_residual: float
    convergence_residual: float


def _tolerance(value: float) -> float:
    if not math.isfinite(value) or value < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    return float(value)


def _steps(value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 2:
        raise DomainViolationError("steps must be an integer >= 2")
    return value


def _vector(value: object, *, name: str = "state") -> np.ndarray:
    result = np.asarray(value, dtype=complex)
    if result.ndim != 1 or result.size < 1:
        raise DomainViolationError(f"{name} must be a nonempty vector")
    if not np.isfinite(result.real).all() or not np.isfinite(result.imag).all():
        raise NonFiniteValueError(f"{name} contains NaN or infinity")
    return result


def _matrix(value: object, dimension: int | None = None, *, name: str = "operator") -> np.ndarray:
    result = np.asarray(value, dtype=complex)
    if result.ndim != 2 or result.shape[0] != result.shape[1] or result.shape[0] < 1:
        raise DomainViolationError(f"{name} must be a finite square matrix")
    if dimension is not None and result.shape != (dimension, dimension):
        raise DomainViolationError(f"{name} dimension does not match state")
    if not np.isfinite(result.real).all() or not np.isfinite(result.imag).all():
        raise NonFiniteValueError(f"{name} contains NaN or infinity")
    return result


def _binary_vector(value: object, length: int | None = None) -> np.ndarray:
    result = np.asarray(value, dtype=int)
    if result.ndim != 1 or result.size < 1 or not np.isin(result, (0, 1)).all():
        raise DomainViolationError("subset must be a nonempty binary vector")
    if length is not None and result.size != length:
        raise DomainViolationError("subset length does not match relation")
    return result


def _residual(name: str, values: Iterable[float], tolerance: float) -> ResidualResult:
    vector = tuple(float(item) for item in values)
    if any(not math.isfinite(item) for item in vector):
        raise NonFiniteValueError(f"{name} contains NaN or infinity")
    norm = float(np.linalg.norm(vector))
    passed = norm <= tolerance
    return ResidualResult(
        name,
        vector,
        tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
    )


def _cesaro(operator: np.ndarray, steps: int) -> np.ndarray:
    identity = np.eye(operator.shape[0], dtype=complex)
    power = identity.copy()
    total = np.zeros_like(operator)
    averages = []
    for index in range(1, steps + 1):
        total = total + power
        averages.append(total / index)
        power = power @ operator
    return np.stack(averages)


def _involution_projectors(operator: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    identity = np.eye(operator.shape[0], dtype=complex)
    return 0.5 * (identity + operator), 0.5 * (identity - operator)


def mean_ergodic_collapse(value: MeanErgodicInput) -> MeanErgodicLaw:
    state = _vector(value.state)
    operator = _matrix(value.operator, state.size)
    steps = _steps(value.steps)
    _tolerance(value.tolerance)
    averages_op = _cesaro(operator, steps)
    averages = np.stack([item @ state for item in averages_op])
    fixed, _ = _involution_projectors(operator)
    fixed_component = fixed @ state
    collapse = averages[-1]
    return MeanErgodicLaw(
        averages,
        collapse,
        fixed,
        fixed_component,
        float(np.linalg.norm(operator @ operator - np.eye(state.size))),
        float(np.linalg.norm(operator @ collapse - collapse)),
        float(np.linalg.norm(collapse - fixed_component)),
        float(np.linalg.norm(averages[-1] - averages[-2])),
    )


def attractor_stability(value: AttractorInput) -> AttractorLaw:
    attractor = _vector(value.attractor, name="attractor")
    perturbations = np.asarray(value.perturbations, dtype=complex)
    if perturbations.ndim != 2 or perturbations.shape[1] != attractor.size or perturbations.shape[0] < 2:
        raise DomainViolationError("perturbations must be a finite time-by-state array")
    if not np.isfinite(perturbations.real).all() or not np.isfinite(perturbations.imag).all():
        raise NonFiniteValueError("perturbations contain NaN or infinity")
    _tolerance(value.tolerance)
    histories = attractor[None, :] + perturbations
    averages = np.cumsum(histories, axis=0) / np.arange(1, len(histories) + 1)[:, None]
    terminal = averages[-1]
    mean_perturbation = np.mean(perturbations, axis=0)
    shifted = attractor + mean_perturbation
    bound = np.linalg.norm(mean_perturbation)
    return AttractorLaw(
        averages,
        terminal,
        shifted,
        float(np.linalg.norm(mean_perturbation)),
        float(np.linalg.norm(terminal - shifted)),
        float(max(0.0, np.linalg.norm(terminal - attractor) - bound)),
    )


def uniqueness_classification(value: UniquenessInput) -> UniquenessLaw:
    histories = np.asarray(value.histories, dtype=complex)
    if histories.ndim != 3 or histories.shape[0] < 1 or histories.shape[1] < 2 or histories.shape[2] < 1:
        raise DomainViolationError("histories must have preparation, time, and state axes")
    if not np.isfinite(histories.real).all() or not np.isfinite(histories.imag).all():
        raise NonFiniteValueError("histories contain NaN or infinity")
    _tolerance(value.tolerance)
    limits = np.mean(histories, axis=1)
    center = np.mean(limits, axis=0)
    diameter = max(
        (float(np.linalg.norm(left - right)) for left in limits for right in limits),
        default=0.0,
    )
    pathwise = float(
        max(np.linalg.norm(np.mean(history, axis=0) - limits[index]) for index, history in enumerate(histories))
    )
    return UniquenessLaw(
        limits,
        diameter,
        center,
        pathwise,
        float(diameter),
        float(max(np.linalg.norm(item - center) for item in limits)),
    )


def hilbert_projection(value: MeanErgodicInput) -> ProjectionLaw:
    state = _vector(value.state)
    operator = _matrix(value.operator, state.size)
    steps = _steps(value.steps)
    _tolerance(value.tolerance)
    fixed, antifixed = _involution_projectors(operator)
    cesaro = _cesaro(operator, steps)[-1]
    selected = fixed @ state
    identity = np.eye(state.size, dtype=complex)
    return ProjectionLaw(
        fixed,
        antifixed,
        cesaro,
        selected,
        float(np.linalg.norm(operator @ operator - identity)),
        float(np.linalg.norm(operator.conj().T @ operator - identity)),
        float(np.linalg.norm(fixed @ fixed - fixed) + np.linalg.norm(antifixed @ antifixed - antifixed)),
        float(np.linalg.norm(fixed @ antifixed) + np.linalg.norm(fixed.conj().T - fixed)),
        float(np.linalg.norm(cesaro @ state - selected)),
    )


def _closure_relation(value: object) -> np.ndarray:
    relation = np.asarray(value, dtype=int)
    if relation.ndim != 2 or relation.shape[0] != relation.shape[1] or relation.shape[0] < 1:
        raise DomainViolationError("closure relation must be a square binary matrix")
    if not np.isin(relation, (0, 1)).all():
        raise DomainViolationError("closure relation must be binary")
    relation = relation.copy()
    np.fill_diagonal(relation, 1)
    for pivot in range(relation.shape[0]):
        relation = np.maximum(relation, relation[:, pivot, None] * relation[pivot, None, :])
    return relation


def _close(relation: np.ndarray, subset: np.ndarray) -> np.ndarray:
    active = np.flatnonzero(subset)
    if active.size == 0:
        return subset.copy()
    return np.max(relation[active], axis=0).astype(int)


def closure_consistency(value: ClosureInput) -> ClosureLaw:
    relation = _closure_relation(value.relation)
    subset = _binary_vector(value.subset, relation.shape[0])
    comparison = _binary_vector(value.comparison_subset, relation.shape[0])
    _tolerance(value.tolerance)
    closed = _close(relation, subset)
    comparison_closed = _close(relation, comparison)
    closed_twice = _close(relation, closed)
    monotone_applicable = bool(np.all(subset <= comparison))
    monotone_residual = (
        float(np.sum(closed > comparison_closed)) if monotone_applicable else 0.0
    )
    fixed_points = tuple(
        tuple(int(item) for item in mask)
        for mask_value in range(2 ** relation.shape[0])
        for mask in [np.asarray([(mask_value >> index) & 1 for index in range(relation.shape[0])], dtype=int)]
        if np.array_equal(_close(relation, mask), mask)
    )
    return ClosureLaw(
        closed,
        comparison_closed,
        fixed_points,
        monotone_residual,
        float(np.sum(subset > closed)),
        float(np.linalg.norm(closed_twice - closed)),
        float(np.linalg.norm(_close(relation, closed) - closed)),
    )


def stabilization_classification(value: StabilizationInput) -> StabilizationLaw:
    transition = tuple(int(item) for item in value.transition)
    if not transition or any(item < 0 or item >= len(transition) for item in transition):
        raise DomainViolationError("transition must map a finite state set to itself")
    if not value.initial_states or any(item < 0 or item >= len(transition) for item in value.initial_states):
        raise DomainViolationError("initial states must lie in the transition carrier")
    if not isinstance(value.max_steps, int) or value.max_steps < 1:
        raise DomainViolationError("max_steps must be positive")
    _tolerance(value.tolerance)
    terminal = []
    depths = []
    failures = []
    for source in value.initial_states:
        current = source
        depth = -1
        for step in range(value.max_steps + 1):
            next_state = transition[current]
            if next_state == current:
                depth = step
                break
            current = next_state
        terminal.append(current)
        depths.append(depth)
        if depth < 0:
            failures.append(source)
    fixed_residual = float(sum(transition[item] != item for item, depth in zip(terminal, depths, strict=True) if depth >= 0))
    partition_residual = float(len(value.initial_states) - (sum(depth >= 0 for depth in depths) + len(failures)))
    return StabilizationLaw(
        tuple(terminal),
        tuple(depths),
        tuple(failures),
        fixed_residual,
        fixed_residual,
        partition_residual,
    )


def instrument_realization(value: InstrumentInput) -> InstrumentLaw:
    state = _vector(value.state)
    norm = np.linalg.norm(state)
    if norm <= value.tolerance:
        raise DomainViolationError("instrument state must be nonzero")
    state = state / norm
    projectors = tuple(_matrix(item, state.size, name="projector") for item in value.projectors)
    if not projectors:
        raise DomainViolationError("at least one projector is required")
    _tolerance(value.tolerance)
    identity = np.eye(state.size, dtype=complex)
    total = sum(projectors, np.zeros_like(identity))
    orthogonality = 0.0
    repeatability = 0.0
    probabilities = []
    conditional = []
    for left_index, left in enumerate(projectors):
        orthogonality += np.linalg.norm(left @ left - left) + np.linalg.norm(left.conj().T - left)
        for right_index, right in enumerate(projectors):
            if left_index != right_index:
                orthogonality += np.linalg.norm(left @ right)
        projected = left @ state
        probability = float(np.vdot(projected, projected).real)
        probabilities.append(probability)
        if probability > value.tolerance:
            conditioned = projected / math.sqrt(probability)
            repeatability += np.linalg.norm(left @ conditioned - conditioned)
        else:
            conditioned = np.zeros_like(state)
        conditional.append(conditioned)
    return InstrumentLaw(
        np.asarray(probabilities),
        tuple(conditional),
        float(np.linalg.norm(total - identity)),
        float(orthogonality),
        float(abs(sum(probabilities) - 1.0)),
        float(repeatability),
        float(abs(np.linalg.norm(state) - 1.0)),
    )


def ergodic_projection(value: MeanErgodicInput) -> ErgodicProjectionLaw:
    state = _vector(value.state)
    operator = _matrix(value.operator, state.size)
    steps = _steps(value.steps)
    _tolerance(value.tolerance)
    identity = np.eye(state.size, dtype=complex)
    projector = 0.5 * (identity + operator)
    averages_op = _cesaro(operator, steps)
    averages = np.stack([item @ state for item in averages_op])
    selected = projector @ state
    return ErgodicProjectionLaw(
        projector,
        averages,
        selected,
        float(np.linalg.norm(operator @ operator - identity)),
        float(np.linalg.norm(projector @ projector - projector)),
        float(np.linalg.norm(operator @ selected - selected)),
        float(np.linalg.norm(projector.conj().T - projector)),
        float(np.linalg.norm(averages[-1] - selected)),
    )
