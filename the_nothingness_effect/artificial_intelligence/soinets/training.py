"""SOInet objectives and architecture-coupled train/validation workflow."""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as functional

from .evaluation import (
    classification_evaluation_from_outputs,
    evaluate_classification,
    forward_classification_batch,
)
from .model import SOInetModel


@dataclass(frozen=True)
class SOInetEpochRecord:
    epoch: int
    train_loss: float
    train_accuracy: float
    validation_loss: float
    validation_accuracy: float
    closure_penalty: float


def training_step(
    model: SOInetModel,
    qenn_features: torch.Tensor,
    pgqenn_features: torch.Tensor,
    target: torch.Tensor,
    *,
    closure_weight: float = 0.1,
) -> torch.Tensor:
    """Backward-compatible single graph-pair objective."""

    output = model(qenn_features, pgqenn_features)
    task = functional.cross_entropy(output.readout, target.reshape(1))
    closure = torch.stack(tuple(output.residuals.values())).sum()
    return task + float(closure_weight) * closure


def batch_training_step(
    model: SOInetModel,
    qenn_batch: torch.Tensor,
    pgqenn_batch: torch.Tensor,
    targets: torch.Tensor,
    *,
    closure_weight: float = 0.1,
    tolerance: float = 1e-5,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Return task-coupled loss, accuracy, and closure penalty for a batch."""

    logits, probabilities, outputs = forward_classification_batch(
        model, qenn_batch, pgqenn_batch, tolerance=tolerance
    )
    evaluation = classification_evaluation_from_outputs(
        logits, probabilities, outputs, targets
    )
    closure_penalty = torch.stack(
        [torch.stack(tuple(output.residuals.values())).sum() for output in outputs]
    ).mean()
    loss = evaluation.loss + float(closure_weight) * closure_penalty
    return loss, evaluation.accuracy, closure_penalty


def train_classification_epoch(
    model: SOInetModel,
    optimizer: torch.optim.Optimizer,
    qenn_batch: torch.Tensor,
    pgqenn_batch: torch.Tensor,
    targets: torch.Tensor,
    *,
    closure_weight: float = 0.1,
    tolerance: float = 1e-5,
) -> tuple[float, float, float]:
    """Run one optimizer epoch over an architecture-coupled finite batch."""

    model.train()
    optimizer.zero_grad(set_to_none=True)
    loss, accuracy, closure_penalty = batch_training_step(
        model,
        qenn_batch,
        pgqenn_batch,
        targets,
        closure_weight=closure_weight,
        tolerance=tolerance,
    )
    loss.backward()
    optimizer.step()
    return float(loss.detach()), float(accuracy.detach()), float(closure_penalty.detach())


def fit_classification(
    model: SOInetModel,
    optimizer: torch.optim.Optimizer,
    train_data: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    validation_data: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    *,
    epochs: int,
    closure_weight: float = 0.1,
    tolerance: float = 1e-5,
) -> tuple[SOInetEpochRecord, ...]:
    """Fit and validate SOInet with metrics derived from the same architecture."""

    if not isinstance(epochs, int) or epochs < 1:
        raise ValueError("SOInet fitting requires a positive epoch count")
    train_qenn, train_pgqenn, train_targets = train_data
    validation_qenn, validation_pgqenn, validation_targets = validation_data
    history: list[SOInetEpochRecord] = []
    for epoch in range(1, epochs + 1):
        train_loss, train_accuracy, closure_penalty = train_classification_epoch(
            model,
            optimizer,
            train_qenn,
            train_pgqenn,
            train_targets,
            closure_weight=closure_weight,
            tolerance=tolerance,
        )
        validation = evaluate_classification(
            model,
            validation_qenn,
            validation_pgqenn,
            validation_targets,
            tolerance=tolerance,
        )
        history.append(
            SOInetEpochRecord(
                epoch=epoch,
                train_loss=train_loss,
                train_accuracy=train_accuracy,
                validation_loss=float(validation.loss),
                validation_accuracy=float(validation.accuracy),
                closure_penalty=closure_penalty,
            )
        )
    return tuple(history)
