"""C2-equivariant differentiable layers."""

from __future__ import annotations

import torch
from torch import nn

from .types import require_finite_tensor


class C2EquivariantLinear(nn.Module):
    """Bias-free linear map satisfying L(-x)=-L(x)."""

    def __init__(self, input_dim: int, output_dim: int):
        super().__init__()
        self.linear = nn.Linear(input_dim, output_dim, bias=False)

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        result = self.linear(require_finite_tensor(value, "equivariant input"))
        return require_finite_tensor(result, "equivariant output")

    def equivariance_residual(self, value: torch.Tensor) -> torch.Tensor:
        return torch.linalg.vector_norm(self(-value) + self(value))


class SpectralMemory(nn.Module):
    """Exact finite real-FFT memory/reconstruction layer."""

    def forward(self, value: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        spectrum = torch.fft.rfft(value, dim=-1, norm="ortho")
        reconstruction = torch.fft.irfft(spectrum, n=value.shape[-1], dim=-1, norm="ortho")
        require_finite_tensor(reconstruction, "spectral reconstruction")
        return reconstruction, torch.linalg.vector_norm(reconstruction - value)
