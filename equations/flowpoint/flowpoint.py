"""Canonical Flowpoint primitives and compatibility generator.

The canonical implementation is the self-negating linear involution and its
anti-invariant orbit. The historical XOR expression is no longer used as a
computational mechanism. ``fp`` remains as a compatibility generator.
"""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Number
from typing import Any, Iterator, Sequence

import numpy as np

from equations.theorem_complex_runtime.types import DomainViolationError
from equations.theorem_complex_runtime.validation import ensure_finite


Numeric = int | float | complex | np.ndarray


def _is_zero(value: Any) -> bool:
    return bool(np.all(np.asarray(value) == 0))


def _same_shape(left: Any, right: Any) -> bool:
    return np.asarray(left).shape == np.asarray(right).shape


def canonical_involution(value: Numeric) -> Numeric:
    """The canonical self-negating involution ``F(x) = -x``."""

    if isinstance(value, bool) or not isinstance(value, (Number, np.ndarray)):
        raise DomainViolationError("canonical Flowpoint states must be numeric, not Boolean")
    ensure_finite(value, name="Flowpoint state")
    result = -value
    ensure_finite(result, name="involuted Flowpoint state")
    return result


def invariant_projector(value: Numeric) -> Numeric:
    return 0.5 * (value + canonical_involution(value))


def anti_invariant_projector(value: Numeric) -> Numeric:
    return 0.5 * (value - canonical_involution(value))


@dataclass(frozen=True)
class FlowpointOrbit:
    initial: Numeric
    states: tuple[Numeric, ...]
    period: int
    involution_residual: float


def flowpoint_orbit(initial: Numeric, *, steps: int) -> FlowpointOrbit:
    if steps <= 0:
        raise DomainViolationError("steps must be positive")
    canonical_involution(initial)
    if _is_zero(initial):
        raise DomainViolationError("the exact two-state Flowpoint orbit requires a nonzero state")
    states = tuple(initial if index % 2 == 0 else canonical_involution(initial) for index in range(steps))
    twice = canonical_involution(canonical_involution(initial))
    residual = float(np.linalg.norm(np.asarray(twice) - np.asarray(initial)))
    return FlowpointOrbit(initial=initial, states=states, period=2, involution_residual=residual)


def harmonic_interpolation(initial: Numeric, time: float, *, delta_t: float) -> Numeric:
    if not np.isfinite(delta_t) or delta_t <= 0:
        raise DomainViolationError("delta_t must be finite and positive")
    if not np.isfinite(time):
        raise DomainViolationError("time must be finite")
    canonical_involution(initial)
    return np.cos(np.pi * time / delta_t) * initial


def _validate_bits(bits: Sequence[int]) -> tuple[int, ...]:
    result = tuple(int(bit) for bit in bits)
    if not result:
        raise DomainViolationError("a finite binary history must contain at least one bit")
    if any(bit not in (0, 1) for bit in result):
        raise DomainViolationError("binary history entries must be exactly 0 or 1")
    return result


@dataclass(frozen=True)
class FlowpointSchedule:
    bits: tuple[int, ...]
    increments: tuple[int, ...]
    times: tuple[int, ...]
    two_adic_prefix: int
    exact_prefix_digits: int

    @classmethod
    def from_bits(cls, bits: Sequence[int]) -> "FlowpointSchedule":
        source = _validate_bits(bits)
        increments = [2 - source[0]]
        increments.extend(2 - (source[index] ^ source[index - 1]) for index in range(1, len(source)))
        times: list[int] = []
        total = 0
        for increment in increments:
            total += increment
            times.append(total)
        if any(time % 2 != bit for time, bit in zip(times, source, strict=True)):
            raise AssertionError("schedule parity construction failed")
        code = sum(bit << index for index, bit in enumerate(source))
        return cls(source, tuple(increments), tuple(times), code, len(source))


@dataclass(frozen=True)
class ScheduledSpectralHistory:
    bits: tuple[int, ...]
    schedule: FlowpointSchedule
    samples: tuple[Numeric, ...]
    decoded_bits: tuple[int, ...]
    two_adic_prefix: int
    reconstruction_residual: float


