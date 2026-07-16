"""Sound -> label -> sound -> label closure for TNE auditory evidence."""

from __future__ import annotations

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.shared.capability_runtime import BidirectionalOutput
from the_nothingness_effect.artificial_intelligence.shared.provenance import backend_metadata
from the_nothingness_effect.artificial_intelligence.shared.types import AIClosureStatus, require_finite_tensor
from the_nothingness_effect.artificial_intelligence.sound_classification import SoundClassifier


class BidirectionalSoundClassifier(nn.Module):
    def __init__(self, *, sample_rate: int = 8000, K_D: float = 1.0) -> None:
        super().__init__()
        self.classifier = SoundClassifier(sample_rate=sample_rate, K_D=K_D)

    def forward(self, waveforms: torch.Tensor, *, tolerance: float = 1e-6) -> BidirectionalOutput:
        forward = self.classifier(waveforms, tolerance=tolerance)
        reconstruction = self.classifier.decode(forward.class_indices, sample_count=waveforms.shape[1])
        roundtrip = self.classifier(reconstruction, tolerance=tolerance)
        label_residual = torch.count_nonzero(roundtrip.class_indices != forward.class_indices).to(waveforms.dtype)
        modality_residual = torch.sqrt(torch.mean((waveforms - reconstruction) ** 2))
        require_finite_tensor(modality_residual, "bidirectional sound residual")
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
                "architecture": "SOInet-style bidirectional auditory closure",
                "closure": "waveform -> label -> prototype tone -> label",
            },
        )
