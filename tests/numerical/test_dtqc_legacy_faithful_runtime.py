from __future__ import annotations

import math

import numpy as np

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.legacy_faithful_runtime import (
    LegacyFaithfulConfig,
    generate_legacy_faithful_state,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.spatial_elastic_pi import (
    backproject_directional_profiles,
    spatial_2d_diagnostics,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.visualization import (
    _elastic_pi_surface,
    _quasicrystal_field,
)


def _config(**overrides: object) -> LegacyFaithfulConfig:
    values: dict[str, object] = {
        "grid_size": 64,
        "point_count": 600,
        "seed": 7,
        "time_steps": 12,
        "sphere_resolution": 48,
    }
    values.update(overrides)
    return LegacyFaithfulConfig(**values)


def test_source_faithful_state_is_finite_non_degenerate_and_typed() -> None:
    state = generate_legacy_faithful_state(_config())

    assert state.carrier.shape == (64, 64)
    assert state.radial_profiles.shape == (60, 64)
    assert state.dfi_volume_profiles.shape == (60, 64)
    assert state.flowpoint_frames.shape == (12, 64, 64)
    assert state.scatter_reference_4d.shape == (600, 4)
    assert state.scatter_trajectory_4d.shape == (12, 600, 4)
    assert state.projection_3d.shape == (12, 600, 3)
    assert np.isfinite(state.elastic_pi).all()
    assert np.isfinite(state.canonical_elastic_pi).all()
    assert float(np.std(state.carrier)) > 1e-3
    assert float(np.std(state.diffraction)) > 1e-3
    assert np.all(state.elastic_pi > 0.0)
    assert np.all(state.canonical_elastic_pi > 0.0)


def test_legacy_visual_and_canonical_dubler_sign_conventions_are_separate() -> None:
    state = generate_legacy_faithful_state(_config(entropy_scale=2.25))

    entropy = backproject_directional_profiles(state.entropy_profiles, grid_size=64)
    legacy = math.pi * np.exp(np.clip(entropy / 2.25, -100.0, math.log(100.0)))
    canonical = math.pi * np.exp(np.clip(-entropy / 2.25, -100.0, math.log(100.0)))
    np.testing.assert_allclose(state.entropy, entropy, rtol=1e-14, atol=1e-14)
    np.testing.assert_allclose(state.elastic_pi, legacy, rtol=1e-14, atol=1e-14)
    np.testing.assert_allclose(state.canonical_elastic_pi, canonical, rtol=1e-14, atol=1e-14)
    assert not np.allclose(state.elastic_pi, state.canonical_elastic_pi)


def test_elastic_pi_fields_are_genuinely_two_dimensional() -> None:
    state = generate_legacy_faithful_state(_config())
    for surface in (state.entropy, state.elastic_pi, state.canonical_elastic_pi):
        diagnostics = spatial_2d_diagnostics(surface)
        assert diagnostics["row_broadcast_residual"] > 0.1
        assert diagnostics["column_broadcast_residual"] > 0.1
        assert diagnostics["axis_gradient_balance"] > 0.1
        assert diagnostics["effective_rank"] > 1.5


def test_canonical_dtqc_elastic_pi_surface_is_genuinely_two_dimensional() -> None:
    _, _, field = _quasicrystal_field(64)
    _, elastic_surface, diagnostics = _elastic_pi_surface(field)
    assert elastic_surface.shape == (64, 64)
    assert diagnostics["row_broadcast_residual"] > 0.1
    assert diagnostics["column_broadcast_residual"] > 0.1
    assert diagnostics["axis_gradient_balance"] > 0.1
    assert diagnostics["effective_rank"] > 1.5


def test_flicker_alternates_and_evolves_intrinsically() -> None:
    state = generate_legacy_faithful_state(_config())

    assert state.flowpoint_sector.tolist() == [1.0, -1.0] * 6
    assert state.legacy_frame_index.tolist() == list(range(0, 48, 4))
    # Regression: the previous implementation only negated one frozen frame.
    assert float(np.linalg.norm(state.flowpoint_frames[1] + state.flowpoint_frames[0])) > 1.0
    assert float(
        np.linalg.norm(np.abs(state.flowpoint_frames[1]) - np.abs(state.flowpoint_frames[0]))
    ) > 1.0
    assert state.source_removal["temporal_evolution"] > 0.0


def test_scatter_cloud_deforms_intrinsically_and_is_deterministic() -> None:
    first = generate_legacy_faithful_state(_config(seed=13))
    second = generate_legacy_faithful_state(_config(seed=13))

    np.testing.assert_array_equal(first.scatter_reference_4d, second.scatter_reference_4d)
    np.testing.assert_array_equal(first.scatter_trajectory_4d, second.scatter_trajectory_4d)
    np.testing.assert_array_equal(first.projection_3d, second.projection_3d)
    assert np.linalg.matrix_rank(first.scatter_reference_4d) == 4
    assert float(
        np.linalg.norm(first.scatter_trajectory_4d[1] - first.scatter_trajectory_4d[0])
    ) > 1.0
    coordinate_spread = np.std(first.scatter_trajectory_4d, axis=1)
    assert float(np.max(np.ptp(coordinate_spread, axis=0))) > 0.1
    assert all(residual > 0.0 for residual in first.source_removal.values())
