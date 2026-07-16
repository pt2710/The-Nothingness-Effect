from __future__ import annotations

import torch

from the_nothingness_effect.artificial_intelligence.qenn.model import QENNModel
from the_nothingness_effect.artificial_intelligence.qenn.training import training_step
from the_nothingness_effect.artificial_intelligence.shared.types import AIClosureStatus
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.neural_operator import DTQC_COMPLEX_IDS


def test_qenn_is_differentiable_and_uses_tne_gates():
    torch.manual_seed(0)
    model = QENNModel(4, 6, 3, K_D=2.0, soi_scale=5.0)
    features = (torch.rand(8, 4) + 0.5).requires_grad_()
    targets = torch.arange(8) % 3

    output = model(features)
    loss = training_step(model, features, targets)
    loss.backward()

    assert output.hidden.shape == (8, 6)
    assert output.dtqc_state is not None
    assert output.dtqc_state.complex_ids == DTQC_COMPLEX_IDS
    assert output.metadata["dtqc_integration"] == "canonical_runtime"
    assert set(output.dtqc_state.residuals) == set(DTQC_COMPLEX_IDS)
    assert output.dfi.shape == features.shape
    assert output.pdfi is not None and output.pdfi.shape == (8, 1)
    assert torch.all(output.elastic_gain > 0)
    assert torch.allclose(output.observation.sum(dim=-1), torch.ones(8))
    assert output.observation_collapse_state is not None
    assert output.elastic_dubler_state is not None
    assert output.elastic_pi_norm_state is not None
    assert output.metadata["observation_collapse_integration"] == "canonical_runtime"
    assert float(output.residuals["collapse_idempotence"]) == 0.0
    assert float(output.residuals["elastic_dubler_cocycle"].detach()) <= 1e-5
    assert float(output.residuals["completeness"].detach()) <= 1e-5
    assert output.closure_status is AIClosureStatus.NUMERICAL_CANDIDATE
    assert features.grad is not None and torch.isfinite(features.grad).all()
    assert all(parameter.grad is not None for parameter in model.parameters())


def test_qenn_flowpoint_and_projectors_are_exact():
    model = QENNModel(3, 3, 2)
    features = torch.rand(5, 3) + 1.0
    output = model(features)

    assert torch.allclose(output.invariant_state, torch.zeros_like(features))
    assert torch.allclose(output.anti_invariant_state, features)
    assert float(output.residuals["flowpoint_involution"]) == 0.0
    assert float(output.residuals["c2_equivariance"].detach()) == 0.0
