"""Deterministic paired color, sound and vision fixtures for multimodal QA."""

from __future__ import annotations

from dataclasses import dataclass

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
            raise AIObstructionError("a multimodal batch requires at least two modalities")
        size = int(self.labels.shape[0])
        if self.labels.ndim != 1 or size < 2:
            raise AIObstructionError("multimodal labels must be a non-empty vector")
        for name, value in self.modalities.items():
            require_finite_tensor(value, f"multimodal dataset {name}")
            if value.shape[0] != size:
                raise AIObstructionError("all modalities and labels require equal sample counts")
        return self

    def select(self, indices: torch.Tensor) -> "MultimodalBatch":
        return MultimodalBatch(
            {name: value[indices] for name, value in self.modalities.items()},
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


def make_synthetic_multimodal_dataset(
    *,
    samples_per_class: int = 10,
    seed: int = 0,
) -> MultimodalDataset:
    """Create aligned finite fixtures; these are not empirical observations."""

    if samples_per_class < 5:
        raise AIObstructionError("at least five samples per class are required")
    generator = torch.Generator().manual_seed(seed)
    class_names = ("red-low", "green-mid", "blue-high", "amber-pulse")
    colors = torch.tensor(
        [[1.0, 0.08, 0.05], [0.08, 1.0, 0.08], [0.05, 0.1, 1.0], [1.0, 0.55, 0.05]]
    )
    time = torch.linspace(0.0, 1.0, 64)
    modality_rows = {"color": [], "sound": [], "vision": []}
    labels: list[int] = []
    for class_index in range(len(class_names)):
        for sample_index in range(samples_per_class):
            noise_scale = 0.015 + 0.002 * (sample_index % 3)
            color = colors[class_index] + noise_scale * torch.randn(3, generator=generator)
            frequency = float(3 + 2 * class_index)
            phase = 0.08 * sample_index
            sound = torch.sin(2.0 * torch.pi * frequency * time + phase)
            sound = sound + noise_scale * torch.randn(64, generator=generator)
            vision = _vision_pattern(class_index)
            vision = vision + noise_scale * torch.randn((8, 8), generator=generator)
            modality_rows["color"].append(color.clamp_min(0.0))
            modality_rows["sound"].append(sound.unsqueeze(0))
            modality_rows["vision"].append(vision.clamp_min(0.0).unsqueeze(0))
            labels.append(class_index)
    modalities = {name: torch.stack(rows) for name, rows in modality_rows.items()}
    label_tensor = torch.tensor(labels, dtype=torch.long)
    train_indices: list[int] = []
    validation_indices: list[int] = []
    test_indices: list[int] = []
    train_count = max(2, int(samples_per_class * 0.6))
    validation_count = max(1, int(samples_per_class * 0.2))
    for class_index in range(len(class_names)):
        start = class_index * samples_per_class
        indices = list(range(start, start + samples_per_class))
        train_indices.extend(indices[:train_count])
        validation_indices.extend(indices[train_count : train_count + validation_count])
        test_indices.extend(indices[train_count + validation_count :])
    complete = MultimodalBatch(modalities, label_tensor).validate()
    return MultimodalDataset(
        complete.select(torch.tensor(train_indices)),
        complete.select(torch.tensor(validation_indices)),
        complete.select(torch.tensor(test_indices)),
        class_names,
    )
