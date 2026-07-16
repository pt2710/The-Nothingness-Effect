"""Typed, fail-closed observation and collapse readout for TNE AI models."""

from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch import nn
from torch.nn import functional as functional

from .types import AIObstructionError, require_finite_tensor


OBSERVATION_COLLAPSE_SOURCE_IDS = (
    "observation_induced_collapse_and_collapse_divergence",
    "definite_state_projection_and_state_ambiguity",
    "fixed_point_consistency_and_trivial_collapse_failure",
)


@dataclass(frozen=True)
class ObservationCollapseState:
    """Finite observation probabilities and their idempotent outcome projection."""

    probabilities: torch.Tensor
    selected_indices: torch.Tensor
    collapsed_outcome: torch.Tensor
    residuals: dict[str, torch.Tensor]
    source_ids: tuple[str, ...] = OBSERVATION_COLLAPSE_SOURCE_IDS


class ObservationCollapseReadout(nn.Module):
    """Normalize logits and project each sample onto one definite outcome.

    The probability field remains differentiable.  The discrete collapsed
    outcome is diagnostic evidence and is never represented as a formal proof
    of mathematical collapse or attainment.
    """

    def __init__(self, *, temperature: float = 1.0) -> None:
        super().__init__()
        if not math.isfinite(temperature) or temperature <= 0:
            raise AIObstructionError("observation temperature must be finite and positive")
        self.temperature = float(temperature)

    @staticmethod
    def _collapse(probabilities: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        indices = torch.argmax(probabilities, dim=-1)
        collapsed = functional.one_hot(indices, num_classes=probabilities.shape[-1]).to(
            dtype=probabilities.dtype
        )
        return indices, collapsed

    def forward(self, logits: torch.Tensor) -> ObservationCollapseState:
        require_finite_tensor(logits, "observation/collapse logits")
        if logits.ndim != 2 or logits.shape[-1] < 1:
            raise AIObstructionError("observation/collapse expects [samples, outcomes]")

        probabilities = require_finite_tensor(
            torch.softmax(logits / self.temperature, dim=-1),
            "observation probability field",
        )
        indices, collapsed = self._collapse(probabilities)
        repeated_indices, repeated_collapse = self._collapse(collapsed)
        residuals = {
            "observation_normalization": torch.max(
                torch.abs(probabilities.sum(dim=-1) - 1.0)
            ),
            "collapse_projection_normalization": torch.max(
                torch.abs(collapsed.sum(dim=-1) - 1.0)
            ),
            "collapse_idempotence": torch.linalg.vector_norm(
                repeated_collapse - collapsed
            ),
            "collapse_outcome_stability": torch.count_nonzero(
                repeated_indices != indices
            ).to(dtype=logits.dtype),
        }
        for name, residual in residuals.items():
            require_finite_tensor(residual, f"observation/collapse residual {name}")
        return ObservationCollapseState(probabilities, indices, collapsed, residuals)
