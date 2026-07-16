"""Flowpoint-equivariant message passing on typed prime graphs."""

from __future__ import annotations

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.shared.equivariant_layers import C2EquivariantLinear
from the_nothingness_effect.artificial_intelligence.shared.types import AIObstructionError, require_finite_tensor

from .growth_law import PrimeGraph


class PrimeEquivariantMessagePassing(nn.Module):
    def __init__(self, input_dim: int, output_dim: int):
        super().__init__()
        self.linear = C2EquivariantLinear(input_dim, output_dim)

    def forward(
        self,
        features: torch.Tensor,
        graph: PrimeGraph,
        *,
        use_triadic_streams: bool = True,
        use_signed_spectrum: bool = True,
    ) -> torch.Tensor:
        require_finite_tensor(features, "PGQENN node features")
        if features.ndim != 2 or features.shape[0] != len(graph.primes):
            raise AIObstructionError("PGQENN node features must align with the prime graph")
        adjacency = graph.message_adjacency.to(
            dtype=features.dtype, device=features.device
        )
        degree = adjacency.sum(dim=-1, keepdim=True).clamp_min(torch.finfo(features.dtype).eps)
        phase = torch.tensor(
            [1.0 if depth.value % 2 == 0 else -1.0 for depth in graph.two_adic_depths],
            dtype=features.dtype,
            device=features.device,
        ).unsqueeze(-1)
        flowpoint_state = phase * features
        prime_messages = (adjacency / degree) @ flowpoint_state
        messages = prime_messages
        if use_triadic_streams:
            triadic = (
                graph.signed_triadic_growth
                if use_signed_spectrum
                else graph.triadic_growth
            )
            if triadic is None:
                raise AIObstructionError(
                    "four-stream message passing requires typed triadic growth"
                )
            source_indices = torch.tensor(
                triadic.source_prime_indices,
                dtype=torch.long,
                device=features.device,
            )
            assignment = torch.nn.functional.one_hot(
                source_indices, num_classes=len(graph.primes)
            ).to(dtype=features.dtype)
            if use_signed_spectrum:
                signs = torch.tensor(
                    triadic.spectrum_signs,
                    dtype=features.dtype,
                    device=features.device,
                ).unsqueeze(-1)
            else:
                signs = torch.ones(
                    (len(triadic.source_prime_indices), 1),
                    dtype=features.dtype,
                    device=features.device,
                )
            triadic_features = signs * (assignment @ flowpoint_state)
            triadic_adjacency = triadic.spatial_adjacency.to(
                dtype=features.dtype, device=features.device
            )
            triadic_degree = triadic_adjacency.sum(dim=-1, keepdim=True).clamp_min(
                torch.finfo(features.dtype).eps
            )
            triadic_messages = (triadic_adjacency / triadic_degree) @ triadic_features
            source_count = assignment.T.sum(dim=-1, keepdim=True).clamp_min(1.0)
            pooled = assignment.T @ (signs * triadic_messages) / source_count
            messages = 0.5 * (prime_messages + pooled)
        return torch.tanh(self.linear(messages))

    def equivariance_residual(
        self,
        features: torch.Tensor,
        graph: PrimeGraph,
        *,
        use_triadic_streams: bool = True,
        use_signed_spectrum: bool = True,
    ) -> torch.Tensor:
        return torch.linalg.vector_norm(
            self(
                -features,
                graph,
                use_triadic_streams=use_triadic_streams,
                use_signed_spectrum=use_signed_spectrum,
            )
            + self(
                features,
                graph,
                use_triadic_streams=use_triadic_streams,
                use_signed_spectrum=use_signed_spectrum,
            )
        )
