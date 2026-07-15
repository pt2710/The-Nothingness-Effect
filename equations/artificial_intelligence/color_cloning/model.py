"""Reversible spectral color cloning with fail-closed domain checks."""

from __future__ import annotations

import torch
from torch import nn

from equations.artificial_intelligence.shared.capability_runtime import CloneOutput, spectral_clone
from equations.artificial_intelligence.shared.types import AIObstructionError, require_finite_tensor


class ColorCloner(nn.Module):
    def forward(self, image: torch.Tensor, *, tolerance: float = 1e-5) -> CloneOutput:
        image = torch.as_tensor(image, dtype=torch.float32)
        require_finite_tensor(image, "color clone image")
        if image.ndim != 3 or image.shape[-1] != 3 or min(image.shape[:2]) < 4:
            raise AIObstructionError("color cloning requires one [height, width, 3] RGB image")
        if bool((image < 0).any()) or bool((image > 1).any()):
            raise AIObstructionError("color cloning values must lie in [0, 1]")
        return spectral_clone(image, dimensions=(0, 1), tolerance=tolerance)
