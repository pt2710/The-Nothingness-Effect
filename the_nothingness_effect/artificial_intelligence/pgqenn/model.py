"""Differentiable canonical PGQENN model."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.shared.closure_losses import (
    arbitrate,
    parseval_residual,
)
from the_nothingness_effect.artificial_intelligence.shared.elastic_pi_gates import (
    ElasticPiGate,
)
from the_nothingness_effect.artificial_intelligence.shared.entropy_gates import (
    parity_conditioned_dfi,
)
from the_nothingness_effect.artificial_intelligence.shared.observation_collapse import (
    ObservationCollapseReadout,
    ObservationCollapseState,
)
from the_nothingness_effect.artificial_intelligence.shared.provenance import (
    backend_metadata,
)
from the_nothingness_effect.artificial_intelligence.shared.types import (
    TNEAIOutput,
    require_finite_tensor,
)
from the_nothingness_effect.artificial_intelligence.qenn.model import (
    QENNModel,
    QENNOutput,
)

from .growth_law import CanonicalPrimeGrowth, PrimeGraph
from .message_passing import PrimeEquivariantMessagePassing
from .mpl_tc_dependency import MPLTCDependencyError, MPLTCMotifProvider


def _mpl_tc_motif_capacity(provider: MPLTCMotifProvider) -> int:
    """Return the pinned finite MPL-TC motif capacity without changing it."""

    module = provider._load()
    law_class = getattr(module, "McCracknsPrimeLaw", None)
    if law_class is None:
        raise MPLTCDependencyError(
            "pinned MPL-TC checkout does not expose McCracknsPrimeLaw"
        )
    capacity = int(law_class.max_supported_primes())
    if capacity < 2:
        raise MPLTCDependencyError(
            "pinned MPL-TC runtime must support at least two motifs"
        )
    return capacity


def _compress_feature_nodes(
    features: torch.Tensor,
    capacity: int,
) -> tuple[torch.Tensor, tuple[int, ...]]:
    """Mean-pool every source row into at most ``capacity`` graph nodes.

    The deterministic contiguous partition is differentiable and uses every
    input row exactly once. It bounds only the finite MPL-TC graph carrier;
    it does not subsample or discard the tabular training observations.
    """

    if features.ndim != 2:
        raise ValueError("PGQENN graph compression requires a rank-2 feature field")
    if capacity < 2:
        raise ValueError("PGQENN graph compression capacity must be at least two")
    node_count = int(features.shape[0])
    if node_count < 2:
        raise ValueError("PGQENN requires at least two feature nodes")
    if node_count <= capacity:
        return features, (1,) * node_count

    quotient, remainder = divmod(node_count, capacity)
    pooled: list[torch.Tensor] = []
    bucket_sizes: list[int] = []
    start = 0
    for index in range(capacity):
        size = quotient + (1 if index < remainder else 0)
        stop = start + size
        pooled.append(features[start:stop].mean(dim=0))
        bucket_sizes.append(size)
        start = stop
    if start != node_count or sum(bucket_sizes) != node_count:
        raise RuntimeError("PGQENN graph compression did not consume every source row")
    return torch.stack(pooled, dim=0), tuple(bucket_sizes)


@dataclass
class PGQENNOutput(TNEAIOutput):
    graph: PrimeGraph | None = None
    pdfi: torch.Tensor | None = None
    node_state: torch.Tensor | None = None
    qenn_backbone_output: QENNOutput | None = None
    mpl_motifs: tuple[str, ...] = ()
    observation_collapse_state: ObservationCollapseState | None = None
    triadic_stream_source_removal_delta: torch.Tensor | None = None
    signed_spectrum_source_removal_delta: torch.Tensor | None = None


class PGQENNModel(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        *,
        K_D: float = 1.0,
        soi_scale: float = 1.0,
        motif_width: int = 2,
        mpl_tc_repository: str | Path | None = None,
        qenn_dtqc_enabled: bool = True,
        triadic_streams_enabled: bool = True,
        signed_spectrum_enabled: bool = True,
    ):
        super().__init__()
        if min(input_dim, hidden_dim, output_dim) <= 0:
            raise ValueError("PGQENN dimensions must be positive")
        self.qenn_backbone = QENNModel(
            input_dim,
            hidden_dim,
            hidden_dim,
            K_D=K_D,
            soi_scale=soi_scale,
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
        self.triadic_streams_enabled = bool(triadic_streams_enabled)
        self.signed_spectrum_enabled = bool(signed_spectrum_enabled)

    def forward(
        self,
        features: torch.Tensor,
        graph: PrimeGraph | None = None,
        *,
        tolerance: float = 1e-5,
    ) -> PGQENNOutput:
        require_finite_tensor(features, "PGQENN input")
        if (
            features.ndim != 2
            or features.shape[1]
            != self.qenn_backbone.equivariant.linear.in_features
        ):
            raise ValueError("PGQENN input must have shape [nodes, input_dim]")

        input_node_count = int(features.shape[0])
        motif_capacity = input_node_count
        bucket_sizes: tuple[int, ...] = (1,) * input_node_count
        graph_features = features
        reduction = "explicit_graph"
        if graph is None:
            motif_capacity = _mpl_tc_motif_capacity(self.growth.provider)
            graph_features, bucket_sizes = _compress_feature_nodes(
                features,
                motif_capacity,
            )
            reduction = (
                "contiguous_mean_pool_all_rows"
                if graph_features.shape[0] < features.shape[0]
                else "identity"
            )
            graph = self.growth.build(
                graph_features.shape[0],
                dtype=features.dtype,
            )
        elif graph.adjacency.shape[0] != input_node_count:
            raise ValueError(
                "an explicit PGQENN graph must match the feature-node count"
            )

        qenn_output = self.qenn_backbone(graph_features, tolerance=tolerance)
        hidden = self.message_passing(
            qenn_output.hidden,
            graph,
            use_triadic_streams=self.triadic_streams_enabled,
            use_signed_spectrum=self.signed_spectrum_enabled,
        )
        positive_spectrum_hidden = self.message_passing(
            qenn_output.hidden,
            graph,
            use_triadic_streams=self.triadic_streams_enabled,
            use_signed_spectrum=False,
        )
        prime_only_hidden = self.message_passing(
            qenn_output.hidden,
            graph,
            use_triadic_streams=False,
        )
        triadic_stream_delta = torch.linalg.vector_norm(hidden - prime_only_hidden)
        signed_spectrum_delta = torch.linalg.vector_norm(
            hidden - positive_spectrum_hidden
        )
        dfi = qenn_output.dfi
        adjacency = graph.adjacency.to(
            dtype=graph_features.dtype,
            device=graph_features.device,
        )
        spatial_adjacency = graph.message_adjacency.to(
            dtype=graph_features.dtype,
            device=graph_features.device,
        )
        coordinates = graph.coordinates_3d.to(
            dtype=graph_features.dtype,
            device=graph_features.device,
        )
        degree_sequence = adjacency.sum(dim=-1) + 1.0
        parity_mask = torch.tensor(
            [
                (index + graph.two_adic_depths[index].value) % 2
                for index in range(len(graph.primes) - 1)
            ],
            dtype=graph_features.dtype,
            device=graph_features.device,
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
        triadic = graph.triadic_growth
        signed_triadic = graph.signed_triadic_growth
        triadic_symmetry = (
            torch.linalg.vector_norm(
                triadic.spatial_adjacency - triadic.spatial_adjacency.T
            ).to(dtype=graph_features.dtype, device=graph_features.device)
            if triadic is not None
            else torch.zeros(
                (),
                dtype=graph_features.dtype,
                device=graph_features.device,
            )
        )
        residuals = {
            "message_equivariance": self.message_passing.equivariance_residual(
                qenn_output.hidden,
                graph,
                use_triadic_streams=self.triadic_streams_enabled,
                use_signed_spectrum=self.signed_spectrum_enabled,
            ),
            "graph_symmetry": torch.linalg.vector_norm(adjacency - adjacency.T),
            "self_loop": torch.linalg.vector_norm(torch.diagonal(adjacency)),
            "growth_3d_spatial_symmetry": torch.linalg.vector_norm(
                spatial_adjacency - spatial_adjacency.T
            ),
            "growth_3d_axis_rank": torch.relu(
                torch.tensor(
                    3.0,
                    dtype=graph_features.dtype,
                    device=graph_features.device,
                )
                - torch.linalg.matrix_rank(
                    coordinates - coordinates.mean(dim=0, keepdim=True)
                ).to(dtype=graph_features.dtype)
            ),
            "triadic_stream_adjacency_symmetry": triadic_symmetry,
            "signed_spectrum_value_involution": torch.tensor(
                signed_triadic.value_involution_residual
                if signed_triadic is not None
                else 0.0,
                dtype=graph_features.dtype,
                device=graph_features.device,
            ),
            "parseval": parseval_residual(node_state),
            "qenn_backbone_completeness": torch.stack(
                tuple(qenn_output.residuals.values())
            ).sum(),
            "mpl_tc_dependency": torch.zeros(
                (),
                dtype=graph_features.dtype,
                device=graph_features.device,
            ),
            "mpl_tc_motif_exhaustion": torch.tensor(
                abs(len(graph.motifs) - graph_features.shape[0]),
                dtype=graph_features.dtype,
                device=graph_features.device,
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
            "growth_geometry": "prime_shell_x_mpl_tc_motif_x_two_adic_run_depth",
            "growth_axis_labels": graph.axis_labels,
            "message_adjacency": (
                "canonical_edges_localized_by_3d_growth_geometry"
            ),
            "input_node_count": input_node_count,
            "graph_node_count": int(graph_features.shape[0]),
            "mpl_tc_motif_capacity": motif_capacity,
            "mpl_tc_capacity_reduction": reduction,
            "mpl_tc_pool_bucket_count": len(bucket_sizes),
            "mpl_tc_pool_bucket_min": min(bucket_sizes),
            "mpl_tc_pool_bucket_max": max(bucket_sizes),
            "mpl_tc_source_rows_consumed": sum(bucket_sizes),
            "triadic_stream_integration": (
                "experimental_finite_prefix_structural_bridge"
                if self.triadic_streams_enabled
                else "source_removal_ablation"
            ),
            "triadic_stream_counts": (
                triadic.stream_counts if triadic is not None else {}
            ),
            "triadic_stream_types": (
                "pure_even_lift",
                "first_order_odd",
                "lpf_odd_composite",
                "mixed_even_composite",
            ),
            "triadic_stream_source_removal_delta": float(
                triadic_stream_delta.detach().cpu()
            ),
            "signed_spectrum_integration": (
                "tne_flowpoint_involution_lift"
                if self.signed_spectrum_enabled
                else "positive_spectrum_ablation"
            ),
            "signed_spectrum_counts": (
                signed_triadic.spectrum_counts
                if signed_triadic is not None
                else {}
            ),
            "signed_spectrum_source_removal_delta": float(
                signed_spectrum_delta.detach().cpu()
            ),
            "signed_spectrum_coordinate_asymmetry": (
                signed_triadic.coordinate_asymmetry
                if signed_triadic is not None
                else 0.0
            ),
            "negative_spectrum_authority": (
                "TNE Flowpoint neural lift; MPL-TC provenance is positive-only"
            ),
            "triadic_modality_semantics": (
                "TC stream kind is a structural growth axis; modality remains "
                "the node feature field"
            ),
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
            triadic_stream_source_removal_delta=triadic_stream_delta,
            signed_spectrum_source_removal_delta=signed_spectrum_delta,
        )
