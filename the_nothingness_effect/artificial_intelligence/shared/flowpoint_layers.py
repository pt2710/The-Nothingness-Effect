"""Differentiable Flowpoint involution and projectors."""

from __future__ import annotations

import torch
from torch import nn

from .types import require_finite_tensor


class FlowpointLayer(nn.Module):
    """Canonical self-negating involution F(x)=-x."""

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        require_finite_tensor(value, "Flowpoint input")
        return -value

    def inverse(self, value: torch.Tensor) -> torch.Tensor:
        return self.forward(value)

    def involution_residual(self, value: torch.Tensor) -> torch.Tensor:
        return torch.linalg.vector_norm(self(self(value)) - value)


def invariant_projector(value: torch.Tensor, involution: nn.Module) -> torch.Tensor:
    return 0.5 * (value + involution(value))


def anti_invariant_projector(value: torch.Tensor, involution: nn.Module) -> torch.Tensor:
    return 0.5 * (value - involution(value))
