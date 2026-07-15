"""Deterministic visual and auditory fixtures for TNE AI capability evidence."""

from __future__ import annotations

import math

import torch


COLOR_LABELS = ("red", "green", "blue", "cyan", "magenta", "yellow")
COLOR_PROTOTYPES = torch.tensor(
    (
        (0.90, 0.10, 0.10),
        (0.10, 0.90, 0.10),
        (0.10, 0.10, 0.90),
        (0.10, 0.85, 0.85),
        (0.85, 0.10, 0.85),
        (0.85, 0.85, 0.10),
    ),
    dtype=torch.float32,
)
SOUND_LABELS = ("low_250_hz", "middle_500_hz", "high_1000_hz")
SOUND_PROTOTYPE_FREQUENCIES = torch.tensor((250.0, 500.0, 1000.0), dtype=torch.float32)


def color_images(
    *,
    seed: int = 0,
    samples_per_class: int = 4,
    image_size: int = 12,
) -> tuple[torch.Tensor, torch.Tensor]:
    if samples_per_class < 1 or image_size < 2:
        raise ValueError("color fixture dimensions must be positive")
    generator = torch.Generator().manual_seed(seed)
    images: list[torch.Tensor] = []
    targets: list[int] = []
    for index, prototype in enumerate(COLOR_PROTOTYPES):
        for _ in range(samples_per_class):
            noise = 0.035 * torch.randn((image_size, image_size, 3), generator=generator)
            images.append(torch.clamp(prototype + noise, 0.0, 1.0))
            targets.append(index)
    return torch.stack(images), torch.tensor(targets, dtype=torch.long)


def color_clone_image(*, image_size: int = 32) -> torch.Tensor:
    if image_size < 4:
        raise ValueError("color clone fixture requires at least four pixels per axis")
    axis = torch.linspace(0.0, 1.0, image_size)
    x, y = torch.meshgrid(axis, axis, indexing="ij")
    return torch.stack((x, y, 0.5 + 0.35 * torch.sin(2.0 * torch.pi * x) * torch.cos(2.0 * torch.pi * y)), dim=-1)


def tone_batch(
    *,
    seed: int = 0,
    samples_per_class: int = 4,
    sample_rate: int = 8000,
    sample_count: int = 2048,
) -> tuple[torch.Tensor, torch.Tensor]:
    if samples_per_class < 1 or sample_rate <= 2000 or sample_count < 128:
        raise ValueError("tone fixture requires a valid sample rate and finite sample window")
    generator = torch.Generator().manual_seed(seed)
    time = torch.arange(sample_count, dtype=torch.float32) / float(sample_rate)
    waveforms: list[torch.Tensor] = []
    targets: list[int] = []
    for index, frequency in enumerate(SOUND_PROTOTYPE_FREQUENCIES):
        for _ in range(samples_per_class):
            jitter = float(torch.randn((), generator=generator)) * 4.0
            phase = float(torch.rand((), generator=generator)) * 2.0 * math.pi
            waveform = 0.6 * torch.sin(2.0 * torch.pi * (frequency + jitter) * time + phase)
            waveform += 0.01 * torch.randn(sample_count, generator=generator)
            waveforms.append(waveform)
            targets.append(index)
    return torch.stack(waveforms), torch.tensor(targets, dtype=torch.long)


def sound_clone_waveform(*, sample_rate: int = 8000, sample_count: int = 2048) -> torch.Tensor:
    time = torch.arange(sample_count, dtype=torch.float32) / float(sample_rate)
    envelope = torch.exp(-2.2 * time)
    return envelope * (
        0.55 * torch.sin(2.0 * torch.pi * 330.0 * time)
        + 0.25 * torch.sin(2.0 * torch.pi * 660.0 * time + 0.3)
    )
