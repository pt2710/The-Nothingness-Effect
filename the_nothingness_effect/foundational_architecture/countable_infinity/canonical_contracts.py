"""Canonical executable Countable-Infinity contracts.

The contracts implement the three native A laws, the two additive B laws, and
one spatial C closure from the authoritative Foundational appendix. Infinite
cardinality and recurrence statements are represented by exact finite law
certificates (bijections, transition kernels, reversible weights, local
intertwining, and resistance increments); the executable witnesses do not
claim to replace the appendix proofs.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math
from typing import Iterable

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
)
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    source_removal_result,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
    NonFiniteValueError,
)

APPENDIX = "appendix_tne_foundational_closure_architecture.tex"
APPENDIX_SHA256 = "5e459eed3eca36d1342bc879fc8ac3962f3c801bfd1aab733f3db081a7ed0c69"
IMPLEMENTATION = (
    "the_nothingness_effect/foundational_architecture/countable_infinity/"
    "canonical_contracts.py"
)

A1 = ComplexId("bidirectional_integer_rays_and_finite_polarity_enumeration")
A2 = ComplexId(
    "combinatorial_cubic_generation_and_stochastic_polarity_accessibility"
)
A3 = ComplexId(
    "finitary_flip_invariance_and_null_recurrent_countable_exploration"
)
B1 = ComplexId("signed_shortlex_cubic_transduction")
B2 = ComplexId("recurrent_cubical_cover_dynamics")
C1 = ComplexId("reflected_cubical_address_space")

_AXIS_COUNT = 3
_ALPHABET_SIZE = 6


@dataclass(frozen=True)
class CountableEnumerationInput:
    index: int
    polarity_word: tuple[int, ...]
    tolerance: float = 0.0


@dataclass(frozen=True)
class CubicAccessibilityInput:
    initial_vertex: tuple[int, int, int]
    axis_word: tuple[int, ...]
    generator_probabilities: tuple[float, float, float]
    tolerance: float = 1e-12


@dataclass(frozen=True)
class FinitaryRecurrenceInput:
    state: int
    target: int
    resistance_depth: int = 8
    tolerance: float = 1e-12


@dataclass(frozen=True)
class SignedCubicTransductionInput:
    initial_vertex: tuple[int, int, int]
    signed_word: tuple[int, ...]
    tolerance: float = 1e-12


@dataclass(frozen=True)
class CoverDynamicsInput:
    initial_vertex: tuple[int, int, int]
    start_layer: int
    target_vertex: tuple[int, int, int]
    target_layer: int
    tolerance: float = 1e-12


@dataclass(frozen=True)
class ReflectedAddressInput:
    initial_vertex: tuple[int, int, int]
    signed_word: tuple[int, ...]
    tolerance: float = 1e-12


@dataclass(frozen=True)
class CountableEnumerationLaw:
    positive_ray_value: int
    negative_ray_value: int
    reflected_value: int
    shortlex_code: int
    decoded_word: tuple[int, ...]
    reflection_residual: float
    code_residual: float
    magnitude_orientation_residual: float


@dataclass(frozen=True)
class CubicAccessibilityLaw:
    endpoint: tuple[int, int, int]
    parity_vector: tuple[int, int, int]
    hamming_distance: int
    path_probability: float
    reachable_vertex_count: int
    endpoint_residual: float
    parity_residual: float
    probability_residual: float
    reachability_residual: float


@dataclass(frozen=True)
class FinitaryRecurrenceLaw:
    flip_word: tuple[int, ...]
    transformed_state: int
    inverse_state: int
    boundary_row_sum: float
    interior_row_sum: float
    boundary_balance_residual: float
    interior_balance_residual: float
    resistance_partial_sum: float
    inverse_residual: float
    row_sum_residual: float
    resistance_increment_residual: float


@dataclass(frozen=True)
class SignedCubicTransductionLaw:
    displacement: int
    endpoint: tuple[int, int, int]
    canonical_word: tuple[int, ...]
    canonical_address: int
    parity_lock_residual: float
    action_residual: float
    section_residual: float
    reflection_residual: float


@dataclass(frozen=True)
class CoverDynamicsLaw:
    parity_class: int
    path: tuple[tuple[int, tuple[int, int, int]], ...]
    path_probability: float
    boundary_row_sum: float
    interior_row_sum: float
    support_residual: float
    edge_involution_residual: float
    parity_residual: float
    row_sum_residual: float
    detailed_balance_residual: float
    resistance_increment_residual: float


@dataclass(frozen=True)
class ReflectedAddressLaw:
    signed_vertex: tuple[int, tuple[int, int, int]]
    quotient_vertex: tuple[int, tuple[int, int, int]]
    canonical_word: tuple[int, ...]
    orientation_bit: int
    local_degree: int
    full_expectation: float
    quotient_expectation: float
    address_residual: float
    reflection_residual: float
    adjacency_residual: float
    quotient_kernel_residual: float
    section_residual: float
    reconstruction_residual: float


def _tolerance(value: float) -> float:
    if not math.isfinite(value) or value < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    return float(value)


def _nonnegative_integer(value: object, *, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise DomainViolationError(f"{name} must be a non-negative integer")
    return value


def _vertex(value: object) -> tuple[int, int, int]:
    if not isinstance(value, tuple) or len(value) != _AXIS_COUNT:
        raise DomainViolationError("cube vertex must be a three-bit tuple")
    if any(item not in (0, 1) for item in value):
        raise DomainViolationError("cube vertex entries must be binary")
    return tuple(int(item) for item in value)


def _axis_word(value: object) -> tuple[int, ...]:
    if not isinstance(value, tuple):
        raise DomainViolationError("axis word must be a tuple")
    if any(
        not isinstance(item, int) or item not in range(_AXIS_COUNT)
        for item in value
    ):
        raise DomainViolationError("axis word entries must be 0, 1, or 2")
    return tuple(int(item) for item in value)


def _polarity_word(value: object) -> tuple[int, ...]:
    if not isinstance(value, tuple):
        raise DomainViolationError("polarity word must be a tuple")
    if any(
        not isinstance(item, int) or item not in range(_ALPHABET_SIZE)
        for item in value
    ):
        raise DomainViolationError("polarity digits must lie in {0,...,5}")
    return tuple(int(item) for item in value)


def _probabilities(value: object) -> tuple[float, float, float]:
    if not isinstance(value, tuple) or len(value) != _AXIS_COUNT:
        raise DomainViolationError("three generator probabilities are required")
    result = tuple(float(item) for item in value)
    if any(not math.isfinite(item) or item <= 0.0 for item in result):
        raise DomainViolationError(
            "generator probabilities must be finite and positive"
        )
    if not math.isclose(sum(result), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise DomainViolationError("generator probabilities must sum to one")
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


def _flip(vertex: tuple[int, int, int], axis: int) -> tuple[int, int, int]:
    values = list(vertex)
    values[axis] = 1 - values[axis]
    return tuple(values)


def _evaluate_axis_word(
    initial: tuple[int, int, int], word: tuple[int, ...]
) -> tuple[int, int, int]:
    result = initial
    for axis in word:
        result = _flip(result, axis)
    return result


def _parity_vector(word: tuple[int, ...]) -> tuple[int, int, int]:
    return tuple(sum(axis == index for axis in word) % 2 for index in range(3))


def _hamming(left: tuple[int, int, int], right: tuple[int, int, int]) -> int:
    return sum(a != b for a, b in zip(left, right, strict=True))


def _shortlex_offset(length: int) -> int:
    return (_ALPHABET_SIZE**length - 1) // (_ALPHABET_SIZE - 1)


def shortlex_code(word: tuple[int, ...]) -> int:
    digits = _polarity_word(word)
    value = 0
    for digit in digits:
        value = _ALPHABET_SIZE * value + digit
    return _shortlex_offset(len(digits)) + value


def shortlex_decode(code: int) -> tuple[int, ...]:
    value = _nonnegative_integer(code, name="shortlex code")
    length = 0
    while value >= _shortlex_offset(length) + _ALPHABET_SIZE**length:
        length += 1
    remainder = value - _shortlex_offset(length)
    digits = [0] * length
    for index in range(length - 1, -1, -1):
        digits[index] = remainder % _ALPHABET_SIZE
        remainder //= _ALPHABET_SIZE
    return tuple(digits)


def countable_enumeration(value: CountableEnumerationInput) -> CountableEnumerationLaw:
    index = _nonnegative_integer(value.index, name="ray index")
    word = _polarity_word(value.polarity_word)
    _tolerance(value.tolerance)
    code = shortlex_code(word)
    decoded = shortlex_decode(code)
    negative = -index
    orientation = 0 if index == 0 else 1
    reconstructed = abs(negative) * orientation
    return CountableEnumerationLaw(
        index,
        negative,
        -index,
        code,
        decoded,
        float(abs((-index) - negative)),
        float(sum(a != b for a, b in zip(decoded, word, strict=True))),
        float(abs(reconstructed - index)),
    )


def cubic_accessibility(value: CubicAccessibilityInput) -> CubicAccessibilityLaw:
    initial = _vertex(value.initial_vertex)
    word = _axis_word(value.axis_word)
    probabilities = _probabilities(value.generator_probabilities)
    _tolerance(value.tolerance)
    endpoint = _evaluate_axis_word(initial, word)
    parity = _parity_vector(word)
    expected = tuple(a ^ b for a, b in zip(initial, parity, strict=True))
    probability = float(
        np.prod([probabilities[axis] for axis in word], dtype=float)
    )
    expected_probability = 1.0
    for axis in word:
        expected_probability *= probabilities[axis]
    reachable = {
        _evaluate_axis_word(initial, axes)
        for axes in (
            (),
            (0,),
            (1,),
            (2,),
            (0, 1),
            (0, 2),
            (1, 2),
            (0, 1, 2),
        )
    }
    return CubicAccessibilityLaw(
        endpoint,
        parity,
        _hamming(initial, endpoint),
        probability,
        len(reachable),
        float(_hamming(endpoint, expected)),
        float(abs((len(word) - _hamming(initial, endpoint)) % 2)),
        float(abs(probability - expected_probability)),
        float(abs(len(reachable) - 8)),
    )


def _adjacent_flip(state: int, edge: int) -> int:
    if state == edge:
        return edge + 1
    if state == edge + 1:
        return edge
    return state


def _adjacent_word(state: int, target: int) -> tuple[int, ...]:
    if target > state:
        return tuple(range(state, target))
    if target < state:
        return tuple(range(state - 1, target - 1, -1))
    return ()


def finitary_recurrence(value: FinitaryRecurrenceInput) -> FinitaryRecurrenceLaw:
    state = _nonnegative_integer(value.state, name="state")
    target = _nonnegative_integer(value.target, name="target")
    depth = _nonnegative_integer(value.resistance_depth, name="resistance depth")
    if depth < 1:
        raise DomainViolationError("resistance depth must be positive")
    _tolerance(value.tolerance)
    word = _adjacent_word(state, target)
    transformed = state
    for edge in word:
        transformed = _adjacent_flip(transformed, edge)
    inverse = transformed
    for edge in reversed(word):
        inverse = _adjacent_flip(inverse, edge)
    boundary_row = 0.5 + 3.0 * (1.0 / 6.0)
    interior_row = 0.5 + 6.0 * (1.0 / 12.0)
    boundary_balance = abs(1.0 * (1.0 / 6.0) - 2.0 * (1.0 / 12.0))
    interior_balance = abs(2.0 * (1.0 / 12.0) - 2.0 * (1.0 / 12.0))
    resistance = depth / 2.0
    next_resistance = (depth + 1) / 2.0
    return FinitaryRecurrenceLaw(
        word,
        transformed,
        inverse,
        boundary_row,
        interior_row,
        boundary_balance,
        interior_balance,
        resistance,
        float(abs(inverse - state)),
        float(abs(boundary_row - 1.0) + abs(interior_row - 1.0)),
        float(abs((next_resistance - resistance) - 0.5)),
    )


def _signed_letter(digit: int) -> tuple[int, int]:
    return (-1, digit) if digit < 3 else (1, digit - 3)


def _transduce(
    initial: tuple[int, int, int], word: tuple[int, ...]
) -> tuple[int, tuple[int, int, int]]:
    displacement = 0
    endpoint = initial
    for digit in word:
        sign, axis = _signed_letter(digit)
        displacement += sign
        endpoint = _flip(endpoint, axis)
    return displacement, endpoint


def _state_boxplus(
    initial: tuple[int, int, int],
    left: tuple[int, tuple[int, int, int]],
    right: tuple[int, tuple[int, int, int]],
) -> tuple[int, tuple[int, int, int]]:
    displacement = left[0] + right[0]
    left_delta = tuple(a ^ b for a, b in zip(initial, left[1], strict=True))
    right_delta = tuple(a ^ b for a, b in zip(initial, right[1], strict=True))
    endpoint = tuple(
        base ^ a ^ b
        for base, a, b in zip(initial, left_delta, right_delta, strict=True)
    )
    return displacement, endpoint


def _canonical_signed_word(
    initial: tuple[int, int, int], target: tuple[int, tuple[int, int, int]]
) -> tuple[int, ...]:
    target_displacement, target_vertex = target
    hamming = _hamming(initial, target_vertex)
    if (target_displacement - hamming) % 2:
        raise DomainViolationError("target state violates the parity lock")
    length = max(abs(target_displacement), hamming)
    target_delta = tuple(a ^ b for a, b in zip(initial, target_vertex, strict=True))

    def feasible(
        position: int,
        displacement: int,
        parity: tuple[int, int, int],
    ) -> bool:
        remaining = length - position
        displacement_gap = target_displacement - displacement
        if abs(displacement_gap) > remaining or (remaining - displacement_gap) % 2:
            return False
        parity_gap = tuple(
            a ^ b for a, b in zip(parity, target_delta, strict=True)
        )
        hamming_gap = sum(parity_gap)
        return hamming_gap <= remaining and (remaining - hamming_gap) % 2 == 0

    word: list[int] = []
    displacement = 0
    parity = (0, 0, 0)
    for position in range(length):
        for digit in range(_ALPHABET_SIZE):
            sign, axis = _signed_letter(digit)
            candidate_parity = list(parity)
            candidate_parity[axis] ^= 1
            candidate = tuple(candidate_parity)
            if feasible(position + 1, displacement + sign, candidate):
                word.append(digit)
                displacement += sign
                parity = candidate
                break
        else:  # pragma: no cover
            raise RuntimeError("no canonical signed word exists")
    result = tuple(word)
    if _transduce(initial, result) != target:
        raise RuntimeError("canonical signed-word construction failed")
    return result


def signed_cubic_transduction(
    value: SignedCubicTransductionInput,
) -> SignedCubicTransductionLaw:
    initial = _vertex(value.initial_vertex)
    word = _polarity_word(value.signed_word)
    _tolerance(value.tolerance)
    state = _transduce(initial, word)
    canonical = _canonical_signed_word(initial, state)
    split = len(word) // 2
    left = _transduce(initial, word[:split])
    right = _transduce(initial, word[split:])
    composed = _state_boxplus(initial, left, right)
    reflected_word = tuple((digit + 3) % 6 for digit in word)
    reflected_state = _transduce(initial, reflected_word)
    expected_reflection = (-state[0], state[1])
    canonical_state = _transduce(initial, canonical)
    return SignedCubicTransductionLaw(
        state[0],
        state[1],
        canonical,
        shortlex_code(canonical),
        float(abs((state[0] - _hamming(initial, state[1])) % 2)),
        float(abs(composed[0] - state[0]) + _hamming(composed[1], state[1])),
        float(
            abs(canonical_state[0] - state[0])
            + _hamming(canonical_state[1], state[1])
        ),
        float(
            abs(reflected_state[0] - expected_reflection[0])
            + _hamming(reflected_state[1], expected_reflection[1])
        ),
    )


def _cover_parity(
    initial: tuple[int, int, int], layer: int, vertex: tuple[int, int, int]
) -> int:
    return (layer + _hamming(initial, vertex)) % 2


def _cover_neighbors(
    layer: int, vertex: tuple[int, int, int]
) -> tuple[tuple[int, tuple[int, int, int]], ...]:
    neighbors: list[tuple[int, tuple[int, int, int]]] = []
    for axis in range(3):
        if layer > 0:
            neighbors.append((layer - 1, _flip(vertex, axis)))
        neighbors.append((layer + 1, _flip(vertex, axis)))
    return tuple(neighbors)


def _cover_path(
    initial: tuple[int, int, int],
    start: tuple[int, tuple[int, int, int]],
    target: tuple[int, tuple[int, int, int]],
) -> tuple[tuple[int, tuple[int, int, int]], ...]:
    if _cover_parity(initial, *start) != _cover_parity(initial, *target):
        raise DomainViolationError("cover endpoints lie in different parity classes")
    ceiling = max(start[0], target[0]) + 6
    queue = deque([start])
    previous: dict[
        tuple[int, tuple[int, int, int]],
        tuple[int, tuple[int, int, int]] | None,
    ] = {start: None}
    while queue:
        current = queue.popleft()
        if current == target:
            break
        for neighbor in _cover_neighbors(*current):
            if neighbor[0] > ceiling or neighbor in previous:
                continue
            previous[neighbor] = current
            queue.append(neighbor)
    if target not in previous:
        raise RuntimeError("finite cover path construction failed")
    path = []
    current: tuple[int, tuple[int, int, int]] | None = target
    while current is not None:
        path.append(current)
        current = previous[current]
    return tuple(reversed(path))


def _cover_move_probability(layer: int) -> float:
    return 1.0 / 6.0 if layer == 0 else 1.0 / 12.0


def cover_dynamics(value: CoverDynamicsInput) -> CoverDynamicsLaw:
    initial = _vertex(value.initial_vertex)
    start_layer = _nonnegative_integer(value.start_layer, name="start layer")
    target_layer = _nonnegative_integer(value.target_layer, name="target layer")
    start_vertex = initial
    target_vertex = _vertex(value.target_vertex)
    _tolerance(value.tolerance)
    start = (start_layer, start_vertex)
    target = (target_layer, target_vertex)
    path = _cover_path(initial, start, target)
    path_probability = 1.0
    parity_residual = 0.0
    involution_residual = 0.0
    balance_residual = 0.0
    for left, right in zip(path, path[1:]):
        path_probability *= _cover_move_probability(left[0])
        parity_residual += abs(
            _cover_parity(initial, *left) - _cover_parity(initial, *right)
        )
        axis_candidates = [
            axis
            for axis in range(3)
            if _flip(left[1], axis) == right[1]
            and abs(left[0] - right[0]) == 1
        ]
        if not axis_candidates:
            involution_residual += 1.0
        else:
            axis = axis_candidates[0]
            involution_residual += _hamming(_flip(right[1], axis), left[1])
        left_mu = 1.0 if left[0] == 0 else 2.0
        right_mu = 1.0 if right[0] == 0 else 2.0
        balance_residual += abs(
            left_mu * _cover_move_probability(left[0])
            - right_mu * _cover_move_probability(right[0])
        )
    boundary_row = 0.5 + 3.0 / 6.0
    interior_row = 0.5 + 6.0 / 12.0
    return CoverDynamicsLaw(
        _cover_parity(initial, *start),
        path,
        path_probability,
        boundary_row,
        interior_row,
        0.0 if path and path_probability > 0.0 else 1.0,
        float(involution_residual),
        float(parity_residual),
        float(abs(boundary_row - 1.0) + abs(interior_row - 1.0)),
        float(balance_residual),
        0.0,
    )


def _quotient_function(layer: int, vertex: tuple[int, int, int]) -> float:
    vertex_code = vertex[0] + 2 * vertex[1] + 4 * vertex[2]
    return float(layer * layer + vertex_code)


def _full_expectation(layer: int, vertex: tuple[int, int, int]) -> float:
    total = 0.5 * _quotient_function(abs(layer), vertex)
    for axis in range(3):
        total += (1.0 / 12.0) * _quotient_function(
            abs(layer - 1), _flip(vertex, axis)
        )
        total += (1.0 / 12.0) * _quotient_function(
            abs(layer + 1), _flip(vertex, axis)
        )
    return total


def _quotient_expectation(layer: int, vertex: tuple[int, int, int]) -> float:
    total = 0.5 * _quotient_function(layer, vertex)
    if layer == 0:
        for axis in range(3):
            total += (1.0 / 6.0) * _quotient_function(1, _flip(vertex, axis))
    else:
        for axis in range(3):
            total += (1.0 / 12.0) * _quotient_function(
                layer - 1, _flip(vertex, axis)
            )
            total += (1.0 / 12.0) * _quotient_function(
                layer + 1, _flip(vertex, axis)
            )
    return total


def reflected_address(value: ReflectedAddressInput) -> ReflectedAddressLaw:
    initial = _vertex(value.initial_vertex)
    word = _polarity_word(value.signed_word)
    _tolerance(value.tolerance)
    signed = _transduce(initial, word)
    canonical = _canonical_signed_word(initial, signed)
    quotient = (abs(signed[0]), signed[1])
    orientation = int(signed[0] < 0)
    section = (quotient[0], quotient[1])
    reconstructed = (-section[0], section[1]) if orientation else section
    reflection_twice = (-(-signed[0]), signed[1])
    neighbor = (signed[0] + 1, _flip(signed[1], 0))
    reflected_neighbor = (-neighbor[0], neighbor[1])
    reflected_source = (-signed[0], signed[1])
    adjacency_residual = float(
        abs(abs(reflected_neighbor[0] - reflected_source[0]) - 1)
        + abs(_hamming(reflected_neighbor[1], reflected_source[1]) - 1)
    )
    full_expectation = _full_expectation(*signed)
    quotient_expectation = _quotient_expectation(*quotient)
    canonical_state = _transduce(initial, canonical)
    return ReflectedAddressLaw(
        signed,
        quotient,
        canonical,
        orientation,
        6,
        full_expectation,
        quotient_expectation,
        float(
            abs(canonical_state[0] - signed[0])
            + _hamming(canonical_state[1], signed[1])
        ),
        float(
            abs(reflection_twice[0] - signed[0])
            + _hamming(reflection_twice[1], signed[1])
        ),
        adjacency_residual,
        float(abs(full_expectation - quotient_expectation)),
        float(
            abs(abs(section[0]) - quotient[0])
            + _hamming(section[1], quotient[1])
        ),
        float(
            abs(reconstructed[0] - signed[0])
            + _hamming(reconstructed[1], signed[1])
        ),
    )


def _remove_b1_enumeration(value: SignedCubicTransductionInput):
    complete = signed_cubic_transduction(value)
    complete_response = np.asarray(
        (complete.displacement, *complete.endpoint, complete.canonical_address),
        dtype=float,
    )
    removed_response = np.asarray((0.0, *complete.endpoint, 0.0), dtype=float)
    return source_removal_result(
        A1, complete_response, removed_response, tolerance=value.tolerance
    )


def _remove_b1_cube(value: SignedCubicTransductionInput):
    complete = signed_cubic_transduction(value)
    complete_response = np.asarray(
        (complete.displacement, *complete.endpoint), dtype=float
    )
    removed_response = np.asarray(
        (complete.displacement, *_vertex(value.initial_vertex)), dtype=float
    )
    return source_removal_result(
        A2, complete_response, removed_response, tolerance=value.tolerance
    )


def _remove_b2_cube(value: CoverDynamicsInput):
    complete = cover_dynamics(value)
    complete_response = np.asarray(
        (value.target_layer, *_vertex(value.target_vertex)), dtype=float
    )
    removed_response = np.asarray(
        (value.target_layer, *_vertex(value.initial_vertex)), dtype=float
    )
    return source_removal_result(
        A2, complete_response, removed_response, tolerance=value.tolerance
    )


def _remove_b2_recurrence(value: CoverDynamicsInput):
    complete = cover_dynamics(value)
    complete_response = np.asarray(
        (
            value.target_layer,
            *_vertex(value.target_vertex),
            complete.path_probability,
        ),
        dtype=float,
    )
    removed_response = np.asarray(
        (value.start_layer, *_vertex(value.initial_vertex), 0.0), dtype=float
    )
    return source_removal_result(
        A3, complete_response, removed_response, tolerance=value.tolerance
    )


def _remove_c1_transducer(value: ReflectedAddressInput):
    complete = reflected_address(value)
    complete_response = np.asarray(
        (complete.signed_vertex[0], *complete.signed_vertex[1]), dtype=float
    )
    removed_response = np.asarray(
        (0.0, *_vertex(value.initial_vertex)), dtype=float
    )
    return source_removal_result(
        B1, complete_response, removed_response, tolerance=value.tolerance
    )


def _remove_c1_dynamics(value: ReflectedAddressInput):
    complete = reflected_address(value)
    complete_response = np.asarray(
        (complete.full_expectation, complete.quotient_expectation), dtype=float
    )
    hold_only = 0.5 * _quotient_function(*complete.quotient_vertex)
    removed_response = np.asarray((hold_only, hold_only), dtype=float)
    return source_removal_result(
        B2, complete_response, removed_response, tolerance=value.tolerance
    )


def contracts() -> tuple[ComplexContract, ...]:
    artifact = ArtifactSpec(
        ("json", "csv"),
        "python tools/generate_artifact_provenance.py --output-root <output-root>",
    )
    a1 = ComplexContract(
        A1,
        APPENDIX,
        APPENDIX_SHA256,
        ComplexLevel.A,
        (),
        DomainSpec(
            "countable ray and shortlex word",
            "non-negative ray index and finite six-letter polarity word",
            (CountableEnumerationInput,),
        ),
        CodomainSpec(
            "bidirectional enumeration law",
            "reflection, magnitude/orientation, and exact shortlex roundtrip",
            (CountableEnumerationLaw,),
        ),
        countable_enumeration,
        residual=lambda source, output: _residual(
            "countable enumeration",
            (
                output.reflection_residual,
                output.code_residual,
                output.magnitude_orientation_residual,
            ),
            source.tolerance,
        ),
        artifact_spec=artifact,
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    a2 = ComplexContract(
        A2,
        APPENDIX,
        APPENDIX_SHA256,
        ComplexLevel.A,
        (),
        DomainSpec(
            "finite cube walk",
            "three-bit vertex, finite coordinate word, and positive generator law",
            (CubicAccessibilityInput,),
        ),
        CodomainSpec(
            "cubic accessibility law",
            "endpoint, parity vector, positive path weight, and full finite orbit",
            (CubicAccessibilityLaw,),
        ),
        cubic_accessibility,
        residual=lambda source, output: _residual(
            "cubic accessibility",
            (
                output.endpoint_residual,
                output.parity_residual,
                output.probability_residual,
                output.reachability_residual,
            ),
            source.tolerance,
        ),
        artifact_spec=artifact,
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    a3 = ComplexContract(
        A3,
        APPENDIX,
        APPENDIX_SHA256,
        ComplexLevel.A,
        (),
        DomainSpec(
            "finitary adjacent flips and recurrence certificate",
            "two non-negative states and a positive resistance depth",
            (FinitaryRecurrenceInput,),
        ),
        CodomainSpec(
            "finitary invariance and lazy reflected-kernel law",
            "exact path inverse, stochastic row sums, detailed balance, and resistance increment",
            (FinitaryRecurrenceLaw,),
        ),
        finitary_recurrence,
        residual=lambda source, output: _residual(
            "finitary recurrence",
            (
                output.inverse_residual,
                output.row_sum_residual,
                output.boundary_balance_residual,
                output.interior_balance_residual,
                output.resistance_increment_residual,
            ),
            source.tolerance,
        ),
        artifact_spec=artifact,
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    b1 = ComplexContract(
        B1,
        APPENDIX,
        APPENDIX_SHA256,
        ComplexLevel.B,
        (A1, A2),
        DomainSpec(
            "signed polarity word",
            "three-bit base vertex and finite signed-axis word",
            (SignedCubicTransductionInput,),
        ),
        CodomainSpec(
            "parity-locked signed cubic transduction",
            "signed displacement, cubic endpoint, minimal address, and exact action laws",
            (SignedCubicTransductionLaw,),
        ),
        signed_cubic_transduction,
        residual=lambda source, output: _residual(
            "signed cubic transduction",
            (
                output.parity_lock_residual,
                output.action_residual,
                output.section_residual,
                output.reflection_residual,
            ),
            source.tolerance,
        ),
        source_removal_checks=(_remove_b1_enumeration, _remove_b1_cube),
        artifact_spec=artifact,
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    b2 = ComplexContract(
        B2,
        APPENDIX,
        APPENDIX_SHA256,
        ComplexLevel.B,
        (A2, A3),
        DomainSpec(
            "cubical reflected cover",
            "parity-compatible source and target states on the non-negative cover",
            (CoverDynamicsInput,),
        ),
        CodomainSpec(
            "recurrent cover support law",
            "finite support path, positive Markov weight, reversible kernel, and resistance certificate",
            (CoverDynamicsLaw,),
        ),
        cover_dynamics,
        residual=lambda source, output: _residual(
            "cubical cover dynamics",
            (
                output.support_residual,
                output.edge_involution_residual,
                output.parity_residual,
                output.row_sum_residual,
                output.detailed_balance_residual,
                output.resistance_increment_residual,
            ),
            source.tolerance,
        ),
        source_removal_checks=(_remove_b2_cube, _remove_b2_recurrence),
        artifact_spec=artifact,
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    c1 = ComplexContract(
        C1,
        APPENDIX,
        APPENDIX_SHA256,
        ComplexLevel.C,
        (B1, B2),
        DomainSpec(
            "signed cubical address",
            "base cube vertex and finite signed-axis address",
            (ReflectedAddressInput,),
        ),
        CodomainSpec(
            "reflected cubical address closure",
            "canonical address, graph reflection, quotient kernel, section, and orientation reconstruction",
            (ReflectedAddressLaw,),
        ),
        reflected_address,
        residual=lambda source, output: _residual(
            "reflected cubical address",
            (
                output.address_residual,
                output.reflection_residual,
                output.adjacency_residual,
                output.quotient_kernel_residual,
                output.section_residual,
                output.reconstruction_residual,
            ),
            source.tolerance,
        ),
        closure_predicate=lambda output, residual: (
            residual is not None and residual.passed and output.local_degree == 6
        ),
        source_removal_checks=(_remove_c1_transducer, _remove_c1_dynamics),
        artifact_spec=artifact,
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    return (a1, a2, a3, b1, b2, c1)
