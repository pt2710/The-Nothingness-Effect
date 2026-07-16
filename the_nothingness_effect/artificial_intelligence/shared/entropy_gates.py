"""Differentiable DFI and parity-conditioned pDFI gates."""

from __future__ import annotations

import torch

from .types import AIObstructionError, require_finite_tensor


def normalized_dfi(value: torch.Tensor, spectrum_scale: torch.Tensor | float) -> torch.Tensor:
    if value.ndim != 2 or value.shape[1] < 2:
        raise AIObstructionError("differentiable DFI expects [samples, features] with at least two features")
    require_finite_tensor(value, "differentiable DFI input")
    scale = torch.as_tensor(spectrum_scale, dtype=value.dtype, device=value.device)
    if scale.numel() != 1 or not bool(torch.isfinite(scale)) or not bool(scale > 0):
        raise AIObstructionError("differentiable DFI scale must be finite and positive")
    feature_count = value.shape[1]
    total = value.sum(dim=1, keepdim=True)
    remainder = total - value
    denominator = remainder * feature_count
    if bool((denominator == 0).any()):
        raise AIObstructionError("differentiable DFI denominator obstruction")
    weight = total * (feature_count - 1) / denominator
    result = (weight - 1.0) / feature_count
    return require_finite_tensor(result, "differentiable DFI output")


def parity_conditioned_dfi(sequence: torch.Tensor, parity_mask: torch.Tensor) -> torch.Tensor:
    if sequence.ndim != 1 or parity_mask.shape != (sequence.numel() - 1,):
        raise AIObstructionError("pDFI expects a scalar sequence and one mask value per transition")
    require_finite_tensor(sequence, "pDFI sequence")
    require_finite_tensor(parity_mask, "pDFI mask")
    if not bool(((parity_mask == 0) | (parity_mask == 1)).all()):
        raise AIObstructionError("pDFI parity mask must be binary")
    predecessors = sequence[:-1]
    if bool((predecessors == 0).any()):
        raise AIObstructionError("pDFI zero predecessor obstruction")
    increments = torch.abs((sequence[1:] - predecessors) / predecessors)
    return require_finite_tensor(torch.mean(parity_mask * increments), "pDFI output")


def batch_parity_conditioned_dfi(sequence: torch.Tensor) -> torch.Tensor:
    """Evaluate pDFI independently across each row of a feature trajectory."""

    if sequence.ndim != 2 or sequence.shape[1] < 2:
        raise AIObstructionError(
            "batched pDFI expects [samples, features] with at least two features"
        )
    require_finite_tensor(sequence, "batched pDFI sequence")
    predecessors = sequence[:, :-1]
    if bool((predecessors == 0).any()):
        raise AIObstructionError("batched pDFI zero predecessor obstruction")
    parity_mask = (
        torch.arange(1, sequence.shape[1], device=sequence.device) % 2
    ).to(dtype=sequence.dtype)
    increments = torch.abs((sequence[:, 1:] - predecessors) / predecessors)
    result = torch.mean(increments * parity_mask.unsqueeze(0), dim=-1, keepdim=True)
    return require_finite_tensor(result, "batched pDFI output")
