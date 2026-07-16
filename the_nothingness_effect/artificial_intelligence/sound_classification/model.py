"""Typed sound classification through spectral memory and TNE collapse."""

from __future__ import annotations

import math

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.shared.capability_fixtures import SOUND_LABELS, SOUND_PROTOTYPE_FREQUENCIES
from the_nothingness_effect.artificial_intelligence.shared.capability_runtime import ClassificationOutput, TNEPrototypeClassifier
from the_nothingness_effect.artificial_intelligence.shared.types import AIObstructionError, require_finite_tensor


class SoundClassifier(nn.Module):
    """Classify finite waveforms by dominant spectral prototypes."""

    def __init__(self, *, sample_rate: int = 8000, amplitude: float = 0.6, K_D: float = 1.0) -> None:
        super().__init__()
        if sample_rate <= 2 * float(SOUND_PROTOTYPE_FREQUENCIES.max()) or not math.isfinite(amplitude) or amplitude <= 0:
            raise AIObstructionError("sound classifier requires a valid Nyquist rate and positive amplitude")
        self.sample_rate = int(sample_rate)
        self.amplitude = float(amplitude)
        nyquist = self.sample_rate / 2.0
        normalized = SOUND_PROTOTYPE_FREQUENCIES / nyquist
        prototypes = torch.stack((normalized, normalized, torch.full_like(normalized, amplitude / math.sqrt(2.0))), dim=-1)
        self.core = TNEPrototypeClassifier(prototypes, SOUND_LABELS, K_D=K_D, temperature=0.025)

    def extract_features(self, waveforms: torch.Tensor) -> torch.Tensor:
        waveforms = torch.as_tensor(waveforms, dtype=torch.float32)
        require_finite_tensor(waveforms, "sound waveforms")
        if waveforms.ndim != 2 or waveforms.shape[1] < 128:
            raise AIObstructionError("sound classification requires [batch, samples] with at least 128 samples")
        if bool((waveforms.abs() > 1.0 + 1e-6).any()):
            raise AIObstructionError("sound waveform amplitudes must lie in [-1, 1]")
        spectrum = torch.abs(torch.fft.rfft(waveforms, dim=-1, norm="ortho"))
        frequencies = torch.fft.rfftfreq(waveforms.shape[1], d=1.0 / self.sample_rate).to(waveforms.device)
        non_dc = spectrum[:, 1:]
        dominant_index = torch.argmax(non_dc, dim=-1) + 1
        dominant = frequencies[dominant_index]
        weight = spectrum.sum(dim=-1)
        if bool((weight == 0).any()):
            raise AIObstructionError("silent waveforms obstruct sound classification")
        # Dominant frequency is duplicated into the signed/dual observation
        # channels. Broadband centroid is retained as a diagnostic by callers,
        # but is deliberately not allowed to overrule the tonal source law.
        rms = torch.sqrt(torch.mean(waveforms.square(), dim=-1))
        nyquist = self.sample_rate / 2.0
        normalized_dominant = dominant / nyquist
        return require_finite_tensor(torch.stack((normalized_dominant, normalized_dominant, rms), dim=-1), "sound features")

    def forward(self, waveforms: torch.Tensor, *, tolerance: float = 1e-6) -> ClassificationOutput:
        return self.core(self.extract_features(waveforms), tolerance=tolerance)

    def decode(self, class_indices: torch.Tensor, *, sample_count: int = 2048) -> torch.Tensor:
        if sample_count < 128:
            raise AIObstructionError("decoded sound requires at least 128 samples")
        indices = torch.as_tensor(class_indices, dtype=torch.long)
        frequencies = SOUND_PROTOTYPE_FREQUENCIES[indices]
        time = torch.arange(sample_count, dtype=torch.float32) / float(self.sample_rate)
        return self.amplitude * torch.sin(2.0 * torch.pi * frequencies[:, None] * time[None, :])

    def dominant_frequencies(self, waveforms: torch.Tensor) -> torch.Tensor:
        return self.extract_features(waveforms)[:, 0] * (self.sample_rate / 2.0)
