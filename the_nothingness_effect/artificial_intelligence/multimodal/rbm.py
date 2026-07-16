"""Typed, fail-closed energy layers for the multimodal TNE realization.

The restricted Boltzmann machine is an external numerical realization.  It is
not presented as a TNE source law.  Its free energy and reconstruction error
are exposed so downstream code cannot confuse a finite latent with closure.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch import nn
from torch.nn import functional

from the_nothingness_effect.artificial_intelligence.shared.types import (
    AIObstructionError,
    require_finite_tensor,
)


@dataclass(frozen=True)
class RBMEnergyState:
    """Complete deterministic mean-field evaluation of one energy layer."""

    hidden_probability: torch.Tensor
    visible_reconstruction: torch.Tensor
    free_energy: torch.Tensor
    negative_free_energy: torch.Tensor
    contrastive_divergence: torch.Tensor
    reconstruction_residual: torch.Tensor


class GaussianBernoulliEnergyLayer(nn.Module):
    """CPU-testable Gaussian-visible/Bernoulli-hidden RBM.

    Canonical evaluation uses deterministic hidden probabilities.  Stochastic
    Bernoulli sampling is available only when explicitly requested and never
    masks non-finite inputs or outputs.
    """

    def __init__(
        self,
        visible_dim: int,
        hidden_dim: int,
        *,
        weight_scale: float = 0.02,
    ) -> None:
        super().__init__()
        if visible_dim < 2 or hidden_dim < 1:
            raise AIObstructionError("RBM dimensions must be positive and visible_dim >= 2")
        if not math.isfinite(weight_scale) or weight_scale <= 0:
            raise AIObstructionError("RBM weight_scale must be finite and positive")
        self.visible_dim = int(visible_dim)
        self.hidden_dim = int(hidden_dim)
        self.weight = nn.Parameter(weight_scale * torch.randn(visible_dim, hidden_dim))
        self.visible_bias = nn.Parameter(torch.zeros(visible_dim))
        self.hidden_bias = nn.Parameter(torch.zeros(hidden_dim))

    def _validate_visible(self, visible: torch.Tensor) -> torch.Tensor:
        require_finite_tensor(visible, "RBM visible state")
        if visible.ndim != 2 or visible.shape[-1] != self.visible_dim:
            raise AIObstructionError(
                f"RBM visible state must have shape [batch, {self.visible_dim}]"
            )
        if visible.shape[0] < 1:
            raise AIObstructionError("RBM visible batch cannot be empty")
        return visible

    def hidden_probability(self, visible: torch.Tensor) -> torch.Tensor:
        visible = self._validate_visible(visible)
        return require_finite_tensor(
            torch.sigmoid(visible @ self.weight + self.hidden_bias),
            "RBM hidden probability",
        )

    def visible_mean(self, hidden: torch.Tensor) -> torch.Tensor:
        require_finite_tensor(hidden, "RBM hidden state")
        if hidden.ndim != 2 or hidden.shape[-1] != self.hidden_dim:
            raise AIObstructionError(
                f"RBM hidden state must have shape [batch, {self.hidden_dim}]"
            )
        return require_finite_tensor(
            hidden @ self.weight.T + self.visible_bias,
            "RBM reconstructed visible mean",
        )

    def free_energy(self, visible: torch.Tensor) -> torch.Tensor:
        visible = self._validate_visible(visible)
        quadratic = 0.5 * torch.sum((visible - self.visible_bias) ** 2, dim=-1)
        hidden_marginal = torch.sum(
            functional.softplus(visible @ self.weight + self.hidden_bias), dim=-1
        )
        return require_finite_tensor(quadratic - hidden_marginal, "RBM free energy")

    def forward(
        self,
        visible: torch.Tensor,
        *,
        steps: int = 1,
        stochastic: bool = False,
        generator: torch.Generator | None = None,
    ) -> RBMEnergyState:
        visible = self._validate_visible(visible)
        if steps < 1:
            raise AIObstructionError("RBM contrastive-divergence steps must be positive")
        negative = visible
        hidden = self.hidden_probability(negative)
        for _ in range(steps):
            hidden = self.hidden_probability(negative)
            carrier = (
                torch.bernoulli(hidden, generator=generator)
                if stochastic
                else hidden
            )
            negative = self.visible_mean(carrier)
        positive_energy = self.free_energy(visible)
        negative_energy = self.free_energy(negative)
        divergence = require_finite_tensor(
            torch.mean(positive_energy - negative_energy),
            "RBM contrastive divergence",
        )
        reconstruction = require_finite_tensor(
            torch.sqrt(torch.mean((negative - visible) ** 2)),
            "RBM reconstruction residual",
        )
        return RBMEnergyState(
            hidden_probability=hidden,
            visible_reconstruction=negative,
            free_energy=positive_energy,
            negative_free_energy=negative_energy,
            contrastive_divergence=divergence,
            reconstruction_residual=reconstruction,
        )
