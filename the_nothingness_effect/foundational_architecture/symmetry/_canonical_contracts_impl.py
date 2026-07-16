"""Canonical executable Symmetry contracts from the Foundational appendix.

This module implements the complete native ``2A -> 2B -> 1C`` Symmetry block:
schedule-controlled parity coding, minimal involutive orbit action, parity-cocycle
transport, involutive generator-word closure, and the schedule-driven word field.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

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
    "the_nothingness_effect/foundational_architecture/symmetry/"
    "canonical_contracts.py"
)

A1 = ComplexId("schedule_controlled_parity_coding_and_uniform_minimal_involution")
A2 = ComplexId(
    "bidirectional_orbit_invariance_and_minimal_involution_generated_c_2_action"
)
B1 = ComplexId("schedule_controlled_orbit_transport")
B2 = ComplexId("involutive_generator_word_closure_and_conjugacy")
C1 = ComplexId("schedule_driven_generator_word_field")
DUALITY = ComplexId("involutive_duality_c_2_action_equivalence_and_free_presentation")


@dataclass(frozen=True)
class ScheduleParityInput:
    tape: tuple[int, ...]
    state: np.ndarray
    tolerance: float = 1e-12


@dataclass(frozen=True)
class OrbitActionInput:
    state: np.ndarray
    tolerance: float = 1e-12


@dataclass(frozen=True)
class ScheduleTransportInput:
    tape: tuple[int, ...]
    state: np.ndarray
    source_index: int
    target_index: int
    tolerance: float = 1e-12


@dataclass(frozen=True)
class GeneratorWordInput:
    state: np.ndarray
    word: tuple[int, ...]
    conjugator: np.ndarray
    tolerance: float = 1e-12


@dataclass(frozen=True)
class ScheduleWordFieldInput:
    tape: tuple[int, ...]
    state: np.ndarray
    conjugator: np.ndarray
    tolerance: float = 1e-12


@dataclass(frozen=True)
class ScheduleParityLaw:
    cumulative_parity: np.ndarray
    encoded_states: np.ndarray
    tape_reconstruction: np.ndarray
    involution_residual: float
    decoder_residual: float


@dataclass(frozen=True)
class OrbitActionLaw:
    orbit: np.ndarray
    group_composition_residual: float
    orbit_invariance_residual: float
    minimality_residual: float


@dataclass(frozen=True)
class ScheduleTransportLaw:
    transported_state: np.ndarray
    transport_exponent: int
    identity_residual: float
    inverse_residual: float
    cocycle_residual: float


@dataclass(frozen=True)
class GeneratorWordLaw:
    word_parity: int
    word_action: np.ndarray
    reduced_action: np.ndarray
    conjugated_action: np.ndarray
    closure_residual: float
    conjugacy_residual: float


@dataclass(frozen=True)
class ScheduleWordFieldLaw:
    cumulative_parity: np.ndarray
    field: np.ndarray
    conjugated_field: np.ndarray
    recurrence_residual: float
    conjugacy_residual: float
    boundary_residual: float


def _tolerance(value: float) -> float:
    if not math.isfinite(value) or value < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    return float(value)


def _state(value: object) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.ndim != 1 or result.size < 1:
        raise DomainViolationError("symmetry state must be a nonempty finite vector")
    if not np.isfinite(result).all():
        raise NonFiniteValueError("symmetry state contains NaN or infinity")
    return result


def _tape(value: tuple[int, ...]) -> np.ndarray:
    result = np.asarray(value, dtype=int)
    if result.ndim != 1 or result.size < 1 or not np.isin(result, (0, 1)).all():
        raise DomainViolationError("schedule tape must be a nonempty binary sequence")
    return result


def _conjugator(value: object, dimension: int) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.shape != (dimension, dimension) or not np.isfinite(result).all():
        raise DomainViolationError("conjugator must be a finite square matrix on the state")
    if np.linalg.matrix_rank(result) != dimension:
        raise DomainViolationError("conjugator must be invertible")
    return result


def _residual(name: str, values: tuple[float, ...], tolerance: float) -> ResidualResult:
    vector = tuple(float(item) for item in values)
    norm = float(np.linalg.norm(vector))
    passed = norm <= tolerance
    return ResidualResult(
        name,
        vector,
        tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
    )


def schedule_parity(value: ScheduleParityInput) -> ScheduleParityLaw:
    tape = _tape(value.tape)
    state = _state(value.state)
    _tolerance(value.tolerance)
    cumulative = np.mod(np.cumsum(tape), 2)
    encoded = np.where(cumulative[:, None] == 0, state, -state)
    decoded = np.empty_like(tape)
    decoded[0] = cumulative[0]
    decoded[1:] = np.mod(cumulative[1:] - cumulative[:-1], 2)
    expected = np.where(cumulative[:, None] == 0, state, -state)
    return ScheduleParityLaw(
        cumulative,
        encoded,
        decoded,
        float(np.linalg.norm(encoded - expected)),
        float(np.linalg.norm(decoded - tape)),
    )


def orbit_action(value: OrbitActionInput) -> OrbitActionLaw:
    state = _state(value.state)
    _tolerance(value.tolerance)
    orbit = np.stack((state, -state))
    minimality = 0.0 if np.linalg.norm(state) > value.tolerance else 1.0
    return OrbitActionLaw(
        orbit,
        float(np.linalg.norm(-(-state) - state)),
        float(abs(np.linalg.norm(orbit[0]) - np.linalg.norm(orbit[1]))),
        minimality,
    )


def schedule_transport(value: ScheduleTransportInput) -> ScheduleTransportLaw:
    tape = _tape(value.tape)
    state = _state(value.state)
    _tolerance(value.tolerance)
    cumulative = np.mod(np.cumsum(tape), 2)
    if not (
        0 <= value.source_index < len(cumulative)
        and 0 <= value.target_index < len(cumulative)
    ):
        raise DomainViolationError("transport indices lie outside the schedule")
    exponent = int(
        (cumulative[value.target_index] - cumulative[value.source_index]) % 2
    )
    transported = state if exponent == 0 else -state
    inverse = transported if exponent == 0 else -transported
    middle = (value.source_index + value.target_index) // 2
    split = int(
        (cumulative[middle] - cumulative[value.source_index]) % 2
    )
    split = (
        split
        + int((cumulative[value.target_index] - cumulative[middle]) % 2)
    ) % 2
    return ScheduleTransportLaw(
        transported,
        exponent,
        0.0,
        float(np.linalg.norm(inverse - state)),
        float(abs(exponent - split)),
    )


def generator_word(value: GeneratorWordInput) -> GeneratorWordLaw:
    state = _state(value.state)
    word = _tape(value.word)
    conjugator = _conjugator(value.conjugator, state.size)
    _tolerance(value.tolerance)
    inverse = np.linalg.inv(conjugator)
    parity = int(np.sum(word) % 2)
    action = state if parity == 0 else -state
    reduced = action.copy()
    conjugated = conjugator @ (inverse @ action)
    return GeneratorWordLaw(
        parity,
        action,
        reduced,
        conjugated,
        float(np.linalg.norm(action - reduced)),
        float(np.linalg.norm(conjugated - action)),
    )


def schedule_word_field(value: ScheduleWordFieldInput) -> ScheduleWordFieldLaw:
    schedule = schedule_parity(
        ScheduleParityInput(value.tape, value.state, value.tolerance)
    )
    conjugator = _conjugator(value.conjugator, schedule.encoded_states.shape[1])
    inverse = np.linalg.inv(conjugator)
    conjugated = np.stack(
        [conjugator @ (inverse @ item) for item in schedule.encoded_states]
    )
    expected = np.stack(
        [
            schedule.encoded_states[0],
            *[
                schedule.encoded_states[index - 1]
                if value.tape[index] == 0
                else -schedule.encoded_states[index - 1]
                for index in range(1, len(value.tape))
            ],
        ]
    )
    state = _state(value.state)
    return ScheduleWordFieldLaw(
        schedule.cumulative_parity,
        schedule.encoded_states,
        conjugated,
        float(np.linalg.norm(schedule.encoded_states - expected)),
        float(np.linalg.norm(conjugated - schedule.encoded_states)),
        float(
            np.linalg.norm(
                schedule.encoded_states[0] - ((-1) ** value.tape[0]) * state
            )
        ),
    )


def _remove_transport_schedule(value: ScheduleTransportInput):
    complete = schedule_transport(value).transported_state
    removed = _state(value.state)
    return source_removal_result(A1, complete, removed, tolerance=value.tolerance)


def _remove_transport_duality(value: ScheduleTransportInput):
    complete = schedule_transport(value).transported_state
    return source_removal_result(
        DUALITY,
        complete,
        np.zeros_like(complete),
        tolerance=value.tolerance,
    )


def _remove_word_orbit(value: GeneratorWordInput):
    complete = generator_word(value).word_action
    removed = _state(value.state)
    return source_removal_result(A2, complete, removed, tolerance=value.tolerance)


def _remove_word_duality(value: GeneratorWordInput):
    complete = generator_word(value).word_action
    return source_removal_result(
        DUALITY,
        complete,
        np.zeros_like(complete),
        tolerance=value.tolerance,
    )


def _remove_field_transport(value: ScheduleWordFieldInput):
    complete = schedule_word_field(value).field
    state = _state(value.state)
    removed = np.repeat(state[None, :], len(value.tape), axis=0)
    return source_removal_result(B1, complete, removed, tolerance=value.tolerance)


def _remove_field_word(value: ScheduleWordFieldInput):
    complete = schedule_word_field(value).field
    return source_removal_result(
        B2,
        complete,
        np.zeros_like(complete),
        tolerance=value.tolerance,
    )


def contracts() -> tuple[ComplexContract, ...]:
    a1 = ComplexContract(
        A1,
        APPENDIX,
        APPENDIX_SHA256,
        ComplexLevel.A,
        (),
        DomainSpec(
            "binary schedule and state",
            "nonempty binary tape and finite state",
            (ScheduleParityInput,),
        ),
        CodomainSpec(
            "schedule parity law",
            "cumulative parity, encoded orbit, decoder, and exact residuals",
            (ScheduleParityLaw,),
        ),
        schedule_parity,
        residual=lambda source, output: _residual(
            "schedule parity",
            (output.involution_residual, output.decoder_residual),
            source.tolerance,
        ),
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
            "minimal involutive orbit",
            "nonzero finite state",
            (OrbitActionInput,),
        ),
        CodomainSpec(
            "C2 orbit action",
            "two-state orbit and exact group-action residuals",
            (OrbitActionLaw,),
        ),
        orbit_action,
        residual=lambda source, output: _residual(
            "orbit action",
            (
                output.group_composition_residual,
                output.orbit_invariance_residual,
                output.minimality_residual,
            ),
            source.tolerance,
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    b1 = ComplexContract(
        B1,
        APPENDIX,
        APPENDIX_SHA256,
        ComplexLevel.B,
        (A1, DUALITY),
        DomainSpec(
            "schedule transport",
            "binary tape, finite state, and two schedule indices",
            (ScheduleTransportInput,),
        ),
        CodomainSpec(
            "parity-cocycle transport",
            "transported state and identity/inverse/cocycle residuals",
            (ScheduleTransportLaw,),
        ),
        schedule_transport,
        residual=lambda source, output: _residual(
            "schedule transport",
            (
                output.identity_residual,
                output.inverse_residual,
                output.cocycle_residual,
            ),
            source.tolerance,
        ),
        source_removal_checks=(
            _remove_transport_schedule,
            _remove_transport_duality,
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    b2 = ComplexContract(
        B2,
        APPENDIX,
        APPENDIX_SHA256,
        ComplexLevel.B,
        (A2, DUALITY),
        DomainSpec(
            "involutive generator word",
            "binary word, finite state, and invertible conjugator",
            (GeneratorWordInput,),
        ),
        CodomainSpec(
            "word closure and conjugacy",
            "reduced word action and exact residuals",
            (GeneratorWordLaw,),
        ),
        generator_word,
        residual=lambda source, output: _residual(
            "generator word",
            (output.closure_residual, output.conjugacy_residual),
            source.tolerance,
        ),
        source_removal_checks=(_remove_word_orbit, _remove_word_duality),
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
            "schedule-driven word field",
            "binary tape, finite state, and invertible conjugator",
            (ScheduleWordFieldInput,),
        ),
        CodomainSpec(
            "symmetry word field",
            "field, conjugated field, recurrence, and boundary residuals",
            (ScheduleWordFieldLaw,),
        ),
        schedule_word_field,
        residual=lambda source, output: _residual(
            "schedule word field",
            (
                output.recurrence_residual,
                output.conjugacy_residual,
                output.boundary_residual,
            ),
            source.tolerance,
        ),
        closure_predicate=lambda _output, residual: residual is not None and residual.passed,
        source_removal_checks=(_remove_field_transport, _remove_field_word),
        artifact_spec=ArtifactSpec(
            ("field_csv", "parity_plot"),
            "python tools/generate_artifact_provenance.py --output-root <output-root>",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    return a1, a2, b1, b2, c1
