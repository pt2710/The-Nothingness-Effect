"""Flowpoint-equivariant message passing on typed prime graphs."""

from __future__ import annotations

import torch
from torch import nn

from equations.artificial_intelligence.shared.equivariant_layers import C2EquivariantLinear
from equations.artificial_intelligence.shared.types import AIObstructionError, require_finite_tensor

from .growth_law import PrimeGraph


class PrimeEquivariantMessagePassing(nn.Module):
    def __init__(self, input_dim: int, output_dim: int):
        super().__init__()
        self.linear = C2EquivariantLinear(input_dim, output_dim)

    def forward(self, features: torch.Tensor, graph: PrimeGraph) -> torch.Tensor:
        require_finite_tensor(features, "PGQENN node features")
        if features.ndim != 2 or features.shape[0] != len(graph.primes):
            raise AIObstructionError("PGQENN node features must align with the prime graph")
        adjacency = graph.adjacency.to(dtype=features.dtype, device=features.device)
        degree = adjacency.sum(dim=-1, keepdim=True).clamp_min(torch.finfo(features.dtype).eps)
        phase = torch.tensor(
            [1.0 if depth.value % 2 == 0 else -1.0 for depth in graph.two_adic_depths],
            dtype=features.dtype,
            device=features.device,
        ).unsqueeze(-1)
        flowpoint_state = phase * features
        messages = (adjacency / degree) @ flowpoint_state
        return torch.tanh(self.linear(messages))

    def equivariance_residual(self, features: torch.Tensor, graph: PrimeGraph) -> torch.Tensor:
        return torch.linalg.vector_norm(self(-features, graph) + self(features, graph))
