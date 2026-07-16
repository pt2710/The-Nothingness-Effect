from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
)
from the_nothingness_effect.the_completeness_theorem.authoritative_obligations import (
    APPENDIX_SHA256,
    certify_sheaf_descent,
    certify_splitting_attainment,
    decode_typed_admissibility,
    factor_terminal_observable,
    noether_transgression_common_codomain,
    separate_noether_operator_and_residual,
)


def test_authority_binding_matches_latest_completeness_source():
    assert APPENDIX_SHA256 == "1a186b3350f16c284b3cb54f7dfb63d6729d98142e9fb8b53c6de4d9ce3d84f3"


def test_noether_operator_and_residual_are_distinct_typed_outputs():
    result = separate_noether_operator_and_residual(
        np.eye(3),
        np.array([0.0, 0.0, 0.0]),
    )
    assert result.types_separated
    assert result.operator_value.shape == (3, 3)
    assert result.residual_value.shape == (3,)


def test_complex_07_decodes_only_on_open_free_orbit_and_detects_null_gate():
    state = np.array([1.0, -1.0])
    involution = lambda value: -value
    open_result = decode_typed_admissibility(
        gate=2.0,
        orientation_bit=1,
        observed_phase_bit=0,
        infinity_state=state,
        involution=involution,
        free_orbit=True,
    )
    assert open_result.reconstructive_domain
    assert open_result.decoded_orientation == 1
    assert not open_result.null_gate_detected

    null_result = decode_typed_admissibility(
        gate=0.0,
        orientation_bit=1,
        observed_phase_bit=0,
        infinity_state=state,
        involution=involution,
        free_orbit=True,
    )
    assert null_result.null_gate_detected
    assert not null_result.reconstructive_domain
    assert null_result.decoded_orientation is None
    assert np.allclose(null_result.output, 0.0)

    fixed_orbit = decode_typed_admissibility(
        gate=1.0,
        orientation_bit=1,
        observed_phase_bit=0,
        infinity_state=np.zeros(2),
        involution=involution,
        free_orbit=False,
    )
    assert not fixed_orbit.reconstructive_domain
    assert fixed_orbit.decoded_orientation is None


def test_complex_08_zero_residual_needs_attainment_witness():
    unattained = certify_splitting_attainment(0.0, infimum_attained=False)
    attained = certify_splitting_attainment(0.0, infimum_attained=True)
    positive = certify_splitting_attainment(1e-3, infimum_attained=True)
    assert not unattained.exact_splitting
    assert attained.exact_splitting
    assert not positive.exact_splitting
    with pytest.raises(DomainViolationError):
        certify_splitting_attainment(-1.0, infimum_attained=True)


def test_noether_transgression_requires_common_codomain_and_zero_flux_domain():
    closed = noether_transgression_common_codomain(
        np.array([1.0, 2.0]),
        np.array([1.0, 2.0]),
        boundary_flux=0.0,
    )
    assert closed.commutation_domain_satisfied
    assert np.allclose(closed.intertwining_residual, 0.0)

    open_flux = noether_transgression_common_codomain(
        np.array([1.0, 2.0]),
        np.array([1.0, 2.0]),
        boundary_flux=0.5,
    )
    assert not open_flux.commutation_domain_satisfied

    with pytest.raises(DomainViolationError):
        noether_transgression_common_codomain(
            np.ones(2),
            np.ones(3),
            boundary_flux=0.0,
        )


def test_complex_10_requires_fixed_isomorphic_descent_and_cocycle():
    closed = certify_sheaf_descent(
        (0.0, 0.0, 0.0),
        0.0,
        fixed_descent_data=True,
        overlap_isomorphisms=True,
    )
    assert closed.gluable

    assert not certify_sheaf_descent(
        (0.0, 0.0, 0.0),
        0.0,
        fixed_descent_data=False,
        overlap_isomorphisms=True,
    ).gluable
    assert not certify_sheaf_descent(
        (0.0, 0.0, 0.0),
        0.0,
        fixed_descent_data=True,
        overlap_isomorphisms=False,
    ).gluable
    assert not certify_sheaf_descent(
        (0.0, 1e-3, 0.0),
        0.0,
        fixed_descent_data=True,
        overlap_isomorphisms=True,
    ).gluable
    assert not certify_sheaf_descent(
        (0.0, 0.0, 0.0),
        1e-3,
        fixed_descent_data=True,
        overlap_isomorphisms=True,
    ).gluable


def test_terminal_observable_factors_through_unique_terminal_map():
    constant = factor_terminal_observable(
        np.array([3.0, 3.0, 3.0]),
        terminal_value=3.0,
    )
    assert constant.factors_through_unique_terminal_map
    assert constant.factorization_residual == 0.0

    nonconstant = factor_terminal_observable(
        np.array([3.0, 4.0, 3.0]),
        terminal_value=3.0,
    )
    assert not nonconstant.factors_through_unique_terminal_map
    assert nonconstant.factorization_residual > 0.0
