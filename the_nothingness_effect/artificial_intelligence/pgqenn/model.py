"""Differentiable canonical PGQENN model."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

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


def _mpl_tc_finite_prefix_capacity(provider: MPLTCMotifProvider) -> int:
    """Return the verified finite-prefix length exposed by pinned MPL-TC code.

    This is an execution-tape length, not a PGQENN node limit and not a bound on
    the unbounded MPL theory. Larger carriers are covered by multiple verified
    finite-prefix graph segments without pooling or dropping source nodes.
    """

    module = provider._load()
    law_class = getattr(module, "McCracknsPrimeLaw", None)
    if law_class is None:
        raise MPLTCDependencyError(
            "pinned MPL-TC checkout does not expose McCracknsPrimeLaw"
        )
    capacity = int(law_class.max_supported_primes())
    if capacity < 3:
        raise MPLTCDependencyError(
            "pinned MPL-TC runtime must support at least three motifs"
        )
    return capacity


def _finite_prefix_segment_sizes(
    node_count: int,
    finite_prefix_capacity: int,
) -> tuple[int, ...]:
    """Partition all nodes into valid finite-prefix segments without loss."""

    if node_count < 2:
        raise ValueError("PGQENN requires at least two feature nodes")
    if finite_prefix_capacity < 3:
        raise ValueError("MPL-TC finite-prefix capacity must be at least three")
    if node_count <= finite_prefix_capacity:
        return (node_count,)

    full_segments, remainder = divmod(node_count, finite_prefix_capacity)
    sizes = [finite_prefix_capacity] * full_segments
    if remainder == 1:
        sizes[-1] -= 1
        sizes.append(2)
    elif remainder > 1:
        sizes.append(remainder)
    if any(size < 2 or size > finite_prefix_capacity for size in sizes):
        raise RuntimeError("invalid PGQENN finite-prefix graph segmentation")
    if sum(sizes) != node_count:
        raise RuntimeError("PGQENN graph segmentation did not preserve every node")
    return tuple(sizes)


def _sum_counts(rows: tuple[dict[str, int], ...]) -> dict[str, int]:
    result: dict[str, int] = {}
    for row in rows:
        for name, value in row.items():
            result[name] = result.get(name, 0) + int(value)
    return result


@dataclass
class PGQENNOutput(TNEAIOutput):
    graph: PrimeGraph | None = None
    graph_shards: tuple[PrimeGraph, ...] = ()
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

    def _segment_forward(
        self,
        qenn_hidden: torch.Tensor,
        qenn_readout: torch.Tensor,
        qenn_dfi: torch.Tensor,
        graph: PrimeGraph,
    ) -> dict[str, Any]:
        hidden = self.message_passing(
            qenn_hidden,
            graph,
            use_triadic_streams=self.triadic_streams_enabled,
            use_signed_spectrum=self.signed_spectrum_enabled,
        )
        positive_spectrum_hidden = self.message_passing(
            qenn_hidden,
            graph,
            use_triadic_streams=self.triadic_streams_enabled,
            use_signed_spectrum=False,
        )
        prime_only_hidden = self.message_passing(
            qenn_hidden,
            graph,
            use_triadic_streams=False,
        )
        triadic_delta = torch.linalg.vector_norm(hidden - prime_only_hidden)
        signed_delta = torch.linalg.vector_norm(hidden - positive_spectrum_hidden)

        adjacency = graph.adjacency.to(
            dtype=qenn_hidden.dtype,
            device=qenn_hidden.device,
        )
        spatial_adjacency = graph.message_adjacency.to(
            dtype=qenn_hidden.dtype,
            device=qenn_hidden.device,
        )
        coordinates = graph.coordinates_3d.to(
            dtype=qenn_hidden.dtype,
            device=qenn_hidden.device,
        )
        degree_sequence = adjacency.sum(dim=-1) + 1.0
        parity_mask = torch.tensor(
            [
                (index + graph.two_adic_depths[index].value) % 2
                for index in range(len(graph.primes) - 1)
            ],
            dtype=qenn_hidden.dtype,
            device=qenn_hidden.device,
        )
        pdfi = parity_conditioned_dfi(degree_sequence, parity_mask)
        elastic = self.elastic_gate(qenn_dfi.abs() + pdfi)
        gain = torch.mean(elastic / torch.pi, dim=-1, keepdim=True)
        node_state = require_finite_tensor(
            0.5 * (hidden * gain + qenn_readout),
            "PGQENN QENN-composed gated state",
        )
        logits = self.readout_layer(node_state.mean(dim=0, keepdim=True))

        triadic = graph.triadic_growth
        signed_triadic = graph.signed_triadic_growth
        triadic_symmetry = (
            torch.linalg.vector_norm(
                triadic.spatial_adjacency - triadic.spatial_adjacency.T
            ).to(dtype=qenn_hidden.dtype, device=qenn_hidden.device)
            if triadic is not None
            else torch.zeros((), dtype=qenn_hidden.dtype, device=qenn_hidden.device)
        )
        residuals = {
            "message_equivariance": self.message_passing.equivariance_residual(
                qenn_hidden,
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
                torch.tensor(3.0, dtype=qenn_hidden.dtype, device=qenn_hidden.device)
                - torch.linalg.matrix_rank(
                    coordinates - coordinates.mean(dim=0, keepdim=True)
                ).to(dtype=qenn_hidden.dtype)
            ),
            "triadic_stream_adjacency_symmetry": triadic_symmetry,
            "signed_spectrum_value_involution": torch.tensor(
                signed_triadic.value_involution_residual
                if signed_triadic is not None
                else 0.0,
                dtype=qenn_hidden.dtype,
                device=qenn_hidden.device,
            ),
            "parseval": parseval_residual(node_state),
            "mpl_tc_dependency": torch.zeros(
                (), dtype=qenn_hidden.dtype, device=qenn_hidden.device
            ),
            "mpl_tc_motif_exhaustion": torch.tensor(
                abs(len(graph.motifs) - qenn_hidden.shape[0]),
                dtype=qenn_hidden.dtype,
                device=qenn_hidden.device,
            ),
        }
        return {
            "node_state": node_state,
            "elastic": elastic,
            "pdfi": pdfi,
            "logits": logits,
            "triadic_delta": triadic_delta,
            "signed_delta": signed_delta,
            "residuals": residuals,
        }

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

        node_count = int(features.shape[0])
        qenn_output = self.qenn_backbone(features, tolerance=tolerance)
        finite_capacity = node_count
        segmentation = "explicit_graph"
        if graph is not None:
            if graph.adjacency.shape[0] != node_count:
                raise ValueError(
                    "an explicit PGQENN graph must match the feature-node count"
                )
            segment_sizes = (node_count,)
            graphs = (graph,)
        else:
            finite_capacity = _mpl_tc_finite_prefix_capacity(self.growth.provider)
            segment_sizes = _finite_prefix_segment_sizes(node_count, finite_capacity)
            segmentation = (
                "identity_single_finite_prefix"
                if len(segment_sizes) == 1
                else "lossless_block_diagonal_finite_prefix_cover"
            )
            graph_cache: dict[int, PrimeGraph] = {}
            graph_rows: list[PrimeGraph] = []
            for size in segment_sizes:
                if size not in graph_cache:
                    graph_cache[size] = self.growth.build(size, dtype=features.dtype)
                graph_rows.append(graph_cache[size])
            graphs = tuple(graph_rows)

        segment_outputs: list[dict[str, Any]] = []
        start = 0
        for size, segment_graph in zip(segment_sizes, graphs, strict=True):
            stop = start + size
            segment_outputs.append(
                self._segment_forward(
                    qenn_output.hidden[start:stop],
                    qenn_output.readout[start:stop],
                    qenn_output.dfi[start:stop],
                    segment_graph,
                )
            )
            start = stop
        if start != node_count:
            raise RuntimeError("PGQENN graph segments did not consume every node")

        node_state = torch.cat(
            [row["node_state"] for row in segment_outputs], dim=0
        )
        elastic = torch.cat([row["elastic"] for row in segment_outputs], dim=0)
        weights = torch.tensor(
            segment_sizes,
            dtype=features.dtype,
            device=features.device,
        ) / float(node_count)
        logits = torch.sum(
            torch.cat([row["logits"] for row in segment_outputs], dim=0)
            * weights.unsqueeze(-1),
            dim=0,
            keepdim=True,
        )
        pdfi = torch.sum(
            torch.stack([row["pdfi"] for row in segment_outputs]) * weights
        )
        observation_state = self.observation_collapse(logits)
        observation = observation_state.probabilities

        graph_residual_names = tuple(segment_outputs[0]["residuals"])
        residuals = {
            name: torch.stack(
                [row["residuals"][name] for row in segment_outputs]
            ).max()
            for name in graph_residual_names
        }
        residuals["parseval"] = parseval_residual(node_state)
        residuals["qenn_backbone_completeness"] = torch.stack(
            tuple(qenn_output.residuals.values())
        ).sum()
        residuals.update(observation_state.residuals)
        status = arbitrate(residuals, tolerance)

        triadic_delta = torch.linalg.vector_norm(
            torch.stack([row["triadic_delta"] for row in segment_outputs])
        )
        signed_delta = torch.linalg.vector_norm(
            torch.stack([row["signed_delta"] for row in segment_outputs])
        )
        triadic_counts = _sum_counts(
            tuple(
                segment_graph.triadic_growth.stream_counts
                if segment_graph.triadic_growth is not None
                else {}
                for segment_graph in graphs
            )
        )
        signed_counts = _sum_counts(
            tuple(
                segment_graph.signed_triadic_growth.spectrum_counts
                if segment_graph.signed_triadic_growth is not None
                else {}
                for segment_graph in graphs
            )
        )
        coordinate_asymmetry = max(
            (
                segment_graph.signed_triadic_growth.coordinate_asymmetry
                if segment_graph.signed_triadic_growth is not None
                else 0.0
            )
            for segment_graph in graphs
        )
        first_graph = graphs[0]
        metadata = {
            **backend_metadata(),
            "architecture": "PGQENN",
            "architecture_base": "QENN",
            "qenn_dtqc_integration": qenn_output.metadata["dtqc_integration"],
            "qenn_observation_collapse_integration": qenn_output.metadata[
                "observation_collapse_integration"
            ],
            "observation_collapse_integration": "canonical_runtime",
            "growth_mode": (
                first_graph.growth_mode
                if len(graphs) == 1
                else "segmented_mpl_tc_prime_motif"
            ),
            "growth_geometry": "prime_shell_x_mpl_tc_motif_x_two_adic_run_depth",
            "growth_axis_labels": first_graph.axis_labels,
            "message_adjacency": (
                "block_diagonal_canonical_edges_localized_by_3d_growth_geometry"
                if len(graphs) > 1
                else "canonical_edges_localized_by_3d_growth_geometry"
            ),
            "input_node_count": node_count,
            "graph_node_count": node_count,
            "graph_segment_count": len(segment_sizes),
            "graph_segment_sizes": segment_sizes,
            "mpl_tc_finite_prefix_capacity": finite_capacity,
            "mpl_tc_node_limit": None,
            "mpl_tc_segmentation": segmentation,
            "mpl_tc_source_nodes_consumed": sum(segment_sizes),
            "mpl_tc_pooling": "none",
            "mpl_tc_unbounded_theory_claim": False,
            "triadic_stream_integration": (
                "experimental_finite_prefix_structural_bridge"
                if self.triadic_streams_enabled
                else "source_removal_ablation"
            ),
            "triadic_stream_counts": triadic_counts,
            "triadic_stream_types": (
                "pure_even_lift",
                "first_order_odd",
                "lpf_odd_composite",
                "mixed_even_composite",
            ),
            "triadic_stream_source_removal_delta": float(
                triadic_delta.detach().cpu()
            ),
            "signed_spectrum_integration": (
                "tne_flowpoint_involution_lift"
                if self.signed_spectrum_enabled
                else "positive_spectrum_ablation"
            ),
            "signed_spectrum_counts": signed_counts,
            "signed_spectrum_source_removal_delta": float(
                signed_delta.detach().cpu()
            ),
            "signed_spectrum_coordinate_asymmetry": coordinate_asymmetry,
            "negative_spectrum_authority": (
                "TNE Flowpoint neural lift; MPL-TC provenance is positive-only"
            ),
            "triadic_modality_semantics": (
                "TC stream kind is a structural growth axis; modality remains "
                "the node feature field"
            ),
            "mpl_tc_repository": first_graph.dependency_url,
            "mpl_tc_commit": first_graph.dependency_commit,
            "mpl_tc_module_sha256": first_graph.dependency_sha256,
        }
        return PGQENNOutput(
            hidden=node_state,
            readout=logits,
            observation=observation,
            dfi=qenn_output.dfi,
            elastic_gain=elastic,
            residuals=residuals,
            closure_status=status,
            metadata=metadata,
            graph=first_graph,
            graph_shards=graphs,
            pdfi=pdfi,
            node_state=node_state,
            qenn_backbone_output=qenn_output,
            mpl_motifs=tuple(
                motif for segment_graph in graphs for motif in segment_graph.motifs
            ),
            observation_collapse_state=observation_state,
            triadic_stream_source_removal_delta=triadic_delta,
            signed_spectrum_source_removal_delta=signed_delta,
        )
