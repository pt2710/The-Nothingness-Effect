"""Differentiable multi-QENN/PGQENN SOInet with fail-closed arbitration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.shared.closure_losses import arbitrate
from the_nothingness_effect.artificial_intelligence.shared.observation_collapse import (
    ObservationCollapseReadout,
    ObservationCollapseState,
)
from the_nothingness_effect.artificial_intelligence.shared.provenance import backend_metadata
from the_nothingness_effect.artificial_intelligence.shared.types import TNEAIOutput, require_finite_tensor

from .meta_closure import complete_meta_adjacency, meta_residuals
from .subnetworks import SubnetworkEnsemble


@dataclass
class SOInetOutput(TNEAIOutput):
    qenn_outputs: tuple[object, ...] = ()
    pgqenn_outputs: tuple[object, ...] = ()
    meta_state: torch.Tensor | None = None
    meta_adjacency: torch.Tensor | None = None
    memory_transfers: tuple[torch.Tensor, torch.Tensor] | None = None
    observation_collapse_state: ObservationCollapseState | None = None


class SOInetModel(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        *,
        qenn_count: int = 2,
        pgqenn_count: int = 2,
        K_D: float = 1.0,
        mpl_tc_repository: str | Path | None = None,
    ):
        super().__init__()
        self.ensemble = SubnetworkEnsemble(
            input_dim,
            hidden_dim,
            output_dim,
            qenn_count=qenn_count,
            pgqenn_count=pgqenn_count,
            K_D=K_D,
            mpl_tc_repository=mpl_tc_repository,
        )
        self.q_to_p = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.p_to_q = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.meta_readout = nn.Linear(hidden_dim, output_dim)
        self.observation_collapse = ObservationCollapseReadout()

    def forward(self, qenn_features: torch.Tensor, pgqenn_features: torch.Tensor, *, tolerance: float = 1e-5) -> SOInetOutput:
        require_finite_tensor(qenn_features, "SOInet QENN modality")
        require_finite_tensor(pgqenn_features, "SOInet PGQENN modality")
        q_outputs, p_outputs = self.ensemble(qenn_features, pgqenn_features)
        q_states = torch.stack([output.hidden.mean(dim=0) for output in q_outputs])
        p_states = torch.stack([output.hidden.mean(dim=0) for output in p_outputs])
        q_state = q_states.mean(dim=0)
        p_state = p_states.mean(dim=0)
        q_to_p = self.q_to_p(q_state)
        p_to_q = self.p_to_q(p_state)
        transferred_q = q_state + p_to_q
        transferred_p = p_state + q_to_p
        states = torch.cat((q_states, p_states, transferred_q.unsqueeze(0), transferred_p.unsqueeze(0)), dim=0)
        adjacency = complete_meta_adjacency(states.shape[0], dtype=states.dtype, device=states.device)
        residuals = meta_residuals(states, adjacency, q_to_p, p_to_q, q_state, p_state)
        # Subnetwork residuals are part of completeness arbitration, not hidden
        # behind a finite-output check.
        residuals["subnetwork_completeness"] = torch.stack([
            *[torch.stack(tuple(output.residuals.values())).sum() for output in q_outputs],
            *[torch.stack(tuple(output.residuals.values())).sum() for output in p_outputs],
        ]).sum()
        meta_state = require_finite_tensor(states.mean(dim=0), "SOInet meta state")
        subnetwork_logits = torch.stack([output.readout.mean(dim=0) for output in (*q_outputs, *p_outputs)]).mean(dim=0, keepdim=True)
        logits = self.meta_readout(meta_state.unsqueeze(0)) + subnetwork_logits
        observation_state = self.observation_collapse(logits)
        observation = observation_state.probabilities
        residuals.update(observation_state.residuals)
        dfi = torch.cat([output.dfi.reshape(-1) for output in (*q_outputs, *p_outputs)])
        elastic = torch.cat([output.elastic_gain.reshape(-1) for output in (*q_outputs, *p_outputs)])
        status = arbitrate(residuals, tolerance)
        mpl_commits = tuple(sorted({output.metadata["mpl_tc_commit"] for output in p_outputs}))
        return SOInetOutput(
            hidden=meta_state,
            readout=logits,
            observation=observation,
            dfi=dfi,
            elastic_gain=elastic,
            residuals=residuals,
            closure_status=status,
            metadata={
                **backend_metadata(),
                "architecture": "SOInet",
                "qenn_count": len(q_outputs),
                "pgqenn_count": len(p_outputs),
                "arbitration": "fail_closed",
                "dependency_chain": ("DTQC->QENN", "QENN+MPL-TC->PGQENN", "QENN+PGQENN->SOInet"),
                "mpl_tc_commits": mpl_commits,
                "observation_collapse_integration": "canonical_meta_aggregation",
            },
            qenn_outputs=tuple(q_outputs),
            pgqenn_outputs=tuple(p_outputs),
            meta_state=meta_state,
            meta_adjacency=adjacency,
            memory_transfers=(q_to_p, p_to_q),
            observation_collapse_state=observation_state,
        )
