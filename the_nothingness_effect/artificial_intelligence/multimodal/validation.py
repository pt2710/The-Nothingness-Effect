"""Validation boundary for the trainable multimodal model."""

from __future__ import annotations

from .data import MultimodalBatch
from .evaluation import MultimodalEvaluation, evaluate_multimodal_model
from .model import TNETrainableMultimodalModel


def validate_multimodal_model(
    model: TNETrainableMultimodalModel,
    validation_batch: MultimodalBatch,
) -> MultimodalEvaluation:
    return evaluate_multimodal_model(model, validation_batch)
