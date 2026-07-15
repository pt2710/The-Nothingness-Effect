from __future__ import annotations

from dataclasses import replace

import numpy as np

from equations.flowpoint.c_level import (
    AffineHistoryInput,
    affine_history_operator,
    affine_history_residual,
)
from equations.flowpoint.flowpoint import (
    BalanceFiber,
    FlowpointSchedule,
    PhaseClock,
    affine_history_field,
    affine_reflection,
    anti_invariant_projector,
    canonical_involution,
    compose_phase_transports,
    flowpoint_orbit,
    invariant_projector,
    scheduled_spectral_history,
)


def test_self_negating_orbit_projectors_and_periodicity():
    source = np.array([1.0, -2.0])
    orbit = flowpoint_orbit(source, steps=6)
    assert orbit.period == 2
    assert orbit.involution_residual == 0.0
    assert np.array_equal(orbit.states[0], orbit.states[2])
    assert np.allclose(invariant_projector(source), 0.0)
    assert np.allclose(anti_invariant_projector(source), source)
    assert np.array_equal(canonical_involution(canonical_involution(source)), source)


def test_parity_schedule_and_finite_two_adic_prefix_are_exact():
    schedule = FlowpointSchedule.from_bits((1, 0, 1, 1))
    assert tuple(time % 2 for time in schedule.times) == schedule.bits
    assert schedule.two_adic_prefix == 13
    assert schedule.exact_prefix_digits == 4


def test_scheduled_encoder_decoder_is_an_inverse_on_finite_histories():
    history = scheduled_spectral_history((0, 1, 1, 0), anti_invariant_state=3.0)
    assert history.decoded_bits == history.bits
    assert history.reconstruction_residual == 0.0
    assert history.two_adic_prefix == 6


def test_balance_fiber_projectors_and_phase_transport_composition():
    fiber = BalanceFiber(4.0, 2.0)
    kernel = fiber.kernel_projector()
    diagonal = fiber.diagonal_projector()
    assert np.isclose(kernel.first + diagonal.first, fiber.first)
    assert np.isclose(kernel.second + diagonal.second, fiber.second)
    composed, direct = compose_phase_transports(
        fiber, PhaseClock(0), PhaseClock(1), PhaseClock(0), amplitude=0.75
    )
    assert np.isclose(composed.first, direct.first)
    assert np.isclose(composed.second, direct.second)


def test_affine_field_complement_is_pointwise_reflection():
    field = affine_history_field(
        (0, 1, 0), balance=2.0, kernel_offset=0.25, history_amplitude=1.0
    )
    complement = affine_history_field(
        (1, 0, 1), balance=2.0, kernel_offset=0.25, history_amplitude=1.0
    )
    reflected = tuple(affine_reflection(state, kernel_offset=0.25) for state in field.states)
    assert all(
        np.isclose(left.first, right.first) and np.isclose(left.second, right.second)
        for left, right in zip(reflected, complement.states, strict=True)
    )


def test_boundary_or_reconstruction_defect_opens_closure():
    value = AffineHistoryInput((0, 1), 2.0, 0.25, 1.0)
    field = affine_history_operator(value)
    tampered = replace(field, boundary_trace_residual=1.0, closure_status="open")
    assert affine_history_residual(value, tampered).passed is False
