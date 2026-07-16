from __future__ import annotations

import pytest
import torch

from the_nothingness_effect.artificial_intelligence.multimodal import (
    AdaptiveModalityClusterNetwork,
    GaussianBernoulliEnergyLayer,
    ModalityAxisNetwork,
)


def test_modality_axes_transport_all_sources_and_expose_cycle_residual() -> None:
    torch.manual_seed(4)
    layer = ModalityAxisNetwork(input_dim=6, axis_dim=8)
    tokens = torch.rand(5, 3, 6)
    weights = torch.softmax(torch.rand(5, 3), dim=-1)
    state = layer(tokens, ("color", "sound", "vision"), weights)

    assert state.mapped_axes.shape == (5, 3, 8)
    assert state.shared_latents.shape == (5, 3, 4)
    assert torch.allclose(state.adjacency.sum(dim=-1), torch.ones(5, 3), atol=1e-6)
    assert set(state.residuals) >= {
        "axis_transport_cycle",
        "axis_cycle_identity",
        "axis_shared_alignment",
    }
    altered = tokens.clone()
    altered[:, 1] = altered[:, 1] + 2.0
    altered_state = layer(altered, ("color", "sound", "vision"), weights)
    assert not torch.allclose(state.fused_axis, altered_state.fused_axis)


def test_rbm_energy_layer_is_differentiable_and_fails_closed() -> None:
    torch.manual_seed(5)
    layer = GaussianBernoulliEnergyLayer(visible_dim=8, hidden_dim=4)
    visible = torch.rand(7, 8, requires_grad=True)
    state = layer(visible, steps=2)
    loss = state.contrastive_divergence.abs() + state.reconstruction_residual
    loss.backward()

    assert state.hidden_probability.shape == (7, 4)
    assert visible.grad is not None
    assert layer.weight.grad is not None
    with pytest.raises(Exception):
        layer(torch.tensor([[float("nan")] * 8]))


def test_cluster_network_grows_deterministically_and_tracks_topology() -> None:
    layer = AdaptiveModalityClusterNetwork(
        4, max_clusters=8, spawn_threshold=0.25, learning_rate=0.4
    )
    first = torch.tensor(
        [
            [[0.0, 0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 1.0]],
            [[0.02, 0.0, 0.0, 0.0], [1.02, 1.0, 1.0, 1.0]],
        ]
    )
    state_a = layer(first, ("color", "sound"), update=True)
    second = first + torch.tensor([[[2.0, 0.0, 0.0, 0.0], [0.0, 2.0, 0.0, 0.0]]])
    state_b = layer(second, ("color", "sound"), update=True)

    assert state_a.active_clusters == 2
    assert state_b.active_clusters > state_a.active_clusters
    assert state_b.topology_adjacency.shape == (
        state_b.active_clusters,
        state_b.active_clusters,
    )
    assert torch.allclose(state_b.topology_adjacency, state_b.topology_adjacency.T)
    assert any(event.event == "spawn" for event in state_b.events)
