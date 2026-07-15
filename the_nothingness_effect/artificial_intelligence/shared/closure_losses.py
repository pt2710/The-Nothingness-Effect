"""Differentiable closure, Parseval, and source-removal losses."""

from __future__ import annotations

import torch

from .types import AIClosureStatus, AIObstructionError, require_finite_tensor


def parseval_residual(value: torch.Tensor) -> torch.Tensor:
    spectrum = torch.fft.fft(value, dim=-1, norm="ortho")
    source_energy = torch.sum(torch.abs(value) ** 2)
    spectral_energy = torch.sum(torch.abs(spectrum) ** 2)
    return torch.abs(source_energy - spectral_energy)


def bidirectional_closure_residual(first: torch.Tensor, second: torch.Tensor) -> torch.Tensor:
    if first.shape != second.shape:
        raise AIObstructionError("bidirectional closure requires equal-shaped sources")
    return torch.linalg.vector_norm((first + second) - (second + first))


def source_removal_residual(complete: torch.Tensor, removed: torch.Tensor) -> torch.Tensor:
    if complete.shape != removed.shape:
        raise AIObstructionError("source-removal responses must share a shape")
    return torch.linalg.vector_norm(complete - removed)


def arbitrate(residuals: dict[str, torch.Tensor], tolerance: float) -> AIClosureStatus:
    if tolerance < 0 or not math_isfinite(tolerance):
        raise AIObstructionError("AI arbitration tolerance must be finite and non-negative")
    if not residuals:
        raise AIObstructionError("AI arbitration requires residual evidence")
    for name, residual in residuals.items():
        require_finite_tensor(residual, f"AI residual {name}")
    return AIClosureStatus.NUMERICAL_CANDIDATE if all(float(item.detach()) <= tolerance for item in residuals.values()) else AIClosureStatus.OPEN


def math_isfinite(value: float) -> bool:
    return value == value and value not in (float("inf"), float("-inf"))
