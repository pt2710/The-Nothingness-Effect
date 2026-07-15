"""Exact differentiable Elastic-pi gain without silent clipping."""

from __future__ import annotations

import math

import torch
from torch import nn

from .types import AIObstructionError, require_finite_tensor


class ElasticPiGate(nn.Module):
    def __init__(self, K_D: float = 1.0):
        super().__init__()
        if not math.isfinite(K_D) or K_D <= 0:
            raise AIObstructionError("Elastic-pi K_D must be finite and positive")
        self.register_buffer("K_D", torch.tensor(float(K_D)))

    def forward(self, entropy: torch.Tensor) -> torch.Tensor:
        require_finite_tensor(entropy, "Elastic-pi entropy")
        result = torch.pi * torch.exp(-entropy / self.K_D.to(dtype=entropy.dtype))
        if bool((result == 0).any()) or not bool(torch.isfinite(result).all()):
            raise AIObstructionError("Elastic-pi differentiable evaluation overflowed or underflowed")
        return result
