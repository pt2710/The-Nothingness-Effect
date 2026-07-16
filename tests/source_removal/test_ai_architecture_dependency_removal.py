from __future__ import annotations

import torch

from the_nothingness_effect.artificial_intelligence.pgqenn.growth_law import CanonicalPrimeGrowth
from the_nothingness_effect.artificial_intelligence.pgqenn.mpl_tc_dependency import (
    MPLTCMotifProvider,
    MPLTCPrefix,
)
from the_nothingness_effect.artificial_intelligence.qenn.model import QENNModel
from the_nothingness_effect.artificial_intelligence.multimodal import (
    TNETrainableMultimodalModel,
    make_synthetic_multimodal_dataset,
)
from the_nothingness_effect.artificial_intelligence.soinets.multimodal import (
    TNEMultimodalSOInet,
)


class _MotifRemovedProvider:
    def __init__(self) -> None:
        self._canonical = MPLTCMotifProvider()

    def prefix(self, count: int) -> MPLTCPrefix:
        source = self._canonical.prefix(count)
        return MPLTCPrefix(
            source.primes,
            source.gaps,
            tuple("U1" for _ in source.motifs),
            tuple(1 for _ in source.motif_runs),
        )

    def triadic_streams(self, count: int):
        return self._canonical.triadic_streams(count)


def test_removing_dtqc_changes_qenn_hidden_lattice():
    torch.manual_seed(12)
    canonical = QENNModel(5, 7, 3)
    ablation = QENNModel(5, 7, 3, dtqc_enabled=False)
    ablation.load_state_dict(
        {key: value for key, value in canonical.state_dict().items() if not key.startswith("dtqc.")},
        strict=True,
    )
    features = torch.rand(9, 5) + 0.25

    canonical_output = canonical(features)
    ablation_output = ablation(features)

    assert canonical_output.dtqc_state is not None
    assert ablation_output.dtqc_state is None
    assert canonical_output.metadata["dtqc_integration"] == "canonical_runtime"
    assert ablation_output.metadata["dtqc_integration"] == "source_removal_ablation"
    assert not torch.allclose(canonical_output.hidden, ablation_output.hidden)


def test_removing_observation_collapse_removes_definite_outcome_projection():
    torch.manual_seed(19)
    canonical = QENNModel(4, 6, 3)
    ablation = QENNModel(4, 6, 3, observation_collapse_enabled=False)
    ablation.load_state_dict(canonical.state_dict(), strict=True)
    features = torch.rand(8, 4) + 0.25

    canonical_output = canonical(features)
    ablation_output = ablation(features)

    assert canonical_output.observation_collapse_state is not None
    assert ablation_output.observation_collapse_state is None
    assert canonical_output.metadata["observation_collapse_integration"] == "canonical_runtime"
    assert ablation_output.metadata["observation_collapse_integration"] == "source_removal_ablation"
    assert not torch.allclose(canonical_output.observation, ablation_output.observation)


def test_removing_elastic_dubler_changes_qenn_feature_bridge():
    torch.manual_seed(29)
    canonical = QENNModel(5, 7, 3)
    ablation = QENNModel(5, 7, 3, elastic_dubler_enabled=False)
    ablation.load_state_dict(
        {
            key: value
            for key, value in canonical.state_dict().items()
            if not key.startswith("elastic_dubler.")
        },
        strict=True,
    )
    features = torch.tensor(
        [
            [0.3, 0.7, 1.1, 0.4, 1.6],
            [1.2, 0.5, 0.9, 1.8, 0.6],
            [0.4, 1.5, 0.8, 0.7, 1.3],
        ]
    )

    canonical_output = canonical(features)
    ablation_output = ablation(features)

    assert canonical_output.elastic_dubler_state is not None
    assert ablation_output.elastic_dubler_state is None
    assert canonical_output.metadata["elastic_dubler_integration"] == "feature_weight_window_bridge"
    assert ablation_output.metadata["elastic_dubler_integration"] == "source_removal_ablation"
    assert not torch.allclose(canonical_output.hidden, ablation_output.hidden)


def test_removing_mpl_tc_motifs_changes_pgqenn_graph_law():
    canonical = CanonicalPrimeGrowth().build(12)
    removed = CanonicalPrimeGrowth(provider=_MotifRemovedProvider()).build(12)

    assert canonical.primes == removed.primes
    assert canonical.motifs != removed.motifs
    assert not torch.equal(canonical.adjacency, removed.adjacency)


def test_removing_three_additional_tc_streams_changes_pgqenn_messages():
    from the_nothingness_effect.artificial_intelligence.pgqenn.model import PGQENNModel

    torch.manual_seed(41)
    model = PGQENNModel(5, 7, 3)
    features = torch.rand(11, 5) + 0.2
    complete = model(features)
    model.triadic_streams_enabled = False
    prime_only = model(features)

    assert complete.graph.triadic_growth.stream_counts["pure_even_lift"] == 6
    assert complete.graph.triadic_growth.stream_counts["first_order_odd"] == 10
    assert all(
        count > 0 for count in complete.graph.triadic_growth.stream_counts.values()
    )
    assert float(complete.triadic_stream_source_removal_delta.detach()) > 0.0
    assert not torch.allclose(complete.node_state, prime_only.node_state)
    assert prime_only.metadata["triadic_stream_integration"] == "source_removal_ablation"


def test_removing_multimodal_dubler_changes_named_domain_fusion():
    torch.manual_seed(31)
    canonical = TNEMultimodalSOInet(5, 7, 3)
    ablation = TNEMultimodalSOInet(5, 7, 3, elastic_dubler_enabled=False)
    ablation.load_state_dict(
        {
            key: value
            for key, value in canonical.state_dict().items()
            if not key.startswith("elastic_dubler.")
        },
        strict=True,
    )
    modalities = {
        "color": torch.tensor(
            [[0.9, 0.1, 0.2], [0.1, 0.8, 0.2], [0.2, 0.1, 0.9]]
        ),
        "sound": torch.arange(36, dtype=torch.float32).reshape(3, 1, 12) / 10.0 + 0.1,
    }

    canonical_output = canonical(modalities)
    ablation_output = ablation(modalities)

    assert canonical_output.elastic_dubler_state is not None
    assert ablation_output.elastic_dubler_state is None
    assert canonical_output.metadata["elastic_dubler_integration"] == "named_modality_domain_bridge"
    assert ablation_output.metadata["elastic_dubler_integration"] == "source_removal_ablation"
    assert not torch.allclose(canonical_output.fused_state, ablation_output.fused_state)


def test_axis_rbm_and_cluster_sources_each_change_trainable_multimodal_hidden_state():
    torch.manual_seed(37)
    dataset = make_synthetic_multimodal_dataset(samples_per_class=5, seed=37)
    model = TNETrainableMultimodalModel(hidden_dim=8)
    model.eval()
    complete = model(dataset.test.modalities).hidden

    variants = (
        ("axis_network_enabled", False),
        ("energy_regulation_enabled", False),
        ("cluster_context_enabled", False),
    )
    for attribute, removed in variants:
        setattr(model, attribute, removed)
        ablated = model(dataset.test.modalities).hidden
        setattr(model, attribute, True)
        assert not torch.allclose(complete, ablated), attribute
