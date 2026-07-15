"""Color -> label -> color -> label closure for TNE visual evidence."""

from __future__ import annotations

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.color_classification import ColorClassifier
from the_nothingness_effect.artificial_intelligence.shared.capability_runtime import BidirectionalOutput
from the_nothingness_effect.artificial_intelligence.shared.provenance import backend_metadata
from the_nothingness_effect.artificial_intelligence.shared.types import AIClosureStatus, require_finite_tensor


class BidirectionalColorClassifier(nn.Module):
    def __init__(self, *, K_D: float = 1.0) -> None:
        super().__init__()
        self.classifier = ColorClassifier(K_D=K_D)

    def forward(self, images: torch.Tensor, *, tolerance: float = 1e-6) -> BidirectionalOutput:
        forward = self.classifier(images, tolerance=tolerance)
        reconstruction = self.classifier.decode(forward.class_indices, image_size=images.shape[1])
        roundtrip = self.classifier(reconstruction, tolerance=tolerance)
        label_residual = torch.count_nonzero(roundtrip.class_indices != forward.class_indices).to(images.dtype)
        modality_residual = torch.sqrt(torch.mean((images - reconstruction) ** 2))
        require_finite_tensor(modality_residual, "bidirectional color residual")
        status = AIClosureStatus.NUMERICAL_CANDIDATE if float(label_residual) <= tolerance else AIClosureStatus.OPEN
        return BidirectionalOutput(
            forward,
            reconstruction,
            roundtrip,
            label_residual,
            modality_residual,
            status,
            {
                **backend_metadata(),
                "architecture": "SOInet-style bidirectional visual closure",
                "closure": "RGB image -> label -> RGB prototype -> label",
            },
        )
