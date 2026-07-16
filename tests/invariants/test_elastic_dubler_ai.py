from __future__ import annotations

import pytest
import torch

from the_nothingness_effect.artificial_intelligence.shared.elastic_dubler import (
    ElasticDublerLayer,
)
from the_nothingness_effect.artificial_intelligence.shared.elastic_pi_norm import (
    elastic_pi_transition_norm,
)
from the_nothingness_effect.artificial_intelligence.shared.types import AIObstructionError


def test_elastic_dubler_ratio_exchange_and_cocycle_are_exact_numerical_laws():
    entropy = torch.tensor([[0.2, 0.7, 1.3], [1.1, 0.4, 0.9]])
    state = ElasticDublerLayer(K_D=2.0)(entropy)

    expected = torch.exp(
        -(entropy.unsqueeze(-1) - entropy.unsqueeze(-2)) / 2.0
    )
    assert torch.allclose(state.ratio, expected, atol=1e-6)
    assert torch.allclose(
        state.log_shift + state.log_shift.transpose(-1, -2),
        torch.zeros_like(state.log_shift),
        atol=1e-6,
    )
    assert all(float(value) <= 1e-5 for value in state.residuals.values())


def test_elastic_pi_transition_norm_uses_successive_field_ratios():
    trajectory = torch.tensor([[1.0, 2.0, 4.0]])
    elastic = torch.tensor([[3.0, 1.5, 0.75]])
    state = elastic_pi_transition_norm(trajectory, elastic, order=2.0)

    assert torch.allclose(state.elastic_ratios, torch.tensor([[0.5, 0.5]]))
    assert torch.allclose(state.value, torch.sqrt(torch.tensor([2.5])))


def test_elastic_dubler_fails_closed_for_non_finite_entropy():
    with pytest.raises(AIObstructionError):
        ElasticDublerLayer()(torch.tensor([[0.0, float("nan")]]))
