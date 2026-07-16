"""Typed evaluation and source-removal diagnostics for multimodal TNE models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch
from torch.nn import functional

from the_nothingness_effect.artificial_intelligence.pgqenn.model import PGQENNModel

from .data import MultimodalBatch
from .model import TNETrainableMultimodalModel, TNETrainableMultimodalOutput


@dataclass(frozen=True)
class MultimodalEvaluation:
    metrics: dict[str, float]
    confusion_matrix: torch.Tensor
    residuals: dict[str, float]
    modality_similarity: torch.Tensor
    reconstruction_rmse: dict[str, float]
    output: TNETrainableMultimodalOutput


def _confusion(labels: torch.Tensor, predictions: torch.Tensor, classes: int) -> torch.Tensor:
    encoded = labels * classes + predictions
    return torch.bincount(encoded, minlength=classes * classes).reshape(classes, classes)


def _expected_calibration_error(
    probabilities: torch.Tensor,
    labels: torch.Tensor,
    bins: int = 5,
) -> float:
    confidence, predictions = probabilities.max(dim=-1)
    total = max(1, labels.numel())
    error = torch.zeros((), dtype=probabilities.dtype)
    edges = torch.linspace(0.0, 1.0, bins + 1)
    for lower, upper in zip(edges[:-1], edges[1:], strict=True):
        mask = (confidence > lower) & (confidence <= upper)
        if bool(mask.any()):
            accuracy = (predictions[mask] == labels[mask]).float().mean()
            error = error + mask.float().sum() / total * torch.abs(
                accuracy - confidence[mask].mean()
            )
    return float(error)


def evaluate_multimodal_model(
    model: TNETrainableMultimodalModel,
    batch: MultimodalBatch,
) -> MultimodalEvaluation:
    batch.validate()
    model.eval()
    with torch.no_grad():
        output = model(batch.modalities)
    probabilities = output.observation
    predictions = probabilities.argmax(dim=-1)
    classes = output.readout.shape[-1]
    targets = output.backbone_output.modality_tokens
    reconstruction = output.reconstructed_fused_tokens
    reconstruction_rmse = {
        name: float(
            torch.sqrt(torch.mean((reconstruction - targets[:, index, :]) ** 2))
        )
        for index, name in enumerate(output.backbone_output.modality_names)
    }
    modality_means = targets.mean(dim=0)
    normalized = functional.normalize(modality_means, dim=-1)
    similarity = normalized @ normalized.T
    one_hot = functional.one_hot(batch.labels, num_classes=classes).to(probabilities.dtype)
    metrics = {
        "accuracy": float((predictions == batch.labels).float().mean()),
        "cross_entropy": float(functional.cross_entropy(output.readout, batch.labels)),
        "brier_score": float(torch.mean((probabilities - one_hot) ** 2)),
        "mean_confidence": float(probabilities.max(dim=-1).values.mean()),
        "predictive_entropy": float(
            torch.mean(-torch.sum(probabilities * torch.log(probabilities.clamp_min(1e-9)), dim=-1))
        ),
        "expected_calibration_error": _expected_calibration_error(probabilities, batch.labels),
        "mean_reconstruction_rmse": sum(reconstruction_rmse.values()) / len(reconstruction_rmse),
        "mean_local_rbm_free_energy": float(output.local_rbm_state.free_energy.mean()),
        "mean_global_rbm_free_energy": float(output.global_rbm_state.free_energy.mean()),
        "local_rbm_reconstruction_rmse": float(
            output.local_rbm_state.reconstruction_residual
        ),
        "global_rbm_reconstruction_rmse": float(
            output.global_rbm_state.reconstruction_residual
        ),
        "active_clusters": float(output.cluster_state.active_clusters),
    }
    return MultimodalEvaluation(
        metrics,
        _confusion(batch.labels, predictions, classes),
        {name: float(value.detach().cpu()) for name, value in output.residuals.items()},
        similarity,
        reconstruction_rmse,
        output,
    )


def evaluate_source_removals(
    model: TNETrainableMultimodalModel,
    batch: MultimodalBatch,
) -> list[dict[str, Any]]:
    """Evaluate named ablations without redefining the canonical implementation."""

    rows: list[dict[str, Any]] = []
    raw_observer = model.backbone.raw_observer
    elastic_dubler = model.backbone.elastic_dubler
    axis_enabled = model.axis_network_enabled
    energy_enabled = model.energy_regulation_enabled
    cluster_enabled = model.cluster_context_enabled
    pgqenn_models = tuple(
        module for module in model.modules() if isinstance(module, PGQENNModel)
    )
    signed_states = tuple(module.signed_spectrum_enabled for module in pgqenn_models)
    variants = (
        ("complete", raw_observer, elastic_dubler, True, True, True, True),
        ("observation_removed", None, elastic_dubler, True, True, True, True),
        ("elastic_dubler_removed", raw_observer, None, True, True, True, True),
        ("modality_axes_removed", raw_observer, elastic_dubler, False, True, True, True),
        ("rbm_regulator_removed", raw_observer, elastic_dubler, True, False, True, True),
        ("cluster_context_removed", raw_observer, elastic_dubler, True, True, False, True),
        ("signed_spectrum_removed", raw_observer, elastic_dubler, True, True, True, False),
        ("observation_and_dubler_removed", None, None, True, True, True, True),
    )
    try:
        for name, observer, dubler, axes, energy, clusters, signed in variants:
            model.backbone.raw_observer = observer
            model.backbone.elastic_dubler = dubler
            model.axis_network_enabled = axes
            model.energy_regulation_enabled = energy
            model.cluster_context_enabled = clusters
            for pgqenn in pgqenn_models:
                pgqenn.signed_spectrum_enabled = signed
            evaluation = evaluate_multimodal_model(model, batch)
            rows.append({"variant": name, **evaluation.metrics})
    finally:
        model.backbone.raw_observer = raw_observer
        model.backbone.elastic_dubler = elastic_dubler
        model.axis_network_enabled = axis_enabled
        model.energy_regulation_enabled = energy_enabled
        model.cluster_context_enabled = cluster_enabled
        for pgqenn, signed in zip(pgqenn_models, signed_states, strict=True):
            pgqenn.signed_spectrum_enabled = signed
    return rows
