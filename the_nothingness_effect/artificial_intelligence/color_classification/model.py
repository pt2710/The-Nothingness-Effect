"""Typed color-patch classification using TNE observation/collapse."""

from __future__ import annotations

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.shared.capability_fixtures import COLOR_LABELS, COLOR_PROTOTYPES
from the_nothingness_effect.artificial_intelligence.shared.capability_runtime import ClassificationOutput, TNEPrototypeClassifier
from the_nothingness_effect.artificial_intelligence.shared.types import AIObstructionError, require_finite_tensor


class ColorClassifier(nn.Module):
    """Classify finite RGB images into six deterministic color prototypes."""

    def __init__(self, *, K_D: float = 1.0) -> None:
        super().__init__()
        self.core = TNEPrototypeClassifier(COLOR_PROTOTYPES, COLOR_LABELS, K_D=K_D, temperature=0.08)

    @staticmethod
    def extract_features(images: torch.Tensor) -> torch.Tensor:
        images = torch.as_tensor(images, dtype=torch.float32)
        require_finite_tensor(images, "color images")
        if images.ndim != 4 or images.shape[-1] != 3 or min(images.shape[1:3]) < 2:
            raise AIObstructionError("color classification requires [batch, height, width, 3] RGB images")
        if bool((images < 0).any()) or bool((images > 1).any()):
            raise AIObstructionError("color image values must lie in the normalized [0, 1] codomain")
        return images.mean(dim=(1, 2))

    def forward(self, images: torch.Tensor, *, tolerance: float = 1e-6) -> ClassificationOutput:
        return self.core(self.extract_features(images), tolerance=tolerance)

    def decode(self, class_indices: torch.Tensor, *, image_size: int = 12) -> torch.Tensor:
        if image_size < 2:
            raise AIObstructionError("decoded color patches require at least two pixels per axis")
        colors = self.core.decode(class_indices)
        return colors[:, None, None, :].expand(-1, image_size, image_size, -1).clone()
