"""Architecture-coupled SOInet task evaluation.

Unlike the deterministic prototype capability fixtures, every metric in this
module is computed from ``SOInetModel`` readouts and therefore changes when the
QENN, PGQENN, transfer, meta-readout, or observation parameters change.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as functional

from .model import SOInetModel, SOInetOutput


@dataclass(frozen=True)
class SOInetClassificationEvaluation:
    logits: torch.Tensor
    probabilities: torch.Tensor
    predictions: torch.Tensor
    targets: torch.Tensor
    loss: torch.Tensor
    accuracy: torch.Tensor
    mean_confidence: torch.Tensor
    closure_statuses: tuple[str, ...]


def forward_classification_batch(
    model: SOInetModel,
    qenn_batch: torch.Tensor,
    pgqenn_batch: torch.Tensor,
    *,
    tolerance: float = 1e-5,
) -> tuple[torch.Tensor, torch.Tensor, tuple[SOInetOutput, ...]]:
    """Run one SOInet graph pair per task sample.

    Inputs are ``[sample, node, feature]``. Node counts may differ between the
    QENN and PGQENN modalities, but sample count and feature width must align.
    """

    if qenn_batch.ndim != 3 or pgqenn_batch.ndim != 3:
        raise ValueError("SOInet task evaluation requires rank-three batched graph features")
    if qenn_batch.shape[0] != pgqenn_batch.shape[0]:
        raise ValueError("SOInet task modalities must contain the same number of samples")
    if qenn_batch.shape[-1] != pgqenn_batch.shape[-1]:
        raise ValueError("SOInet task modalities must use the same feature width")
    if qenn_batch.shape[0] < 1:
        raise ValueError("SOInet task evaluation requires at least one sample")

    outputs = tuple(
        model(qenn_features, pgqenn_features, tolerance=tolerance)
        for qenn_features, pgqenn_features in zip(qenn_batch, pgqenn_batch, strict=True)
    )
    logits = torch.stack([output.readout.squeeze(0) for output in outputs])
    probabilities = torch.stack([output.observation.squeeze(0) for output in outputs])
    return logits, probabilities, outputs


def classification_evaluation_from_outputs(
    logits: torch.Tensor,
    probabilities: torch.Tensor,
    outputs: tuple[SOInetOutput, ...],
    targets: torch.Tensor,
) -> SOInetClassificationEvaluation:
    targets = torch.as_tensor(targets, dtype=torch.long, device=logits.device)
    if targets.ndim != 1 or targets.shape[0] != logits.shape[0]:
        raise ValueError("SOInet task targets must have shape [sample]")
    if bool((targets < 0).any()) or bool((targets >= logits.shape[-1]).any()):
        raise ValueError("SOInet task targets lie outside the model output codomain")
    loss = functional.cross_entropy(logits, targets)
    predictions = torch.argmax(probabilities, dim=-1)
    confidence = torch.max(probabilities, dim=-1).values
    accuracy = (predictions == targets).to(dtype=logits.dtype).mean()
    return SOInetClassificationEvaluation(
        logits=logits,
        probabilities=probabilities,
        predictions=predictions,
        targets=targets,
        loss=loss,
        accuracy=accuracy,
        mean_confidence=confidence.mean(),
        closure_statuses=tuple(output.closure_status.value for output in outputs),
    )


def evaluate_classification(
    model: SOInetModel,
    qenn_batch: torch.Tensor,
    pgqenn_batch: torch.Tensor,
    targets: torch.Tensor,
    *,
    tolerance: float = 1e-5,
) -> SOInetClassificationEvaluation:
    """Evaluate a task without disconnecting its metrics from SOInet."""

    was_training = model.training
    model.eval()
    try:
        with torch.no_grad():
            logits, probabilities, outputs = forward_classification_batch(
                model, qenn_batch, pgqenn_batch, tolerance=tolerance
            )
            return classification_evaluation_from_outputs(
                logits, probabilities, outputs, targets
            )
    finally:
        model.train(was_training)
