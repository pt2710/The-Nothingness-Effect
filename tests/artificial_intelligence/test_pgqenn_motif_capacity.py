from __future__ import annotations

import torch

from the_nothingness_effect.artificial_intelligence.pgqenn import model as pgqenn_model


def test_feature_compression_consumes_every_row_and_preserves_gradients() -> None:
    features = torch.arange(51, dtype=torch.float32).reshape(17, 3)
    features.requires_grad_(True)

    pooled, bucket_sizes = pgqenn_model._compress_feature_nodes(features, 5)

    assert pooled.shape == (5, 3)
    assert bucket_sizes == (4, 4, 3, 3, 3)
    assert sum(bucket_sizes) == features.shape[0]
    assert torch.allclose(pooled[0], features[:4].mean(dim=0))
    assert torch.allclose(pooled[-1], features[-3:].mean(dim=0))

    pooled.sum().backward()
    assert features.grad is not None
    assert torch.isfinite(features.grad).all()
    assert bool((features.grad.abs().sum(dim=1) > 0).all())


def test_pgqenn_forward_reduces_only_the_finite_graph_carrier(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        pgqenn_model,
        "_mpl_tc_motif_capacity",
        lambda _provider: 5,
    )
    model = pgqenn_model.PGQENNModel(
        input_dim=4,
        hidden_dim=6,
        output_dim=2,
        triadic_streams_enabled=False,
        signed_spectrum_enabled=False,
    )
    features = torch.linspace(0.1, 2.8, 28).reshape(7, 4)

    output = model(features)

    assert output.graph is not None
    assert output.hidden.shape[0] == 5
    assert len(output.mpl_motifs) == 5
    assert output.metadata["input_node_count"] == 7
    assert output.metadata["graph_node_count"] == 5
    assert output.metadata["mpl_tc_motif_capacity"] == 5
    assert output.metadata["mpl_tc_capacity_reduction"] == (
        "contiguous_mean_pool_all_rows"
    )
    assert output.metadata["mpl_tc_source_rows_consumed"] == 7
    assert output.metadata["mpl_tc_pool_bucket_min"] == 1
    assert output.metadata["mpl_tc_pool_bucket_max"] == 2
    assert float(output.residuals["mpl_tc_motif_exhaustion"]) == 0.0
