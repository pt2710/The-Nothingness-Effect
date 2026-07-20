"""Deterministic multimodal fixtures with controlled intra-class variance."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch

from the_nothingness_effect.artificial_intelligence.shared.types import (
    AIObstructionError,
    require_finite_tensor,
)


@dataclass(frozen=True)
class MultimodalBatch:
    modalities: dict[str, torch.Tensor]
    labels: torch.Tensor

    def validate(self) -> "MultimodalBatch":
        if len(self.modalities) < 2:
            raise AIObstructionError(
                "a multimodal batch requires at least two modalities"
            )
        size = int(self.labels.shape[0])
        if self.labels.ndim != 1 or size < 2:
            raise AIObstructionError(
                "multimodal labels must contain at least two samples"
            )
        for name, value in self.modalities.items():
            require_finite_tensor(value, f"multimodal dataset {name}")
            if value.shape[0] != size:
                raise AIObstructionError(
                    "all modalities and labels require equal sample counts"
                )
        return self

    def select(self, indices: torch.Tensor) -> "MultimodalBatch":
        return MultimodalBatch(
            {
                name: value[indices]
                for name, value in self.modalities.items()
            },
            self.labels[indices],
        ).validate()


@dataclass(frozen=True)
class MultimodalDataset:
    train: MultimodalBatch
    validation: MultimodalBatch
    test: MultimodalBatch
    class_names: tuple[str, ...]


def _vision_pattern(class_index: int) -> torch.Tensor:
    image = torch.zeros(8, 8)
    if class_index == 0:
        image[:, 2:4] = 1.0
    elif class_index == 1:
        image[4:6, :] = 1.0
    elif class_index == 2:
        image[torch.arange(8), torch.arange(8)] = 1.0
    else:
        image[1:7, 1] = 1.0
        image[1:7, 6] = 1.0
        image[1, 1:7] = 1.0
        image[6, 1:7] = 1.0
    return image


def _text_pattern(
    class_index: int,
    sample_index: int,
    generator: torch.Generator,
) -> torch.Tensor:
    length = 48
    position = torch.linspace(0.0, 1.0, length)
    centres = (0.16, 0.38, 0.62, 0.84)
    widths = (0.055, 0.075, 0.065, 0.085)
    centre = centres[class_index] + 0.012 * (
        (sample_index % 5) - 2
    )
    lexical = torch.exp(
        -0.5 * ((position - centre) / widths[class_index]) ** 2
    )
    syntax = 0.20 * (
        1.0
        + torch.sin(
            2.0
            * torch.pi
            * (class_index + 1)
            * position
            + 0.11 * sample_index
        )
    )
    noise = 0.012 * torch.randn(length, generator=generator)
    return (lexical + syntax + noise).clamp(0.0, 1.5).unsqueeze(0)


def _state_pattern(
    class_index: int,
    sample_index: int,
    generator: torch.Generator,
) -> torch.Tensor:
    phase = 0.19 * sample_index
    base = torch.tensor(
        [
            0.22 + 0.17 * class_index,
            0.86 - 0.12 * class_index,
            0.18 + 0.09 * class_index,
            0.25 + 0.11 * (class_index % 2),
            0.35 + 0.08 * ((class_index + 1) % 3),
            0.50 + 0.07 * class_index,
            0.30 + 0.05 * class_index,
            0.16 + 0.10 * (3 - class_index),
        ],
        dtype=torch.float32,
    )
    oscillation = 0.045 * torch.tensor(
        [
            torch.sin(torch.tensor(phase)),
            torch.cos(torch.tensor(phase)),
            torch.sin(torch.tensor(2.0 * phase)),
            torch.cos(torch.tensor(2.0 * phase)),
            torch.sin(torch.tensor(0.5 * phase)),
            torch.cos(torch.tensor(0.5 * phase)),
            torch.sin(torch.tensor(1.5 * phase)),
            torch.cos(torch.tensor(1.5 * phase)),
        ]
    )
    noise = 0.01 * torch.randn(8, generator=generator)
    return (base + oscillation + noise).clamp_min(0.0)


def _variation_summary(
    batch: MultimodalBatch,
    split: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, values in sorted(batch.modalities.items()):
        flattened = values.reshape(values.shape[0], -1).to(torch.float64)
        sample_means = flattened.mean(dim=-1)
        centred = flattened - flattened.mean(dim=0, keepdim=True)
        feature_variance = torch.mean(centred * centred, dim=0)
        pairwise = (
            torch.pdist(flattened)
            if flattened.shape[0] > 1
            else torch.zeros(1, dtype=flattened.dtype)
        )
        rows.append(
            {
                "split": split,
                "modality": name,
                "sample_count": int(flattened.shape[0]),
                "feature_count": int(flattened.shape[1]),
                "mean_feature_variance": float(feature_variance.mean()),
                "maximum_feature_variance": float(feature_variance.max()),
                "sample_mean_variance": float(
                    torch.var(sample_means, unbiased=False)
                ),
                "mean_pairwise_distance": float(pairwise.mean()),
                "minimum_pairwise_distance": float(pairwise.min()),
                "maximum_pairwise_distance": float(pairwise.max()),
            }
        )
    return rows


def dataset_variation_summary(
    dataset: MultimodalDataset,
) -> list[dict[str, Any]]:
    """Return finite evidence that every split contains varied observations."""

    rows: list[dict[str, Any]] = []
    for split in ("train", "validation", "test"):
        rows.extend(_variation_summary(getattr(dataset, split), split))
    return rows


def make_synthetic_multimodal_dataset(
    *,
    samples_per_class: int = 10,
    seed: int = 0,
    include_extended_modalities: bool = False,
) -> MultimodalDataset:
    """Create aligned finite fixtures; these are not empirical observations.

    Every class contains multiple observations with independent brightness,
    phase, frequency, translation, contrast, lexical and state variation.
    The optional extended mode adds explicit text and state carriers while
    preserving the historical color/sound/vision fixture API by default.
    """

    if samples_per_class < 5:
        raise AIObstructionError(
            "at least five samples per class are required"
        )
    generator = torch.Generator().manual_seed(seed)
    class_names = (
        "red-low",
        "green-mid",
        "blue-high",
        "amber-pulse",
    )
    colors = torch.tensor(
        [
            [1.0, 0.08, 0.05],
            [0.08, 1.0, 0.08],
            [0.05, 0.1, 1.0],
            [1.0, 0.55, 0.05],
        ]
    )
    time = torch.linspace(0.0, 1.0, 96)
    modality_rows: dict[str, list[torch.Tensor]] = {
        "color": [],
        "sound": [],
        "vision": [],
    }
    if include_extended_modalities:
        modality_rows.update({"text": [], "state": []})
    labels: list[int] = []

    for class_index in range(len(class_names)):
        for sample_index in range(samples_per_class):
            noise_scale = 0.012 + 0.004 * (sample_index % 4)
            brightness = 0.78 + 0.05 * (sample_index % 5)
            contrast = 0.88 + 0.04 * ((sample_index + 2) % 4)
            channel_jitter = noise_scale * torch.randn(
                3,
                generator=generator,
            )
            color = (
                brightness * colors[class_index] + channel_jitter
            ).clamp(0.0, 1.25)

            frequency = (
                3.0
                + 2.0 * class_index
                + 0.08 * ((sample_index % 7) - 3)
            )
            phase = 0.13 * sample_index
            amplitude = 0.62 + 0.055 * (sample_index % 6)
            envelope = 0.72 + 0.28 * torch.sin(
                torch.pi * time
            ) ** 2
            fundamental = torch.sin(
                2.0 * torch.pi * frequency * time + phase
            )
            harmonic = 0.23 * torch.sin(
                2.0
                * torch.pi
                * (frequency * 2.0 + 0.15 * class_index)
                * time
                - 0.5 * phase
            )
            sound = amplitude * envelope * (
                fundamental + harmonic
            )
            sound = sound + noise_scale * torch.randn(
                96,
                generator=generator,
            )

            vision = _vision_pattern(class_index)
            shift_x = int((sample_index % 3) - 1)
            shift_y = int(((sample_index // 3) % 3) - 1)
            vision = torch.roll(
                vision,
                shifts=(shift_x, shift_y),
                dims=(0, 1),
            )
            if sample_index % 4 == 0:
                vision = torch.maximum(
                    vision,
                    torch.roll(vision, shifts=1, dims=0),
                )
            vision = contrast * vision
            vision = vision + noise_scale * torch.randn(
                (8, 8),
                generator=generator,
            )

            modality_rows["color"].append(color)
            modality_rows["sound"].append(sound.unsqueeze(0))
            modality_rows["vision"].append(
                vision.clamp(0.0, 1.5).unsqueeze(0)
            )
            if include_extended_modalities:
                modality_rows["text"].append(
                    _text_pattern(
                        class_index,
                        sample_index,
                        generator,
                    )
                )
                modality_rows["state"].append(
                    _state_pattern(
                        class_index,
                        sample_index,
                        generator,
                    )
                )
            labels.append(class_index)

    modalities = {
        name: torch.stack(rows)
        for name, rows in modality_rows.items()
    }
    label_tensor = torch.tensor(labels, dtype=torch.long)
    complete = MultimodalBatch(
        modalities,
        label_tensor,
    ).validate()

    train_indices: list[int] = []
    validation_indices: list[int] = []
    test_indices: list[int] = []
    train_count = max(2, int(samples_per_class * 0.6))
    validation_count = max(1, int(samples_per_class * 0.2))
    for class_index in range(len(class_names)):
        start = class_index * samples_per_class
        permutation = torch.randperm(
            samples_per_class,
            generator=generator,
        ).tolist()
        indices = [start + index for index in permutation]
        train_indices.extend(indices[:train_count])
        validation_indices.extend(
            indices[train_count : train_count + validation_count]
        )
        test_indices.extend(
            indices[train_count + validation_count :]
        )

    dataset = MultimodalDataset(
        complete.select(torch.tensor(train_indices)),
        complete.select(torch.tensor(validation_indices)),
        complete.select(torch.tensor(test_indices)),
        class_names,
    )
    for row in dataset_variation_summary(dataset):
        if int(row["sample_count"]) < 2:
            raise AIObstructionError(
                "every dataset split requires multiple data points"
            )
        if float(row["mean_pairwise_distance"]) <= 0.0:
            raise AIObstructionError(
                f"{row['split']} {row['modality']} contains no variation"
            )
    return dataset
