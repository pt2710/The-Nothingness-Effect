"""Differentiable finite Elastic-pi weighted transition norm."""

from __future__ import annotations

from dataclasses import dataclass
import math

import torch

from .types import AIObstructionError, require_finite_tensor


ELASTIC_PI_NORM_SOURCE_IDS = (
    "weighted_path_functional_and_norm_admissibility",
    "elastic_field_ratios_and_weight_regularity",
)


@dataclass(frozen=True)
class ElasticPiNormState:
    value: torch.Tensor
    transition_distances: torch.Tensor
    elastic_ratios: torch.Tensor
    order: float
    source_ids: tuple[str, ...] = ELASTIC_PI_NORM_SOURCE_IDS


def elastic_pi_transition_norm(
    trajectory: torch.Tensor,
    elastic_pi: torch.Tensor,
    *,
    order: float = 2.0,
) -> ElasticPiNormState:
    """Evaluate the declared weighted path functional across the final axis."""

    require_finite_tensor(trajectory, "Elastic-pi norm trajectory")
    require_finite_tensor(elastic_pi, "Elastic-pi norm field")
    if trajectory.ndim != 2 or trajectory.shape != elastic_pi.shape:
        raise AIObstructionError(
            "Elastic-pi norm requires equal [samples, transitions] tensors"
        )
    if trajectory.shape[-1] < 2:
        raise AIObstructionError("Elastic-pi norm requires at least one transition")
    if not math.isfinite(order) or order < 1:
        raise AIObstructionError("Elastic-pi norm order must be finite and at least one")
    if bool((elastic_pi <= 0).any()):
        raise AIObstructionError("Elastic-pi norm weights must be strictly positive")

    distances = torch.abs(trajectory[:, 1:] - trajectory[:, :-1])
    ratios = elastic_pi[:, 1:] / elastic_pi[:, :-1]
    require_finite_tensor(ratios, "Elastic-pi norm weight ratios")
    weighted = torch.sum(distances.pow(order) * ratios, dim=-1)
    value = require_finite_tensor(
        weighted.pow(1.0 / order), "Elastic-pi transition norm"
    )
    return ElasticPiNormState(value, distances, ratios, float(order))
