from __future__ import annotations

import torch

from the_nothingness_effect.artificial_intelligence.pgqenn.growth_law import (
    CanonicalPrimeGrowth,
    spatial_locality_adjacency,
    stochastic_comparison_graph,
)
from the_nothingness_effect.artificial_intelligence.pgqenn.model import PGQENNModel
from the_nothingness_effect.artificial_intelligence.pgqenn.training import training_step


def test_prime_growth_is_deterministic_typed_and_distinct_from_ablation():
    first = CanonicalPrimeGrowth().build(9)
    second = CanonicalPrimeGrowth().build(9)
    ablation = stochastic_comparison_graph(9, seed=3)
    assert first.primes == (2, 3, 5, 7, 11, 13, 17, 19, 23)
    assert first.two_adic_depths == second.two_adic_depths
    assert torch.equal(first.adjacency, second.adjacency)
    assert torch.equal(first.coordinates_3d, second.coordinates_3d)
    assert torch.equal(first.spatial_adjacency, second.spatial_adjacency)
    assert first.coordinates_3d.shape == (9, 3)
    assert int(torch.linalg.matrix_rank(first.coordinates_3d - first.coordinates_3d.mean(0))) == 3
    flattened_motif_axis = first.coordinates_3d.clone()
    flattened_motif_axis[:, 1] = 0.0
    assert not torch.allclose(
        first.spatial_adjacency,
        spatial_locality_adjacency(first.adjacency, flattened_motif_axis),
    )
    assert first.growth_mode == "mpl_tc_prime_motif"
    signed = first.signed_triadic_growth
    assert signed is not None
    assert signed.spectrum_counts == {"positive": 52, "negative": 52}
    assert signed.value_involution_residual == 0.0
    assert signed.coordinate_asymmetry > 0.0
    split = signed.positive_node_count
    assert not torch.allclose(
        signed.coordinates_3d[split:], -signed.coordinates_3d[:split]
    )
    assert not torch.allclose(
        signed.spatial_adjacency[:split, :split],
        signed.spatial_adjacency[split:, split:],
    )
    assert first.dependency_commit == "056e346824e9ec9785ab45b642b3b842c88f6e56"
    assert len(first.motifs) == len(first.primes)
    assert ablation.growth_mode == "stochastic_comparison_ablation"
    assert not torch.equal(first.adjacency, ablation.adjacency)


def test_pgqenn_uses_equivariant_messages_pdfi_elastic_gain_and_gradients():
    torch.manual_seed(0)
    model = PGQENNModel(5, 7, 3)
    features = (torch.rand((9, 5)) + 0.2).requires_grad_()
    output = model(features)
    assert output.graph is not None and output.graph.growth_mode == "mpl_tc_prime_motif"
    assert output.qenn_backbone_output is not None
    assert output.qenn_backbone_output.dtqc_state is not None
    assert output.qenn_backbone_output.observation_collapse_state is not None
    assert output.observation_collapse_state is not None
    assert output.metadata["architecture_base"] == "QENN"
    assert output.metadata["qenn_observation_collapse_integration"] == "canonical_runtime"
    assert output.metadata["observation_collapse_integration"] == "canonical_runtime"
    assert output.metadata["mpl_tc_commit"] == "056e346824e9ec9785ab45b642b3b842c88f6e56"
    assert output.metadata["growth_geometry"] == "prime_shell_x_mpl_tc_motif_x_two_adic_run_depth"
    assert output.metadata["triadic_stream_integration"] == "experimental_finite_prefix_structural_bridge"
    assert set(output.metadata["triadic_stream_counts"]) == {
        "pure_even_lift", "first_order_odd", "lpf_odd_composite", "mixed_even_composite"
    }
    assert float(output.triadic_stream_source_removal_delta.detach()) > 0.0
    assert float(output.signed_spectrum_source_removal_delta.detach()) > 0.0
    assert output.metadata["signed_spectrum_integration"] == "tne_flowpoint_involution_lift"
    assert output.metadata["signed_spectrum_counts"]["positive"] == output.metadata["signed_spectrum_counts"]["negative"]
    assert output.pdfi is not None and torch.isfinite(output.pdfi)
    assert output.node_state is not None and output.node_state.shape == (9, 7)
    assert float(output.residuals["message_equivariance"].detach()) == 0.0
    assert float(output.residuals["collapse_idempotence"].detach()) == 0.0
    loss = training_step(model, features, torch.tensor(1))
    loss.backward()
    assert features.grad is not None
    assert all(parameter.grad is not None for parameter in model.parameters())