def scheduled_spectral_history(bits: Sequence[int], *, anti_invariant_state: Numeric) -> ScheduledSpectralHistory:
    """Combine the anti-invariant orbit and parity schedule into a new encoder."""

    if _is_zero(anti_invariant_state):
        raise DomainViolationError("the history encoder requires a nonzero anti-invariant state")
    schedule = FlowpointSchedule.from_bits(bits)
    canonical_involution(anti_invariant_state)
    samples = tuple(
        anti_invariant_state if time % 2 == 0 else canonical_involution(anti_invariant_state)
        for time in schedule.times
    )
    decoded = tuple(
        0 if np.array_equal(sample, anti_invariant_state) else 1
        if np.array_equal(sample, canonical_involution(anti_invariant_state))
        else -1
        for sample in samples
    )
    residual = float(sum(abs(a - b) for a, b in zip(schedule.bits, decoded, strict=True)))
    return ScheduledSpectralHistory(
        bits=schedule.bits,
        schedule=schedule,
        samples=samples,
        decoded_bits=decoded,
        two_adic_prefix=schedule.two_adic_prefix,
        reconstruction_residual=residual,
    )


@dataclass(frozen=True)
class BalanceFiber:
    first: Numeric
    second: Numeric

    def __post_init__(self) -> None:
        ensure_finite(self.first, name="balance-fiber first component")
        ensure_finite(self.second, name="balance-fiber second component")
        if not _same_shape(self.first, self.second):
            raise DomainViolationError("balance-fiber components must share a shape")

    @property
    def balance(self) -> Numeric:
        return self.first + self.second

    @property
    def internal(self) -> Numeric:
        return 0.5 * (self.first - self.second)

    def swap(self) -> "BalanceFiber":
        return BalanceFiber(self.second, self.first)

    def kernel_projector(self) -> "BalanceFiber":
        half_difference = 0.5 * (self.first - self.second)
        return BalanceFiber(half_difference, -half_difference)

    def diagonal_projector(self) -> "BalanceFiber":
        half_sum = 0.5 * (self.first + self.second)
        return BalanceFiber(half_sum, half_sum)

    def update(self, increment: Numeric) -> "BalanceFiber":
        ensure_finite(increment, name="balance-fiber increment")
        return BalanceFiber(self.first + increment, self.second - increment)

    @classmethod
    def from_balance_internal(cls, balance: Numeric, internal: Numeric) -> "BalanceFiber":
        ensure_finite(balance, name="balance")
        ensure_finite(internal, name="internal coordinate")
        return cls(0.5 * balance + internal, 0.5 * balance - internal)


@dataclass(frozen=True)
class PhaseClock:
    phase: int

    def __post_init__(self) -> None:
        if self.phase not in (0, 1):
            raise DomainViolationError("the intrinsic C2 phase is 0 or 1")

    def shift(self) -> "PhaseClock":
        return PhaseClock(1 - self.phase)

    def act(self, value: Numeric) -> Numeric:
        return value if self.phase == 0 else canonical_involution(value)


@dataclass(frozen=True)
class PhaseTransportResult:
    source: BalanceFiber
    transported: BalanceFiber
    source_phase: PhaseClock
    target_phase: PhaseClock
    amplitude: Numeric
    connection_increment: Numeric
    balance_residual: float


def phase_potential(phase: PhaseClock, amplitude: Numeric) -> Numeric:
    ensure_finite(amplitude, name="phase amplitude")
    return amplitude if phase.phase == 0 else canonical_involution(amplitude)


def phase_indexed_kernel_transport(
    fiber: BalanceFiber,
    source_phase: PhaseClock,
    target_phase: PhaseClock,
    *,
    amplitude: Numeric,
) -> PhaseTransportResult:
    increment = phase_potential(target_phase, amplitude) - phase_potential(source_phase, amplitude)
    transported = fiber.update(increment)
    residual = float(np.linalg.norm(np.asarray(transported.balance) - np.asarray(fiber.balance)))
    return PhaseTransportResult(
        source=fiber,
        transported=transported,
        source_phase=source_phase,
        target_phase=target_phase,
        amplitude=amplitude,
        connection_increment=increment,
        balance_residual=residual,
    )


