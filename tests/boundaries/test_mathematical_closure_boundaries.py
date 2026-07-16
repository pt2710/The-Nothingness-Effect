from __future__ import annotations

import pytest

from the_nothingness_effect.mathematical_architecture.a_level import PiApproximationInput, pi_approximation
from the_nothingness_effect.mathematical_architecture.b_level import ApproximationHarmonicInput, approximation_harmonic_geometry
from the_nothingness_effect.mathematical_architecture.c_level import SignedPolarFieldInput, signed_polar_field
from the_nothingness_effect._runtime.theorem_complex_runtime.types import DomainViolationError


def test_damping_length_is_part_of_approximation_domain():
    with pytest.raises(DomainViolationError):
        pi_approximation(PiApproximationInput(4, (0.0, 0.0)))


def test_harmonic_times_must_stay_inside_declared_horizon():
    with pytest.raises(DomainViolationError):
        approximation_harmonic_geometry(
            ApproximationHarmonicInput(4, (), (0.0, 2.0), (1.0 + 0j,), 1.0)
        )


def test_signed_polar_phase_must_be_unit_norm():
    with pytest.raises(DomainViolationError):
        signed_polar_field(SignedPolarFieldInput(1.0, 2.0 + 0j, 4, (), (0.0,), 1.0))


def test_negative_radius_uses_quotient_equivalent_phase():
    positive = signed_polar_field(
        SignedPolarFieldInput(2.0, 1.0 + 0j, 4, (), (0.0, 0.5), 1.0)
    )
    negative = signed_polar_field(
        SignedPolarFieldInput(-2.0, -1.0 + 0j, 4, (), (0.0, 0.5), 1.0)
    )
    assert positive.field == negative.field
