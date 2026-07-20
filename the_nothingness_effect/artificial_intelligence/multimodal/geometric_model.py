"""Geometry-aware TNE multimodal model over the no-local-RBM backbone."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.shared.closure_losses import arbitrate
from the_nothingness_effect.artificial_intelligence.shared.types import require_finite_tensor

from .model import TNETrainableMultimodalOutput
from .no_local_rbm_model import TNENoLocalRBMMultimodalModel


class TNEGeometricMultimodalModel(TNENoLocalRBMMultimodalModel):
    """Add explicit rotated 3D, dual and MPL-TC growth context to the task head.

    Raw modalities still pass through the same Observation--Collapse encoder.
    The axis network supplies distinct modality frames, antipodal duals,
    Observer-Horizon values and four tetrahedral MPL-TC stream directions.
    Local RBM regulation is removed; learned normalized modality precision and
    one aggregate global energy model remain.
    """

    def __init__(
        self,
        input_dim: int = 6,
        hidden_dim: int = 16,
        output_dim: int = 4,
        *,
        K_D: float = 1.0,
        soi_scale: float = 1.0,
        qenn_count: int = 1,
        pgqenn_count: int = 1,
        mpl_tc_repository: str | Path | None = None,
        raw_observation_collapse_enabled: bool = True,
        elastic_dubler_enabled: bool = True,
        modality_count: int = 5,
        axis_dim: int | None = None,
        global_rbm_hidden: int | None = None,
        max_clusters: int = 40,
        dropout: float = 0.05,
    ) -> None:
        super().__init__(
            input_dim,
            hidden_dim,
            output_dim,
            K_D=K_D,
            soi_scale=soi_scale,
            qenn_count=qenn_count,
            pgqenn_count=pgqenn_count,
            mpl_tc_repository=mpl_tc_repository,
            raw_observation_collapse_enabled=raw_observation_collapse_enabled,
            elastic_dubler_enabled=elastic_dubler_enabled,
            modality_count=modality_count,
            axis_dim=axis_dim,
            global_rbm_hidden=global_rbm_hidden,
            max_clusters=max_clusters,
            dropout=dropout,
        )
        self.geometry_projection = nn.Linear(3, hidden_dim, bias=False)
        self.dual_projection = nn.Linear(3, hidden_dim, bias=False)
        self.growth_projection = nn.Linear(3, hidden_dim, bias=False)
        self.horizon_projection = nn.Linear(1, hidden_dim, bias=False)
        self.geometric_context_enabled = True
        self.dual_context_enabled = True
        self.observer_horizon_growth_enabled = True

    def forward(
        self,
        modalities: Mapping[str, torch.Tensor],
        *,
        tolerance: float = 1e-5,
    ) -> TNETrainableMultimodalOutput:
        output = super().forward(modalities, tolerance=tolerance)
        axis = output.axis_state
        weights = output.regulated_modality_weights
        if axis is None or weights is None:
            raise RuntimeError("geometric model requires axis and modality-weight state")

        geometry = torch.sum(
            weights.unsqueeze(-1) * axis.geometric_coordinates,
            dim=1,
        )
        negative_horizon_pressure = torch.relu(-axis.observer_horizon)
        dual_weights = weights * (1.0 + negative_horizon_pressure)
        dual_weights = dual_weights / dual_weights.sum(
            dim=-1,
            keepdim=True,
        ).clamp_min(1e-8)
        dual_geometry = torch.sum(
            dual_weights.unsqueeze(-1) * axis.dual_coordinates,
            dim=1,
        )
        growth = torch.sum(
            weights.unsqueeze(-1) * axis.mpl_tc_growth_vectors,
            dim=1,
        )
        horizon_pressure = torch.sum(
            weights * negative_horizon_pressure,
            dim=1,
            keepdim=True,
        )

        hidden = output.hidden
        if self.geometric_context_enabled:
            hidden = hidden + self.geometry_projection(geometry)
            hidden = hidden + self.growth_projection(growth)
        if self.dual_context_enabled:
            hidden = hidden + self.dual_projection(dual_geometry)
        if self.observer_horizon_growth_enabled:
            hidden = hidden + self.horizon_projection(horizon_pressure)
        hidden = require_finite_tensor(
            self.context_dropout(torch.tanh(self.context_norm(hidden))),
            "geometry-aware multimodal hidden state",
        )
        logits = require_finite_tensor(
            self.task_head(hidden),
            "geometry-aware multimodal logits",
        )
        observation_state = self.sample_observation(logits)
        reconstruction = require_finite_tensor(
            torch.nn.functional.softplus(self.shared_token_decoder(hidden)),
            "geometry-aware shared reconstruction",
        )

        output.hidden = hidden
        output.fused_hidden = hidden
        output.readout = logits
        output.observation = observation_state.probabilities
        output.sample_observation_state = observation_state
        output.reconstructed_fused_tokens = reconstruction
        output.reconstructed_modality_tokens = {
            name: reconstruction
            for name in output.backbone_output.modality_names
        }
        output.residuals.update(
            {
                "geometry::dual_involution": torch.max(
                    torch.abs(
                        axis.dual_coordinates
                        + axis.geometric_coordinates
                    )
                ),
                "geometry::stream_normalization": torch.max(
                    torch.abs(
                        axis.mpl_tc_stream_weights.sum(dim=-1)
                        - 1.0
                    )
                ),
                "geometry::negative_horizon_pressure": torch.max(
                    torch.relu(-horizon_pressure)
                ),
            }
        )
        output.closure_status = arbitrate(
            output.residuals,
            tolerance,
        )
        output.metadata.update(
            {
                "geometric_architecture": (
                    "modality_rotated_three_dimensional"
                ),
                "geometric_modalities": list(axis.modality_names),
                "geometric_dual": (
                    "antipodal_positive_negative_carrier"
                ),
                "observer_horizon": (
                    "negative_only_pressure_increases_dual_context"
                ),
                "mpl_tc_growth": (
                    "four_stream_tetrahedral_directions_"
                    "rotated_by_modality_frame"
                ),
                "geometry_context_enabled": self.geometric_context_enabled,
                "dual_context_enabled": self.dual_context_enabled,
                "observer_horizon_growth_enabled": (
                    self.observer_horizon_growth_enabled
                ),
                "local_rbm": "removed",
            }
        )
        return output
