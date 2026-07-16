"""Differentiable canonical PGQENN model."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.shared.closure_losses import arbitrate, parseval_residual
from the_nothingness_effect.artificial_intelligence.shared.elastic_pi_gates import ElasticPiGate
from the_nothingness_effect.artificial_intelligence.shared.entropy_gates import parity_conditioned_dfi
from the_nothingness_effect.artificial_intelligence.shared.observation_collapse import (
    ObservationCollapseReadout,
    ObservationCollapseState,
)
from the_nothingness_effect.artificial_intelligence.shared.provenance import backend_metadata
from the_nothingness_effect.artificial_intelligence.shared.types import TNEAIOutput, require_finite_tensor
from the_nothingness_effect.artificial_intelligence.qenn.model import QENNModel, QENNOutput

from .growth_law import CanonicalPrimeGrowth, PrimeGraph
from .message_passing import PrimeEquivariantMessagePassing
from .mpl_tc_dependency import MPLTCMotifProvider


@dataclass
class PGQENNOutput(TNEAIOutput):
    graph: PrimeGraph | None = None
    pdfi: torch.Tensor | None = None
    node_state: torch.Tensor | None = None
    qenn_backbone_output: QENNOutput | None = None
    mpl_motifs: tuple[str, ...] = ()
    observation_collapse_state: ObservationCollapseState | None = None


class PGQENNModel(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        *,
        K_D: float = 1.0,
        motif_width: int = 2,
        mpl_tc_repository: str | Path | None = None,
        qenn_dtqc_enabled: bool = True,
    ):
        super().__init__()
        if min(input_dim, hidden_dim, output_dim) <= 0:
            raise ValueError("PGQENN dimensions must be positive")
        self.qenn_backbone = QENNModel(
            input_dim,
            hidden_dim,
            hidden_dim,
            K_D=K_D,
            dtqc_enabled=qenn_dtqc_enabled,
        )
        self.growth = CanonicalPrimeGrowth(
            motif_width,
            provider=MPLTCMotifProvider(mpl_tc_repository),
        )
        self.message_passing = PrimeEquivariantMessagePassing(hidden_dim, hidden_dim)
        self.elastic_gate = ElasticPiGate(K_D)
        self.readout_layer = nn.Linear(hidden_dim, output_dim)
        self.observation_collapse = ObservationCollapseReadout()

    def forward(self, features: torch.Tensor, graph: PrimeGraph | None = None, *, tolerance: float = 1e-5) -> PGQENNOutput:
        require_finite_tensor(features, "PGQENN input")
        if features.ndim != 2 or features.shape[1] != self.qenn_backbone.equivariant.linear.in_features:
            raise ValueError("PGQENN input must have shape [nodes, input_dim]")
        qenn_output = self.qenn_backbone(features, tolerance=tolerance)
        graph = graph or self.growth.build(features.shape[0], dtype=features.dtype)
        hidden = self.message_passing(qenn_output.hidden, graph)
        dfi = qenn_output.dfi
        adjacency = graph.adjacency.to(dtype=features.dtype, device=features.device)
        degree_sequence = adjacency.sum(dim=-1) + 1.0
        parity_mask = torch.tensor(
            [(index + graph.two_adic_depths[index].value) % 2 for index in range(len(graph.primes) - 1)],
            dtype=features.dtype,
            device=features.device,
        )
        pdfi = parity_conditioned_dfi(degree_sequence, parity_mask)
        entropy = dfi.abs() + pdfi
        elastic = self.elastic_gate(entropy)
        gain = torch.mean(elastic / torch.pi, dim=-1, keepdim=True)
        node_state = require_finite_tensor(
            0.5 * (hidden * gain + qenn_output.readout),
            "PGQENN QENN-composed gated state",
        )
        logits = self.readout_layer(node_state.mean(dim=0, keepdim=True))
        observation_state = self.observation_collapse(logits)
        observation = observation_state.probabilities
        residuals = {
            "message_equivariance": self.message_passing.equivariance_residual(qenn_output.hidden, graph),
            "graph_symmetry": torch.linalg.vector_norm(adjacency - adjacency.T),
            "self_loop": torch.linalg.vector_norm(torch.diagonal(adjacency)),
            "parseval": parseval_residual(node_state),
            "qenn_backbone_completeness": torch.stack(tuple(qenn_output.residuals.values())).sum(),
            "mpl_tc_dependency": torch.zeros((), dtype=features.dtype, device=features.device),
            "mpl_tc_motif_exhaustion": torch.tensor(
                abs(len(graph.motifs) - features.shape[0]),
                dtype=features.dtype,
                device=features.device,
            ),
            **observation_state.residuals,
        }
        status = arbitrate(residuals, tolerance)
        metadata = {
            **backend_metadata(),
            "architecture": "PGQENN",
            "architecture_base": "QENN",
            "qenn_dtqc_integration": qenn_output.metadata["dtqc_integration"],
            "qenn_observation_collapse_integration": qenn_output.metadata[
                "observation_collapse_integration"
            ],
            "observation_collapse_integration": "canonical_runtime",
            "growth_mode": graph.growth_mode,
            "mpl_tc_repository": graph.dependency_url,
            "mpl_tc_commit": graph.dependency_commit,
            "mpl_tc_module_sha256": graph.dependency_sha256,
        }
        return PGQENNOutput(
            hidden=node_state,
            readout=logits,
            observation=observation,
            dfi=dfi,
            elastic_gain=elastic,
            residuals=residuals,
            closure_status=status,
            metadata=metadata,
            graph=graph,
            pdfi=pdfi,
            node_state=node_state,
            qenn_backbone_output=qenn_output,
            mpl_motifs=graph.motifs,
            observation_collapse_state=observation_state,
        )
