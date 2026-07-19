from __future__ import annotations

import math

import numpy as np

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.legacy_faithful_runtime import (
    LegacyFaithfulConfig,
    generate_legacy_faithful_state,
)


def test_legacy_faithful_state_is_finite_non_degenerate_and_typed() -> None:
    state = generate_legacy_faithful_state(LegacyFaithfulConfig(grid_size=48, point_count=500, seed=7))

    assert state.carrier.shape == (48, 48)
    assert state.diffraction.shape == (48, 48)
    assert state.dfi_channels.shape == (5, 48, 48)
    assert state.flowpoint_frames.shape == (10, 48, 48)
    assert state.projection_5d.shape == (500, 5)
    assert state.projection_3d.shape == (500, 3)
    assert state.wavelet_ridges.shape == (2, 48, 48)
    assert np.isfinite(state.elastic_pi).all()
    assert float(np.std(state.carrier)) > 1e-3
    assert float(np.std(state.diffraction)) > 1e-3
    assert np.all(state.elastic_pi > 0.0)


def test_flowpoint_recurrence_and_canonical_elastic_pi_are_exact() -> None:
    config = LegacyFaithfulConfig(grid_size=48, point_count=400, seed=11, entropy_scale=2.25)
    state = generate_legacy_faithful_state(config)

    np.testing.assert_allclose(state.flowpoint_frames[1:], -state.flowpoint_frames[:-1], atol=0.0, rtol=0.0)
    np.testing.assert_allclose(state.flowpoint_frames[2:], state.flowpoint_frames[:-2], atol=0.0, rtol=0.0)
    np.testing.assert_allclose(
        state.elastic_pi,
        math.pi * np.exp(-state.entropy / config.entropy_scale),
        rtol=1e-14,
        atol=1e-14,
    )
    assert state.flowpoint_sector.tolist() == [1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0]


def test_projection_sphere_and_source_removal_are_deterministic_and_non_degenerate() -> None:
    config = LegacyFaithfulConfig(grid_size=48, point_count=450, seed=13)
    first = generate_legacy_faithful_state(config)
    second = generate_legacy_faithful_state(config)

    np.testing.assert_array_equal(first.projection_5d, second.projection_5d)
    np.testing.assert_array_equal(first.projection_3d, second.projection_3d)
    assert np.linalg.matrix_rank(first.projection_5d) == 5
    assert first.sphere_points.shape[1] == 3
    assert first.half_sphere_points.shape[1] == 3
    assert 0 < len(first.half_sphere_points) < len(first.sphere_points)
    assert all(residual > 0.0 for residual in first.source_removal.values())
