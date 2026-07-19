"""Deterministic CPU training loop with visible TNE residual components."""

from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch.nn import functional

from the_nothingness_effect.artificial_intelligence.shared.dynamic_kd import (
    dynamic_kd_state,
)
from the_nothingness_effect.artificial_intelligence.shared.dynamic_soi import (
    dynamic_soi_state,
)

from .data import MultimodalBatch
from .evaluation import evaluate_multimodal_model
from .model import TNETrainableMultimodalModel, TNETrainableMultimodalOutput
from .optimization import (
    DynamicKDSearch,
    KDProbe,
    KDSelection,
    validation_objective,
)


@dataclass(frozen=True)
class MultimodalEpoch:
    epoch: int
    train_total_loss: float
    train_task_loss: float
    train_reconstruction_loss: float
    train_energy_loss: float
    train_closure_penalty: float
    train_accuracy: float
    validation_loss: float
    validation_accuracy: float
    gradient_norm: float
    modality_weights: tuple[float, ...]
    confusion_matrix: tuple[tuple[int, ...], ...]
    latent_snapshot: tuple[tuple[float, ...], ...]
    axis_snapshot: tuple[tuple[float, ...], ...]
    local_free_energy: float
    global_free_energy: float
    cluster_count: int
    growth_event_count: int
    cluster_centroids: tuple[tuple[float, ...], ...]
    K_D: float
    soi_scale: float
    learning_rate: float
    validation_objective: float
    K_D_selection_improvement: float
    joint_hyperparameter_improvement: float


@dataclass(frozen=True)
class MultimodalTrainingRun:
    history: tuple[MultimodalEpoch, ...]
    seed: int
    epochs: int
    learning_rate: float
    kd_probes: tuple[KDProbe, ...] = ()
    kd_selections: tuple[KDSelection, ...] = ()
    best_epoch: int = -1
    best_validation_objective: float = math.inf
    restored_best_checkpoint: bool = False

    @property
    def hyperparameter_probes(self) -> tuple[KDProbe, ...]:
        return self.kd_probes

    @property
    def hyperparameter_selections(self) -> tuple[KDSelection, ...]:
        return self.kd_selections


