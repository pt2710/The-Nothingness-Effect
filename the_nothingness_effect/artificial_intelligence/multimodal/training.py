"""Deterministic CPU training loop with visible TNE residual components."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch.nn import functional

from .data import MultimodalBatch
from .evaluation import evaluate_multimodal_model
from .model import TNETrainableMultimodalModel, TNETrainableMultimodalOutput


@dataclass(frozen=True)
class MultimodalEpoch:
    epoch: int
    train_total_loss: float
    train_task_loss: float
    train_reconstruction_loss: float
    train_closure_penalty: float
    train_accuracy: float
    validation_loss: float
    validation_accuracy: float
    gradient_norm: float
    modality_weights: tuple[float, ...]
    confusion_matrix: tuple[tuple[int, ...], ...]
    latent_snapshot: tuple[tuple[float, ...], ...]


@dataclass(frozen=True)
class MultimodalTrainingRun:
    history: tuple[MultimodalEpoch, ...]
    seed: int
    epochs: int
    learning_rate: float


def _loss_components(
    output: TNETrainableMultimodalOutput,
    labels: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    task = functional.cross_entropy(output.readout, labels)
    target = output.backbone_output.modality_tokens.mean(dim=1)
    reconstruction = functional.mse_loss(output.reconstructed_fused_tokens, target)
    residual_vector = torch.stack(
        [torch.tanh(torch.abs(value)) for value in output.residuals.values()]
    )
    closure = residual_vector.mean()
    total = task + 0.25 * reconstruction + 0.02 * closure
    return total, task, reconstruction, closure


def train_multimodal_model(
    model: TNETrainableMultimodalModel,
    train_batch: MultimodalBatch,
    validation_batch: MultimodalBatch,
    *,
    epochs: int = 8,
    learning_rate: float = 0.015,
    seed: int = 0,
) -> MultimodalTrainingRun:
    if epochs < 1 or learning_rate <= 0:
        raise ValueError("epochs and learning rate must be positive")
    train_batch.validate()
    validation_batch.validate()
    torch.manual_seed(seed)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    history: list[MultimodalEpoch] = []
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        output = model(train_batch.modalities)
        total, task, reconstruction, closure = _loss_components(output, train_batch.labels)
        total.backward()
        gradient_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
        optimizer.step()
        predictions = output.readout.argmax(dim=-1)
        train_accuracy = (predictions == train_batch.labels).float().mean()
        validation = evaluate_multimodal_model(model, validation_batch)
        weights = output.backbone_output.modality_weights.mean(dim=0)
        history.append(
            MultimodalEpoch(
                epoch=epoch,
                train_total_loss=float(total.detach()),
                train_task_loss=float(task.detach()),
                train_reconstruction_loss=float(reconstruction.detach()),
                train_closure_penalty=float(closure.detach()),
                train_accuracy=float(train_accuracy.detach()),
                validation_loss=validation.metrics["cross_entropy"],
                validation_accuracy=validation.metrics["accuracy"],
                gradient_norm=float(gradient_norm.detach()),
                modality_weights=tuple(float(item) for item in weights.detach()),
                confusion_matrix=tuple(
                    tuple(int(value) for value in row)
                    for row in validation.confusion_matrix.tolist()
                ),
                latent_snapshot=tuple(
                    tuple(float(value) for value in row)
                    for row in output.hidden.detach().cpu().tolist()
                ),
            )
        )
    return MultimodalTrainingRun(tuple(history), seed, epochs, learning_rate)
