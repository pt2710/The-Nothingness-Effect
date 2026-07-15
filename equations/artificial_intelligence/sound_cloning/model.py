"""Reversible spectral sound cloning with fail-closed domain checks."""

from __future__ import annotations

import torch
from torch import nn

from equations.artificial_intelligence.shared.capability_runtime import CloneOutput, spectral_clone
from equations.artificial_intelligence.shared.types import AIObstructionError, require_finite_tensor


class SoundCloner(nn.Module):
    def forward(self, waveform: torch.Tensor, *, tolerance: float = 1e-4) -> CloneOutput:
        waveform = torch.as_tensor(waveform, dtype=torch.float32)
        require_finite_tensor(waveform, "sound clone waveform")
        if waveform.ndim != 1 or waveform.numel() < 128:
            raise AIObstructionError("sound cloning requires one waveform with at least 128 samples")
        if bool((waveform.abs() > 1.0 + 1e-6).any()):
            raise AIObstructionError("sound cloning amplitudes must lie in [-1, 1]")
        return spectral_clone(waveform, dimensions=(0,), tolerance=tolerance)
