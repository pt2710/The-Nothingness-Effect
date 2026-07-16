"""Batch-trainable multimodal model over the canonical SOInet backbone."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.shared.closure_losses import arbitrate
from the_nothingness_effect.artificial_intelligence.shared.observation_collapse import (
    ObservationCollapseReadout,
    ObservationCollapseState,
)
from the_nothingness_effect.artificial_intelligence.shared.provenance import backend_metadata
from the_nothingness_effect.artificial_intelligence.shared.types import (
    TNEAIOutput,
    require_finite_tensor,
)
from the_nothingness_effect.artificial_intelligence.soinets.multimodal import (
    TNEMultimodalOutput,
    TNEMultimodalSOInet,
)


@dataclass
class TNETrainableMultimodalOutput(TNEAIOutput):
    """Per-sample task output plus the complete TNE multimodal backbone state."""

    backbone_output: TNEMultimodalOutput | None = None
    sample_observation_state: ObservationCollapseState | None = None
    fused_hidden: torch.Tensor | None = None
    reconstructed_fused_tokens: torch.Tensor | None = None
    reconstructed_modality_tokens: dict[str, torch.Tensor] | None = None


class TNETrainableMultimodalModel(nn.Module):
    """Trainable color/sound/vision model with a canonical SOInet backbone.

    The backbone supplies raw observation/collapse, normalized DFI, exact
    Elastic-pi and Elastic Dubler fusion, QENN/DTQC, PGQENN/MPL-TC and SOInet
    meta-closure.  This class adds a per-sample task head and shared token
    decoder so training, validation and evaluation operate on batches rather
    than on one batch-aggregate meta-readout.
    """

    def __init__(
        self,
        input_dim: int = 6,
        hidden_dim: int = 12,
        output_dim: int = 4,
        *,
        K_D: float = 1.0,
        qenn_count: int = 1,
        pgqenn_count: int = 1,
        mpl_tc_repository: str | Path | None = None,
        raw_observation_collapse_enabled: bool = True,
        elastic_dubler_enabled: bool = True,
    ) -> None:
        super().__init__()
        self.input_dim = int(input_dim)
        self.hidden_dim = int(hidden_dim)
        self.output_dim = int(output_dim)
        self.backbone = TNEMultimodalSOInet(
            input_dim,
            hidden_dim,
            output_dim,
            K_D=K_D,
            qenn_count=qenn_count,
            pgqenn_count=pgqenn_count,
            mpl_tc_repository=mpl_tc_repository,
            raw_observation_collapse_enabled=raw_observation_collapse_enabled,
            elastic_dubler_enabled=elastic_dubler_enabled,
        )
        self.fused_projection = nn.Linear(input_dim, hidden_dim)
        self.meta_projection = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.task_head = nn.Linear(hidden_dim, output_dim)
        self.shared_token_decoder = nn.Linear(hidden_dim, input_dim)
        self.sample_observation = ObservationCollapseReadout()

    def forward(
        self,
        modalities: Mapping[str, torch.Tensor],
        *,
        tolerance: float = 1e-5,
    ) -> TNETrainableMultimodalOutput:
        backbone = self.backbone(modalities, tolerance=tolerance)
        if backbone.fused_state is None or backbone.soinet_output is None:
            raise RuntimeError("multimodal backbone did not return its typed fusion state")
        meta_context = self.meta_projection(backbone.soinet_output.hidden).unsqueeze(0)
        hidden = require_finite_tensor(
            torch.tanh(self.fused_projection(backbone.fused_state) + meta_context),
            "trainable multimodal hidden state",
        )
        logits = require_finite_tensor(self.task_head(hidden), "multimodal task logits")
        observation_state = self.sample_observation(logits)
        reconstruction = require_finite_tensor(
            torch.nn.functional.softplus(self.shared_token_decoder(hidden)),
            "multimodal shared token reconstruction",
        )
        reconstructed = {
            name: reconstruction for name in backbone.modality_names
        }
        target_token = torch.mean(backbone.modality_tokens, dim=1)
        residuals = {
            **{
                f"backbone::{name}": residual
                for name, residual in backbone.residuals.items()
            },
            **{
                f"sample::{name}": residual
                for name, residual in observation_state.residuals.items()
            },
            "fused_token_reconstruction": torch.sqrt(
                torch.mean((reconstruction - target_token) ** 2)
            ),
        }
        for name, residual in residuals.items():
            require_finite_tensor(residual, f"trainable multimodal residual {name}")
        return TNETrainableMultimodalOutput(
            hidden=hidden,
            readout=logits,
            observation=observation_state.probabilities,
            dfi=backbone.dfi,
            elastic_gain=backbone.elastic_gain,
            residuals=residuals,
            closure_status=arbitrate(residuals, tolerance),
            metadata={
                **backend_metadata(),
                "architecture": "TNE Trainable Multimodal SOInet",
                "backbone": "TNEMultimodalSOInet",
                "dependency_chain": backbone.metadata["dependency_chain"],
                "batch_task_readout": "typed_per_sample",
                "claim_boundary": (
                    "finite trained computational model; not a formal proof substitute"
                ),
            },
            backbone_output=backbone,
            sample_observation_state=observation_state,
            fused_hidden=hidden,
            reconstructed_fused_tokens=reconstruction,
            reconstructed_modality_tokens=reconstructed,
        )
