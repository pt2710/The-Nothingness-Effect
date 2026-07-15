from __future__ import annotations

import torch

from equations.artificial_intelligence.pgqenn.growth_law import CanonicalPrimeGrowth, stochastic_comparison_graph
from equations.artificial_intelligence.pgqenn.model import PGQENNModel
from equations.artificial_intelligence.pgqenn.training import training_step


def test_prime_growth_is_deterministic_typed_and_distinct_from_ablation():
    first = CanonicalPrimeGrowth().build(9)
    second = CanonicalPrimeGrowth().build(9)
    ablation = stochastic_comparison_graph(9, seed=3)
    assert first.primes == (2, 3, 5, 7, 11, 13, 17, 19, 23)
    assert first.two_adic_depths == second.two_adic_depths
    assert torch.equal(first.adjacency, second.adjacency)
    assert first.growth_mode == "canonical_prime_parity"
    assert ablation.growth_mode == "stochastic_comparison_ablation"
    assert not torch.equal(first.adjacency, ablation.adjacency)


def test_pgqenn_uses_equivariant_messages_pdfi_elastic_gain_and_gradients():
    torch.manual_seed(0)
    model = PGQENNModel(5, 7, 3)
    features = (torch.rand((9, 5)) + 0.2).requires_grad_()
    output = model(features)
    assert output.graph is not None and output.graph.growth_mode == "canonical_prime_parity"
    assert output.pdfi is not None and torch.isfinite(output.pdfi)
    assert output.node_state is not None and output.node_state.shape == (9, 7)
    assert float(output.residuals["message_equivariance"].detach()) == 0.0
    loss = training_step(model, features, torch.tensor(1))
    loss.backward()
    assert features.grad is not None
    assert all(parameter.grad is not None for parameter in model.parameters())
