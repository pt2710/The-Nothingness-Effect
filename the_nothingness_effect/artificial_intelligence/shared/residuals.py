"""Residual collection utilities."""

from __future__ import annotations

import torch

from .types import require_finite_tensor


def residual_vector(residuals: dict[str, torch.Tensor]) -> torch.Tensor:
    result = torch.stack([item.reshape(()) for item in residuals.values()])
    return require_finite_tensor(result, "AI residual vector")
