"""Learned modality axes with explicit shared/private and cycle residuals."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn
from torch.nn import functional

from the_nothingness_effect.artificial_intelligence.shared.types import (
    AIObstructionError,
    require_finite_tensor,
)


@dataclass(frozen=True)
class ModalityAxisState:
    modality_names: tuple[str, ...]
    axis_latents: torch.Tensor
    shared_latents: torch.Tensor
    private_latents: torch.Tensor
    mapped_axes: torch.Tensor
    adjacency: torch.Tensor
    reverse_adjacency: torch.Tensor
    reconstructed_axes: torch.Tensor
    fused_axis: torch.Tensor
    residuals: dict[str, torch.Tensor]


class ModalityAxisNetwork(nn.Module):
    """Map named modality tokens onto interacting learned axes.

    The same encoder is used for every modality.  Pairwise adjacency is built
    from the shared coordinates, while private coordinates stay attached to
    their originating modality.  A reverse transport makes cycle failure
    measurable instead of assuming cross-modal equivalence.
    """

    def __init__(self, input_dim: int, axis_dim: int, *, shared_dim: int | None = None) -> None:
        super().__init__()
        if input_dim < 2 or axis_dim < 4:
            raise AIObstructionError("axis input_dim must be >= 2 and axis_dim >= 4")
        split = axis_dim // 2 if shared_dim is None else int(shared_dim)
        if split < 1 or split >= axis_dim:
            raise AIObstructionError("axis shared_dim must lie strictly inside axis_dim")
        self.input_dim = int(input_dim)
        self.axis_dim = int(axis_dim)
        self.shared_dim = split
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, axis_dim, bias=False),
            nn.LayerNorm(axis_dim),
            nn.SiLU(),
        )
        self.forward_transport = nn.Linear(axis_dim, axis_dim, bias=False)
        self.reverse_transport = nn.Linear(axis_dim, axis_dim, bias=False)
        with torch.no_grad():
            self.forward_transport.weight.copy_(torch.eye(axis_dim))
            self.reverse_transport.weight.copy_(torch.eye(axis_dim))
        self.log_temperature = nn.Parameter(torch.zeros(()))

    def forward(
        self,
        tokens: torch.Tensor,
        modality_names: tuple[str, ...],
        modality_weights: torch.Tensor,
    ) -> ModalityAxisState:
        require_finite_tensor(tokens, "modality-axis input tokens")
        require_finite_tensor(modality_weights, "modality-axis weights")
        if tokens.ndim != 3 or tokens.shape[-1] != self.input_dim:
            raise AIObstructionError(
                f"axis tokens must have shape [batch, modalities, {self.input_dim}]"
            )
        batch, modality_count, _ = tokens.shape
        if modality_count < 2 or len(modality_names) != modality_count:
            raise AIObstructionError("axis network requires a unique name for each modality")
        if len(set(modality_names)) != modality_count:
            raise AIObstructionError("modality-axis names must be unique")
        if modality_weights.shape != (batch, modality_count):
            raise AIObstructionError("modality-axis weights have the wrong shape")

        axes = require_finite_tensor(self.encoder(tokens), "encoded modality axes")
        shared = axes[..., : self.shared_dim]
        private = axes[..., self.shared_dim :]
        normalized = functional.normalize(shared, dim=-1, eps=1e-8)
        temperature = functional.softplus(self.log_temperature) + 1e-4
        similarity = torch.einsum("bmd,bnd->bmn", normalized, normalized) / temperature
        adjacency = require_finite_tensor(
            torch.softmax(similarity, dim=-1), "modality-axis adjacency"
        )
        transported = self.forward_transport(axes)
        mapped = require_finite_tensor(
            torch.einsum("bmn,bnd->bmd", adjacency, transported),
            "forward modality-axis transport",
        )
        reverse = adjacency.transpose(-1, -2)
        reverse = reverse / reverse.sum(dim=-1, keepdim=True).clamp_min(1e-8)
        reconstructed = require_finite_tensor(
            self.reverse_transport(torch.einsum("bmn,bnd->bmd", reverse, mapped)),
            "reverse modality-axis transport",
        )
        normalized_weights = modality_weights / modality_weights.sum(
            dim=-1, keepdim=True
        ).clamp_min(1e-8)
        fused = require_finite_tensor(
            torch.sum(normalized_weights.unsqueeze(-1) * mapped, dim=1),
            "fused modality-axis state",
        )
        identity = torch.eye(modality_count, dtype=tokens.dtype, device=tokens.device)
        cycle_matrix = torch.matmul(reverse, adjacency)
        residuals = {
            "axis_adjacency_normalization": torch.max(
                torch.abs(adjacency.sum(dim=-1) - 1.0)
            ),
            "axis_reverse_normalization": torch.max(
                torch.abs(reverse.sum(dim=-1) - 1.0)
            ),
            "axis_transport_cycle": torch.sqrt(torch.mean((reconstructed - axes) ** 2)),
            "axis_cycle_identity": torch.sqrt(
                torch.mean((cycle_matrix - identity.unsqueeze(0)) ** 2)
            ),
            "axis_shared_alignment": torch.sqrt(
                torch.mean((mapped[..., : self.shared_dim] - shared) ** 2)
            ),
        }
        for name, residual in residuals.items():
            require_finite_tensor(residual, name)
        return ModalityAxisState(
            modality_names=modality_names,
            axis_latents=axes,
            shared_latents=shared,
            private_latents=private,
            mapped_axes=mapped,
            adjacency=adjacency,
            reverse_adjacency=reverse,
            reconstructed_axes=reconstructed,
            fused_axis=fused,
            residuals=residuals,
        )
