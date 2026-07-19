from __future__ import annotations

import numpy as np

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.canonical_artifact_suite import (
    _bundle,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.quantum_wave_bridge import (
    QUARKS,
    normalized_quark_frequencies,
    simulate_quantum_bridge,
    source_removal_metrics,
)


def test_fp_quantum_bridge_is_normalized_entangled_and_source_bound() -> None:
    state = simulate_quantum_bridge(
        lambda phase: _bundle(32, phase),
        frame_count=8,
    )

    assert state["wavefunctions"].shape == (8, 32, 32)
    assert state["quark_modes"].shape == (8, len(QUARKS), 32, 32)
    assert np.max(np.abs(state["norms"] - 1.0)) < 1e-12
    assert np.allclose(
        np.trace(state["rho_a"], axis1=1, axis2=2),
        1.0,
        atol=1e-12,
    )
    assert np.all(state["entanglement_entropy"] > 0.0)
    assert np.all(state["entanglement_entropy"] <= 1.0 + 1e-12)
    assert np.all(state["concurrence"] > 0.0)
    assert np.all(state["concurrence"] <= 1.0 + 1e-12)
    assert float(np.ptp(state["probabilities"], axis=0).max()) > 1e-7

    frequencies = normalized_quark_frequencies()
    assert frequencies.shape == (6,)
    assert np.all(np.diff(np.sort(frequencies)) >= 0.0)
    assert float(np.ptp(frequencies)) > 1.0

    removals = source_removal_metrics(
        lambda phase: _bundle(28, phase),
        frame_count=6,
    )
    assert {row["source"] for row in removals} == {
        "fp_wave_functionality",
        "fp_particle_and_quark_modes",
        "fp_density_matrix_entanglement",
    }
    assert all(row["necessary"] is True for row in removals)
    assert all(float(row["removal_residual"]) > 1e-4 for row in removals)
