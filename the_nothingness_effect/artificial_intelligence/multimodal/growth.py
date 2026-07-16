"""Deterministic, bounded self-growth over modality-axis clusters."""

from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.shared.types import (
    AIObstructionError,
    require_finite_tensor,
)


@dataclass(frozen=True)
class ClusterGrowthEvent:
    step: int
    event: str
    cluster_id: int
    modality: str
    novelty: float


@dataclass(frozen=True)
class ClusterGrowthState:
    assignments: torch.Tensor
    selected_distance: torch.Tensor
    context: torch.Tensor
    centroids: torch.Tensor
    cluster_modalities: torch.Tensor
    cluster_counts: torch.Tensor
    topology_adjacency: torch.Tensor
    events: tuple[ClusterGrowthEvent, ...]
    active_clusters: int
    residuals: dict[str, torch.Tensor]


class AdaptiveModalityClusterNetwork(nn.Module):
    """Grow and update modality-specific latent prototypes.

    Growth is triggered only when a sample is farther than ``spawn_threshold``
    from every existing prototype of the same modality.  Capacity is explicit;
    reaching it routes to the nearest cluster and records a capacity residual
    rather than allocating unbounded state.
    """

    def __init__(
        self,
        axis_dim: int,
        *,
        max_clusters: int = 24,
        spawn_threshold: float = 0.55,
        learning_rate: float = 0.2,
    ) -> None:
        super().__init__()
        if axis_dim < 2 or max_clusters < 2:
            raise AIObstructionError("cluster dimensions and capacity must be >= 2")
        if not math.isfinite(spawn_threshold) or spawn_threshold <= 0:
            raise AIObstructionError("cluster spawn threshold must be finite and positive")
        if not 0 < learning_rate <= 1:
            raise AIObstructionError("cluster learning rate must lie in (0, 1]")
        self.axis_dim = int(axis_dim)
        self.max_clusters = int(max_clusters)
        self.spawn_threshold = float(spawn_threshold)
        self.learning_rate = float(learning_rate)
        self.register_buffer("centroids", torch.zeros(max_clusters, axis_dim))
        self.register_buffer("counts", torch.zeros(max_clusters, dtype=torch.long))
        self.register_buffer("modality_ids", torch.full((max_clusters,), -1, dtype=torch.long))
        self.register_buffer("active_count", torch.zeros((), dtype=torch.long))
        self.register_buffer("growth_step", torch.zeros((), dtype=torch.long))

    def reset_growth(self) -> None:
        with torch.no_grad():
            self.centroids.zero_()
            self.counts.zero_()
            self.modality_ids.fill_(-1)
            self.active_count.zero_()
            self.growth_step.zero_()

    def _spawn(self, value: torch.Tensor, modality_id: int) -> int:
        index = int(self.active_count.item())
        self.centroids[index].copy_(value)
        self.counts[index] = 1
        self.modality_ids[index] = modality_id
        self.active_count += 1
        return index

    def _update_state(
        self,
        axes: torch.Tensor,
        modality_names: tuple[str, ...],
    ) -> tuple[ClusterGrowthEvent, ...]:
        events: list[ClusterGrowthEvent] = []
        step = int(self.growth_step.item())
        with torch.no_grad():
            for sample_index in range(axes.shape[0]):
                for modality_id, modality in enumerate(modality_names):
                    value = axes[sample_index, modality_id].detach()
                    active = int(self.active_count.item())
                    compatible = torch.nonzero(
                        self.modality_ids[:active] == modality_id, as_tuple=False
                    ).reshape(-1)
                    if compatible.numel() == 0:
                        if active < self.max_clusters:
                            cluster = self._spawn(value, modality_id)
                            events.append(
                                ClusterGrowthEvent(step, "spawn", cluster, modality, float("nan"))
                            )
                        continue
                    distances = torch.linalg.vector_norm(
                        self.centroids[compatible] - value.unsqueeze(0), dim=-1
                    )
                    nearest_position = int(torch.argmin(distances).item())
                    nearest = int(compatible[nearest_position].item())
                    novelty = float(distances[nearest_position].item())
                    if novelty > self.spawn_threshold and active < self.max_clusters:
                        cluster = self._spawn(value, modality_id)
                        events.append(
                            ClusterGrowthEvent(step, "spawn", cluster, modality, novelty)
                        )
                    else:
                        rate = self.learning_rate / math.sqrt(float(self.counts[nearest].item()) + 1.0)
                        self.centroids[nearest].lerp_(value, rate)
                        self.counts[nearest] += 1
                        events.append(
                            ClusterGrowthEvent(step, "update", nearest, modality, novelty)
                        )
            self.growth_step += 1
        return tuple(events)

    def forward(
        self,
        axes: torch.Tensor,
        modality_names: tuple[str, ...],
        *,
        update: bool,
    ) -> ClusterGrowthState:
        require_finite_tensor(axes, "cluster-growth modality axes")
        if axes.ndim != 3 or axes.shape[-1] != self.axis_dim:
            raise AIObstructionError(
                f"cluster axes must have shape [batch, modalities, {self.axis_dim}]"
            )
        if len(modality_names) != axes.shape[1]:
            raise AIObstructionError("cluster growth requires one name per modality")
        events = self._update_state(axes, modality_names) if update else ()
        active = int(self.active_count.item())

        if active == 0:
            # Evaluation before fitting uses non-persistent modality means.  This
            # is reported as an open numerical candidate, not learned growth.
            prototypes = axes.detach().mean(dim=0)
            prototype_modalities = torch.arange(
                axes.shape[1], device=axes.device, dtype=torch.long
            )
            prototype_counts = torch.zeros(axes.shape[1], device=axes.device, dtype=torch.long)
        else:
            prototypes = self.centroids[:active].to(device=axes.device, dtype=axes.dtype)
            prototype_modalities = self.modality_ids[:active].to(device=axes.device)
            prototype_counts = self.counts[:active].to(device=axes.device)

        assignments: list[torch.Tensor] = []
        selected_distances: list[torch.Tensor] = []
        contexts: list[torch.Tensor] = []
        for modality_id in range(axes.shape[1]):
            compatible = torch.nonzero(
                prototype_modalities == modality_id, as_tuple=False
            ).reshape(-1)
            if compatible.numel() == 0:
                raise AIObstructionError("cluster growth has no compatible modality prototype")
            distances = torch.cdist(
                axes[:, modality_id, :], prototypes[compatible]
            )
            local_assignment = torch.argmin(distances, dim=-1)
            assignment = compatible[local_assignment]
            assignments.append(assignment)
            selected_distances.append(
                distances.gather(1, local_assignment.unsqueeze(-1)).squeeze(-1)
            )
            contexts.append(prototypes[assignment])
        assignment_tensor = torch.stack(assignments, dim=1)
        distance_tensor = require_finite_tensor(
            torch.stack(selected_distances, dim=1), "cluster selected distances"
        )
        context = require_finite_tensor(
            torch.stack(contexts, dim=1), "cluster context"
        )
        if prototypes.shape[0] == 1:
            topology = torch.zeros(1, 1, dtype=axes.dtype, device=axes.device)
        else:
            pairwise = torch.cdist(prototypes, prototypes)
            topology = torch.exp(-pairwise)
            topology.fill_diagonal_(0.0)
        residuals = {
            "cluster_coverage": torch.mean(distance_tensor),
            "cluster_topology_symmetry": torch.linalg.vector_norm(topology - topology.T),
            "cluster_capacity": torch.relu(
                torch.tensor(
                    float(active - self.max_clusters), dtype=axes.dtype, device=axes.device
                )
            ),
        }
        for name, residual in residuals.items():
            require_finite_tensor(residual, name)
        return ClusterGrowthState(
            assignments=assignment_tensor,
            selected_distance=distance_tensor,
            context=context,
            centroids=prototypes,
            cluster_modalities=prototype_modalities,
            cluster_counts=prototype_counts,
            topology_adjacency=topology,
            events=events,
            active_clusters=active if active else int(prototypes.shape[0]),
            residuals=residuals,
        )
