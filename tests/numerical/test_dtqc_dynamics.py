from __future__ import annotations

import torch

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.neural_operator import (
    DTQC_COMPLEX_IDS,
    DTQCInflationLayer,
)


def test_dtqc_exposes_stateful_trajectory_and_flowpoint_clock():
    torch.manual_seed(101)
    value = torch.rand(4, 8) + 0.2
    state = DTQCInflationLayer(time_steps=8)(value)

    assert state.trajectory is not None and state.trajectory.shape == (8, 4, 8)
    assert state.flowpoint_sector is not None
    assert torch.equal(
        state.flowpoint_sector,
        torch.tensor([1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0]),
    )
    assert state.drive_phase is not None and state.drive_phase.shape == (8,)
    assert state.temporal_spectrum is not None and state.temporal_spectrum.shape[0] == 5
    assert state.order_parameters is not None
    assert set(state.residuals) == set(DTQC_COMPLEX_IDS)
    assert all(torch.isfinite(value) for value in state.order_parameters.values())


def test_elastic_gain_changes_the_returned_dtqc_reconstruction():
    torch.manual_seed(103)
    value = torch.rand(3, 10) + 0.3
    layer = DTQCInflationLayer(time_steps=6)
    unit = layer(value, elastic_gain=torch.ones(3, 1))
    amplified = layer(value, elastic_gain=torch.full((3, 1), 1.2))

    assert not torch.allclose(unit.reconstruction, amplified.reconstruction)
    assert not torch.allclose(unit.trajectory, amplified.trajectory)


def test_flowpoint_ablation_reduces_period_two_response():
    torch.manual_seed(107)
    value = torch.rand(5, 12) + 0.4
    canonical = DTQCInflationLayer(time_steps=10, flowpoint_alternation=True)(value)
    ablated = DTQCInflationLayer(time_steps=10, flowpoint_alternation=False)(value)

    assert canonical.order_parameters is not None
    assert ablated.order_parameters is not None
    assert canonical.order_parameters["subharmonic_fraction"] > ablated.order_parameters["subharmonic_fraction"]
    assert canonical.order_parameters["flowpoint_one_step_correlation"] < ablated.order_parameters["flowpoint_one_step_correlation"]


def test_strict_leakage_threshold_fails_closed_in_existing_contract_vector():
    torch.manual_seed(109)
    value = torch.rand(4, 14) + 0.2
    state = DTQCInflationLayer(
        support_fraction=0.25,
        max_input_leakage=0.0,
        time_steps=6,
    )(value)

    assert state.input_leakage > 0.0
    assert state.residuals[DTQC_COMPLEX_IDS[1]] > 0.0
    assert state.residuals[DTQC_COMPLEX_IDS[-1]] > 0.0