def _loss_components(
    output: TNETrainableMultimodalOutput,
    labels: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    task = functional.cross_entropy(output.readout, labels)
    target = output.backbone_output.modality_tokens.mean(dim=1)
    reconstruction = functional.mse_loss(
        output.reconstructed_fused_tokens,
        target,
    )
    if output.local_rbm_state is None or output.global_rbm_state is None:
        raise RuntimeError("multimodal energy states are required during training")
    energy = (
        torch.abs(output.local_rbm_state.contrastive_divergence)
        + torch.abs(output.global_rbm_state.contrastive_divergence)
        + output.local_rbm_state.reconstruction_residual
        + output.global_rbm_state.reconstruction_residual
    )
    residual_vector = torch.stack(
        [torch.tanh(torch.abs(value)) for value in output.residuals.values()]
    )
    closure = residual_vector.mean()
    total = task + 0.25 * reconstruction + 0.03 * energy + 0.02 * closure
    return total, task, reconstruction, energy, closure


def _clone_state_dict(
    model: TNETrainableMultimodalModel,
) -> dict[str, torch.Tensor]:
    return {
        name: value.detach().cpu().clone()
        for name, value in model.state_dict().items()
    }


def train_multimodal_model(
    model: TNETrainableMultimodalModel,
    train_batch: MultimodalBatch,
    validation_batch: MultimodalBatch,
    *,
    epochs: int = 8,
    learning_rate: float = 0.015,
    seed: int = 0,
    optimize_K_D: bool = False,
    adaptive_learning_rate: bool = False,
    kd_search: DynamicKDSearch | None = None,
) -> MultimodalTrainingRun:
    if epochs < 1 or learning_rate <= 0:
        raise ValueError("epochs and learning rate must be positive")
    train_batch.validate()
    validation_batch.validate()
    torch.manual_seed(seed)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = (
        torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode="min",
            factor=0.7,
            patience=2,
            min_lr=learning_rate * 0.08,
        )
        if adaptive_learning_rate
        else None
    )
    search = kd_search or (DynamicKDSearch() if optimize_K_D else None)
    history: list[MultimodalEpoch] = []
    best_state: dict[str, torch.Tensor] | None = None
    best_epoch = -1
    best_objective = math.inf
    for epoch in range(epochs):
        selection = (
            search.select(model, validation_batch, epoch=epoch)
            if search is not None
            else None
        )
        model.train()
        optimizer.zero_grad(set_to_none=True)
        output = model(train_batch.modalities)
        total, task, reconstruction, energy, closure = _loss_components(
            output,
            train_batch.labels,
        )
        total.backward()
        gradient_norm = torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            5.0,
        )
        optimizer.step()
        predictions = output.readout.argmax(dim=-1)
        train_accuracy = (
            predictions == train_batch.labels
        ).float().mean()
        validation = evaluate_multimodal_model(
            model,
            validation_batch,
        )
        objective = validation_objective(validation)
        if not math.isfinite(objective):
            raise RuntimeError("validation objective became non-finite")
        current_learning_rate = float(optimizer.param_groups[0]["lr"])
        if scheduler is not None:
            scheduler.step(objective)
        if objective < best_objective:
            best_objective = float(objective)
            best_epoch = epoch
            best_state = _clone_state_dict(model)
        weights = output.backbone_output.modality_weights.mean(dim=0)
        history.append(
            MultimodalEpoch(
                epoch=epoch,
                train_total_loss=float(total.detach()),
                train_task_loss=float(task.detach()),
                train_reconstruction_loss=float(reconstruction.detach()),
                train_energy_loss=float(energy.detach()),
                train_closure_penalty=float(closure.detach()),
                train_accuracy=float(train_accuracy.detach()),
                validation_loss=validation.metrics["cross_entropy"],
                validation_accuracy=validation.metrics["accuracy"],
                gradient_norm=float(gradient_norm.detach()),
                modality_weights=tuple(
                    float(item) for item in weights.detach()
                ),
                confusion_matrix=tuple(
                    tuple(int(value) for value in row)
                    for row in validation.confusion_matrix.tolist()
                ),
                latent_snapshot=tuple(
                    tuple(float(value) for value in row)
                    for row in output.hidden.detach().cpu().tolist()
                ),
                axis_snapshot=tuple(
                    tuple(float(value) for value in row)
                    for row in output.axis_state.mapped_axes.detach()
                    .reshape(output.hidden.shape[0], -1)
                    .cpu()
                    .tolist()
                ),
                local_free_energy=float(
                    output.local_rbm_state.free_energy.mean().detach()
                ),
                global_free_energy=float(
                    output.global_rbm_state.free_energy.mean().detach()
                ),
                cluster_count=output.cluster_state.active_clusters,
                growth_event_count=len(output.cluster_state.events),
                cluster_centroids=tuple(
                    tuple(float(value) for value in row)
                    for row in output.cluster_state.centroids.detach()
                    .cpu()
                    .tolist()
                ),
                K_D=dynamic_kd_state(model).value,
                soi_scale=dynamic_soi_state(model).value,
                learning_rate=current_learning_rate,
                validation_objective=objective,
                K_D_selection_improvement=(
                    selection.improvement
                    if selection is not None
                    else 0.0
                ),
                joint_hyperparameter_improvement=(
                    selection.improvement
                    if selection is not None
                    else 0.0
                ),
            )
        )
    if best_state is None or best_epoch < 0:
        raise RuntimeError("training did not produce a valid checkpoint")
    model.load_state_dict(best_state)
    return MultimodalTrainingRun(
        history=tuple(history),
        seed=seed,
        epochs=epochs,
        learning_rate=learning_rate,
        kd_probes=search.probes if search is not None else (),
        kd_selections=search.selections if search is not None else (),
        best_epoch=best_epoch,
        best_validation_objective=best_objective,
        restored_best_checkpoint=True,
    )
