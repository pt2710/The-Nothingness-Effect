from __future__ import annotations

import torch

from the_nothingness_effect.artificial_intelligence.soinets.model import SOInetModel
from the_nothingness_effect.artificial_intelligence.soinets.training import training_step


def test_soinet_runs_multiple_subnetworks_and_fail_closed_meta_residuals():
    torch.manual_seed(0)
    model = SOInetModel(5, 7, 3, qenn_count=2, pgqenn_count=2)
    qenn = (torch.rand((8, 5)) + 0.2).requires_grad_()
    pgqenn = (torch.rand((9, 5)) + 0.2).requires_grad_()
    output = model(qenn, pgqenn)
    assert len(output.qenn_outputs) == 2 and len(output.pgqenn_outputs) == 2
    assert all(item.dtqc_state is not None for item in output.qenn_outputs)
    assert all(item.qenn_backbone_output is not None for item in output.pgqenn_outputs)
    assert all(item.qenn_backbone_output.dtqc_state is not None for item in output.pgqenn_outputs)
    assert all(item.observation_collapse_state is not None for item in output.qenn_outputs)
    assert all(item.observation_collapse_state is not None for item in output.pgqenn_outputs)
    assert output.observation_collapse_state is not None
    assert output.metadata["dependency_chain"] == (
        "DTQC->QENN",
        "QENN+MPL-TC->PGQENN",
        "QENN+PGQENN->SOInet",
    )
    assert output.metadata["mpl_tc_commits"] == ("056e346824e9ec9785ab45b642b3b842c88f6e56",)
    assert output.metadata["observation_collapse_integration"] == "canonical_meta_aggregation"
    assert output.meta_adjacency is not None and output.meta_adjacency.shape == (6, 6)
    assert output.memory_transfers is not None
    assert set(output.residuals) == {
        "bidirectional_memory", "spectral", "spatial_reconstruction",
        "spatial_boundary", "local_observability", "subnetwork_completeness",
        "observation_normalization", "collapse_projection_normalization",
        "collapse_idempotence", "collapse_outcome_stability",
    }
    assert output.metadata["arbitration"] == "fail_closed"
    loss = training_step(model, qenn, pgqenn, torch.tensor(1))
    loss.backward()
    assert qenn.grad is not None and pgqenn.grad is not None
    assert all(parameter.grad is not None for parameter in model.parameters())