def compose_phase_transports(
    fiber: BalanceFiber,
    first: PhaseClock,
    second: PhaseClock,
    third: PhaseClock,
    *,
    amplitude: Numeric,
) -> tuple[BalanceFiber, BalanceFiber]:
    first_leg = phase_indexed_kernel_transport(fiber, first, second, amplitude=amplitude)
    second_leg = phase_indexed_kernel_transport(first_leg.transported, second, third, amplitude=amplitude)
    direct = phase_indexed_kernel_transport(fiber, first, third, amplitude=amplitude)
    return second_leg.transported, direct.transported


@dataclass(frozen=True)
class AffineHistoryField:
    bits: tuple[int, ...]
    spatial_points: tuple[int, ...]
    states: tuple[BalanceFiber, ...]
    balance: Numeric
    kernel_offset: Numeric
    history_amplitude: Numeric
    local_internal_gradient: tuple[Numeric, ...]
    balance_residual: float
    boundary_trace_residual: float
    reconstruction_residual: float
    closure_status: str


def affine_reflection(fiber: BalanceFiber, *, kernel_offset: Numeric) -> BalanceFiber:
    reflected_internal = -2 * kernel_offset - fiber.internal
    return BalanceFiber.from_balance_internal(fiber.balance, reflected_internal)


def affine_history_field(
    bits: Sequence[int],
    *,
    balance: Numeric,
    kernel_offset: Numeric,
    history_amplitude: Numeric,
    tolerance: float = 1e-10,
) -> AffineHistoryField:
    """Exact finite spatial realization of the two complete B sources."""

    history = scheduled_spectral_history(bits, anti_invariant_state=history_amplitude)
    ensure_finite(balance, name="field balance")
    ensure_finite(kernel_offset, name="kernel offset")
    anchor_internal = history_amplitude
    states = tuple(
        BalanceFiber.from_balance_internal(
            balance,
            -kernel_offset + ((-1) ** bit) * (history_amplitude + kernel_offset),
        )
        for bit in history.bits
    )
    internals = tuple(state.internal for state in states)
    gradients = tuple(internals[index + 1] - internals[index] for index in range(len(states) - 1))
    balance_residual = max(
        float(np.linalg.norm(np.asarray(state.balance) - np.asarray(balance))) for state in states
    )
    expected_first = BalanceFiber.from_balance_internal(
        balance,
        -kernel_offset + ((-1) ** history.bits[0]) * (history_amplitude + kernel_offset),
    )
    expected_last = BalanceFiber.from_balance_internal(
        balance,
        -kernel_offset + ((-1) ** history.bits[-1]) * (history_amplitude + kernel_offset),
    )
    boundary_residual = float(
        np.linalg.norm(np.asarray(states[0].internal) - np.asarray(expected_first.internal))
        + np.linalg.norm(np.asarray(states[-1].internal) - np.asarray(expected_last.internal))
    )
    decoded = tuple(
        0 if np.array_equal(state.internal, anchor_internal) else 1
        if np.array_equal(
            state.internal, -2 * kernel_offset - history_amplitude
        )
        else -1
        for state in states
    )
    reconstruction = float(sum(abs(a - b) for a, b in zip(history.bits, decoded, strict=True)))
    closed = balance_residual <= tolerance and boundary_residual <= tolerance and reconstruction <= tolerance
    return AffineHistoryField(
        bits=history.bits,
        spatial_points=tuple(range(len(states))),
        states=states,
        balance=balance,
        kernel_offset=kernel_offset,
        history_amplitude=history_amplitude,
        local_internal_gradient=gradients,
        balance_residual=balance_residual,
        boundary_trace_residual=boundary_residual,
        reconstruction_residual=reconstruction,
        closure_status="closed" if closed else "open",
    )


def _legacy_neg(value: bool | int | float | complex) -> bool | int | float | complex:
    return not value if isinstance(value, bool) else -value


def fp(value: bool | int | float | complex) -> Iterator[bool | int | float | complex]:
    """Compatibility generator alternating between a value and its negation."""

    if not isinstance(value, (bool, int, float, complex)):
        raise TypeError(f"Unsupported type for flowpoint: {type(value)}")
    state = value
    while True:
        yield state
        state = _legacy_neg(state)
