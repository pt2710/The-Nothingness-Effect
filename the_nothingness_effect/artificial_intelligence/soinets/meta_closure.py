"""Bidirectional memory, spectral, and spatial meta-network closure."""

from __future__ import annotations

import torch

from the_nothingness_effect.artificial_intelligence.shared.closure_losses import parseval_residual
from the_nothingness_effect.artificial_intelligence.shared.types import AIObstructionError, require_finite_tensor


def complete_meta_adjacency(size: int, *, dtype: torch.dtype, device: torch.device) -> torch.Tensor:
    if size < 2:
        raise AIObstructionError("SOInet meta-network requires at least two subnetworks")
    adjacency = torch.ones((size, size), dtype=dtype, device=device) - torch.eye(size, dtype=dtype, device=device)
    return adjacency / float(size - 1)


def spatial_meta_closure(states: torch.Tensor, adjacency: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    require_finite_tensor(states, "SOInet meta states")
    if states.ndim != 2 or adjacency.shape != (states.shape[0], states.shape[0]):
        raise AIObstructionError("SOInet meta adjacency must align with stacked subnetwork states")
    local = states - adjacency @ states
    reconstruction = states - (local + adjacency @ states)
    boundary = torch.linalg.vector_norm(local[[0, -1]])
    return local, torch.linalg.vector_norm(reconstruction), boundary


def meta_residuals(
    states: torch.Tensor,
    adjacency: torch.Tensor,
    q_to_p: torch.Tensor,
    p_to_q: torch.Tensor,
    q_state: torch.Tensor,
    p_state: torch.Tensor,
) -> dict[str, torch.Tensor]:
    local, reconstruction, boundary = spatial_meta_closure(states, adjacency)
    return {
        "bidirectional_memory": torch.linalg.vector_norm(q_to_p - p_state) + torch.linalg.vector_norm(p_to_q - q_state),
        "spectral": parseval_residual(states),
        "spatial_reconstruction": reconstruction,
        "spatial_boundary": boundary,
        "local_observability": torch.linalg.vector_norm(local),
    }
