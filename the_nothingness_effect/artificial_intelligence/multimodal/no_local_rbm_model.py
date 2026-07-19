"""Multimodal realization with learned precision and no local RBM.

The canonical local Gaussian--Bernoulli RBM was an external numerical
regularizer rather than a TNE source law.  This module removes that local RBM
from the trained geometric path.  Per-modality precision is learned directly
from the modality-axis carriers, while the global RBM remains available as a
single aggregate energy model.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import torch
from torch import nn
from torch.nn import functional

from the_nothingness_effect.artificial_intelligence.shared.closure_losses import arbitrate
from the_nothingness_effect.artificial_intelligence.shared.provenance import backend_metadata
from the_nothingness_effect.artificial_intelligence.shared.types import require_finite_tensor

from .growth import ClusterGrowthState
from .model import TNETrainableMultimodalModel, TNETrainableMultimodalOutput
from .rbm import GaussianBernoulliEnergyLayer


class TNENoLocalRBMMultimodalModel(TNETrainableMultimodalModel):
    """Trainable multimodal model with learned precision and one global RBM.

    The inherited constructor is used only to preserve the public model
    surface.  The local RBM module is then deleted from the final module tree,
    the global RBM is rebound to the complete flattened modality-axis field,
    and a normalized precision scorer replaces local free-energy weighting.
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
            local_rbm_hidden=global_rbm_hidden,
            max_clusters=max_clusters,
        )
        if not 0.0 <= dropout < 1.0:
            raise ValueError("dropout must lie in [0, 1)")
        resolved_axis_dim = int(self.axis_projection.in_features)
        resolved_global_hidden = int(global_rbm_hidden or resolved_axis_dim)

        # The final model contains no local RBM parameters or local RBM state.
        del self.local_energy
        self.modality_precision_norm = nn.LayerNorm(resolved_axis_dim)
        self.modality_precision_score = nn.Linear(
            resolved_axis_dim,
            1,
            bias=False,
        )
        self.precision_temperature_raw = nn.Parameter(torch.zeros(()))
        self.global_energy = GaussianBernoulliEnergyLayer(
            self.modality_count * resolved_axis_dim,
            resolved_global_hidden,
        )
        self.energy_projection = nn.Linear(
            resolved_global_hidden,
            hidden_dim,
            bias=False,
        )
        self.context_norm = nn.LayerNorm(hidden_dim)
        self.context_dropout = nn.Dropout(dropout)

    def _precision_weights(self, mapped_axes: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        temperature = functional.softplus(self.precision_temperature_raw) + 0.25
        logits = self.modality_precision_score(
            self.modality_precision_norm(mapped_axes)
        ).squeeze(-1)
        weights = require_finite_tensor(
            torch.softmax(logits / temperature, dim=-1),
            "learned modality precision",
        )
        entropy = -torch.sum(
            weights * torch.log(weights.clamp_min(1e-9)),
            dim=-1,
        ) / torch.log(
            torch.tensor(
                float(self.modality_count),
                dtype=weights.dtype,
                device=weights.device,
            )
        )
        return weights, require_finite_tensor(
            entropy,
            "normalized modality precision entropy",
        )

    def forward(
        self,
        modalities: Mapping[str, torch.Tensor],
        *,
        tolerance: float = 1e-5,
    ) -> TNETrainableMultimodalOutput:
        backbone = self.backbone(modalities, tolerance=tolerance)
        if backbone.fused_state is None or backbone.soinet_output is None:
            raise RuntimeError("multimodal backbone did not return its typed fusion state")
        if backbone.modality_tokens is None or backbone.modality_weights is None:
            raise RuntimeError("multimodal backbone did not return modality carriers")
        if len(backbone.modality_names) != self.modality_count:
            raise ValueError(
                f"model expects {self.modality_count} modalities, got "
                f"{len(backbone.modality_names)}"
            )

        axis_state = self.axis_network(
            backbone.modality_tokens,
            backbone.modality_names,
            backbone.modality_weights,
        )
        batch, modality_count, axis_dim = axis_state.mapped_axes.shape
        precision, precision_entropy = self._precision_weights(
            axis_state.mapped_axes
        )
        if self.energy_regulation_enabled:
            regulated_weights = backbone.modality_weights * precision
            regulated_weights = regulated_weights / regulated_weights.sum(
                dim=-1,
                keepdim=True,
            ).clamp_min(1e-8)
        else:
            regulated_weights = backbone.modality_weights

        global_visible = axis_state.mapped_axes.reshape(
            batch,
            modality_count * axis_dim,
        )
        global_rbm = self.global_energy(
            global_visible,
            steps=1,
            stochastic=False,
        )
        cluster_state: ClusterGrowthState = self.cluster_growth(
            axis_state.mapped_axes,
            backbone.modality_names,
            update=self.training,
        )
        regulated_axis = require_finite_tensor(
            torch.sum(
                regulated_weights.unsqueeze(-1) * axis_state.mapped_axes,
                dim=1,
            ),
            "learned-precision modality-axis fusion",
        )
        cluster_context = require_finite_tensor(
            torch.sum(
                regulated_weights.unsqueeze(-1) * cluster_state.context,
                dim=1,
            ),
            "cluster-growth context",
        )
        meta_context = self.meta_projection(
            backbone.soinet_output.hidden
        ).unsqueeze(0)
        axis_contribution = (
            self.axis_projection(regulated_axis)
            if self.axis_network_enabled
            else torch.zeros_like(meta_context.expand(batch, -1))
        )
        energy_contribution = (
            self.energy_projection(global_rbm.hidden_probability)
            if self.energy_regulation_enabled
            else torch.zeros_like(axis_contribution)
        )
        cluster_contribution = (
            self.cluster_projection(cluster_context)
            if self.cluster_context_enabled
            else torch.zeros_like(axis_contribution)
        )
        preactivation = (
            self.fused_projection(backbone.fused_state)
            + meta_context
            + axis_contribution
            + energy_contribution
            + cluster_contribution
        )
        hidden = require_finite_tensor(
            self.context_dropout(torch.tanh(self.context_norm(preactivation))),
            "no-local-RBM multimodal hidden state",
        )
        logits = require_finite_tensor(
            self.task_head(hidden),
            "no-local-RBM multimodal task logits",
        )
        observation_state = self.sample_observation(logits)
        reconstruction = require_finite_tensor(
            torch.nn.functional.softplus(self.shared_token_decoder(hidden)),
            "no-local-RBM shared token reconstruction",
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
            **{
                f"axis::{name}": residual
                for name, residual in axis_state.residuals.items()
            },
            "precision::normalization": torch.max(
                torch.abs(precision.sum(dim=-1) - 1.0)
            ),
            "precision::entropy_floor": torch.relu(
                torch.tensor(
                    0.35,
                    dtype=precision_entropy.dtype,
                    device=precision_entropy.device,
                )
                - precision_entropy.mean()
            ),
            "precision::regulated_weight_normalization": torch.max(
                torch.abs(regulated_weights.sum(dim=-1) - 1.0)
            ),
            "rbm::global_reconstruction": global_rbm.reconstruction_residual,
            **{
                f"growth::{name}": residual
                for name, residual in cluster_state.residuals.items()
            },
        }
        for name, residual in residuals.items():
            require_finite_tensor(
                residual,
                f"no-local-RBM multimodal residual {name}",
            )
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
                "architecture": "TNE Trainable Multimodal SOInet without local RBM",
                "backbone": "TNEMultimodalSOInet",
                "dependency_chain": backbone.metadata["dependency_chain"],
                "batch_task_readout": "typed_per_sample",
                "modality_axes": "learned_shared_private_cycle_checked",
                "local_rbm": "removed",
                "modality_precision": "learned_normalized_axis_score",
                "energy_realization": "single_global_gaussian_bernoulli_rbm",
                "energy_source_status": "external_numerical_realization_not_tne_source_law",
                "cluster_growth": "bounded_deterministic_modality_prototypes",
                "precision_temperature": float(
                    (functional.softplus(self.precision_temperature_raw) + 0.25)
                    .detach()
                    .cpu()
                ),
                "dynamic_K_D": float(
                    self.backbone.elastic_dubler.K_D.detach().cpu()
                ) if self.backbone.elastic_dubler is not None else None,
                "dynamic_K_D_semantics": (
                    "exact positive source-law parameter; no exponent clipping"
                ),
                "active_clusters": cluster_state.active_clusters,
                "claim_boundary": (
                    "finite trained computational model; not a formal proof substitute"
                ),
            },
            backbone_output=backbone,
            sample_observation_state=observation_state,
            fused_hidden=hidden,
            reconstructed_fused_tokens=reconstruction,
            reconstructed_modality_tokens=reconstructed,
            axis_state=axis_state,
            local_rbm_state=None,
            global_rbm_state=global_rbm,
            cluster_state=cluster_state,
            energy_precision=precision,
            regulated_modality_weights=regulated_weights,
        )
