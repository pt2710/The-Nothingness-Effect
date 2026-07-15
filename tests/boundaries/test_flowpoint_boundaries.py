from __future__ import annotations

import math

import pytest

from equations.flowpoint.flowpoint import (
    BalanceFiber,
    FlowpointSchedule,
    affine_history_field,
    flowpoint_orbit,
    harmonic_interpolation,
    scheduled_spectral_history,
)
from tne_runtime.theorem_complex_runtime.types import DomainViolationError, NonFiniteValueError


def test_zero_state_is_not_promoted_to_two_state_orbit():
    with pytest.raises(DomainViolationError, match="nonzero"):
        flowpoint_orbit(0.0, steps=4)


def test_invalid_binary_schedule_fails():
    with pytest.raises(DomainViolationError):
        FlowpointSchedule.from_bits((0, -1, 1))


def test_harmonic_sampling_requires_positive_scale():
    with pytest.raises(DomainViolationError):
        harmonic_interpolation(1.0, 1.0, delta_t=0.0)


def test_nonfinite_balance_fiber_and_history_fail_closed():
    with pytest.raises(NonFiniteValueError):
        BalanceFiber(math.inf, 0.0)
    with pytest.raises(NonFiniteValueError):
        scheduled_spectral_history((0, 1), anti_invariant_state=math.nan)


def test_affine_field_rejects_nonbinary_spatial_history():
    with pytest.raises(DomainViolationError):
        affine_history_field((0, 2), balance=0.0, kernel_offset=0.0, history_amplitude=1.0)
