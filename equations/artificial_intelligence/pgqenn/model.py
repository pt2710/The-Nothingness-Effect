"""Differentiable canonical PGQENN model."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

from equations.artificial_intelligence.shared.closure_losses import arbitrate, parseval_residual
from equations.artificial_intelligence.shared.elastic_pi_gates import ElasticPiGate
from equations.artificial_intelligence.shared.entropy_gates import normalized_dfi, parity_conditioned_dfi
from equations.artificial_intelligence.shared.provenance import backend_metadata
from equations.artificial_intelligence.shared.types import TNEAIOutput, require_finite_tensor

from .growth_law import CanonicalPrimeGrowth, PrimeGraph
from .message_passing import PrimeEquivariantMessagePassing


@dataclass
class PGQENNOutput(TNEAIOutput):
    graph: PrimeGraph | None = None
    pdfi: torch.Tensor | None = None
    node_state: torch.Tensor | None = None


class PGQENNModel(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, *, K_D: float = 1.0, motif_width: int = 2):
        super().__init__()
        if min(input_dim, hidden_dim, output_dim) <= 0:
            raise ValueError("PGQENN dimensions must be positive")
        self.growth = CanonicalPrimeGrowth(motif_width)
        self.message_passing = PrimeEquivariantMessagePassing(input_dim, hidden_dim)
        self.elastic_gate = ElasticPiGate(K_D)
        self.readout_layer = nn.Linear(hidden_dim, output_dim)

    def forward(self, features: torch.Tensor, graph: PrimeGraph | None = None, *, tolerance: float = 1e-5) -> PGQENNOutput:
        require_finite_tensor(features, "PGQENN input")
        if features.ndim != 2 or features.shape[1] != self.message_passing.linear.linear.in_features:
            raise ValueError("PGQENN input must have shape [nodes, input_dim]")
        graph = graph or self.growth.build(features.shape[0], dtype=features.dtype)
        hidden = self.message_passing(features, graph)
        dfi = normalized_dfi(features, 1.0)
        adjacency = graph.adjacency.to(dtype=features.dtype, device=features.device)
        degree_sequence = adjacency.sum(dim=-1) + 1.0
        parity_mask = torch.tensor(
            [(index + graph.two_adic_depths[index].value) % 2 for index in range(len(graph.primes) - 1)],
            dtype=features.dtype,
            device=features.device,
        )
        pdfi = parity_conditioned_dfi(degree_sequence, parity_mask)
        entropy = dfi.abs() + pdfi
        elastic = self.elastic_gate(entropy)
        gain = torch.mean(elastic / torch.pi, dim=-1, keepdim=True)
        node_state = require_finite_tensor(hidden * gain, "PGQENN gated state")
        logits = self.readout_layer(node_state.mean(dim=0, keepdim=True))
        observation = torch.softmax(logits, dim=-1)
        residuals = {
            "message_equivariance": self.message_passing.equivariance_residual(features, graph),
            "graph_symmetry": torch.linalg.vector_norm(adjacency - adjacency.T),
            "self_loop": torch.linalg.vector_norm(torch.diagonal(adjacency)),
            "parseval": parseval_residual(node_state),
        }
        status = arbitrate(residuals, tolerance)
        return PGQENNOutput(
            node_state, logits, observation, dfi, elastic, residuals, status,
            {**backend_metadata(), "architecture": "PGQENN", "growth_mode": graph.growth_mode},
            graph, pdfi, node_state,
        )
