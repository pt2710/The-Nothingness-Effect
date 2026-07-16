"""Static and animated evidence from PGQENN's executable 3D growth graph."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np

from the_nothingness_effect._runtime.artifacts.io import (
    save_csv,
    save_figure,
    write_metadata,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import (
    git_commit,
    parameter_hash,
)

from .growth_law import (
    CanonicalPrimeGrowth,
    PrimeGraph,
    SignedTriadicGrowthGraph,
    TriadicGrowthGraph,
)


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"
_STREAM_COLORS = {
    "pure_even_lift": "#4c78a8",
    "first_order_odd": "#59a14f",
    "lpf_odd_composite": "#f28e2b",
    "mixed_even_composite": "#e15759",
}


def _edge_rows(graph: PrimeGraph) -> list[dict[str, Any]]:
    coordinates = graph.coordinates_3d.detach().cpu().numpy()
    adjacency = graph.adjacency.detach().cpu().numpy()
    spatial = graph.spatial_adjacency.detach().cpu().numpy()
    rows: list[dict[str, Any]] = []
    for source in range(len(graph.primes)):
        for target in range(source + 1, len(graph.primes)):
            if adjacency[source, target] <= 0.0:
                continue
            rows.append(
                {
                    "source_index": source,
                    "target_index": target,
                    "source_prime": graph.primes[source],
                    "target_prime": graph.primes[target],
                    "canonical_weight": float(adjacency[source, target]),
                    "spatial_weight": float(spatial[source, target]),
                    "distance_3d": float(
                        np.linalg.norm(coordinates[source] - coordinates[target])
                    ),
                }
            )
    return rows


def _draw_graph(
    axis: Any,
    graph: PrimeGraph,
    *,
    visible: int,
    title: str,
    activation: np.ndarray | None = None,
    azimuth: float = -55.0,
) -> None:
    coordinates = graph.coordinates_3d.detach().cpu().numpy()
    adjacency = graph.spatial_adjacency.detach().cpu().numpy()
    visible = min(max(1, int(visible)), len(graph.primes))
    for source in range(visible):
        for target in range(source + 1, visible):
            weight = adjacency[source, target]
            if weight <= 0.0:
                continue
            axis.plot(
                coordinates[[source, target], 0],
                coordinates[[source, target], 1],
                coordinates[[source, target], 2],
                color="#667788",
                alpha=min(0.85, 0.18 + 1.3 * float(weight)),
                linewidth=0.6 + 3.0 * float(weight),
            )
    values = (
        np.asarray(activation[:visible], dtype=float)
        if activation is not None
        else np.asarray(
            [depth.value for depth in graph.two_adic_depths[:visible]], dtype=float
        )
    )
    sizes = 45.0 + 4.0 * np.sqrt(np.asarray(graph.primes[:visible], dtype=float))
    scatter = axis.scatter(
        coordinates[:visible, 0],
        coordinates[:visible, 1],
        coordinates[:visible, 2],
        c=values,
        cmap="viridis" if activation is None else "plasma",
        s=sizes,
        edgecolors="black",
        linewidths=0.45,
        vmin=float(np.min(values)) if values.size else 0.0,
        vmax=float(np.max(values)) + 1e-9 if values.size else 1.0,
    )
    for index in range(visible):
        axis.text(
            coordinates[index, 0],
            coordinates[index, 1],
            coordinates[index, 2] + 0.045,
            str(graph.primes[index]),
            fontsize=6,
            ha="center",
        )
    axis.set(
        title=title,
        xlabel="prime shell",
        ylabel="MPL-TC motif",
        zlabel="2-adic + run depth",
        xlim=(-1.15, 1.15),
        ylim=(-1.15, 1.15),
        zlim=(-1.15, 1.15),
    )
    axis.view_init(elev=23.0, azim=azimuth)
    return scatter


def _matrix_indices(graph: PrimeGraph, bins: int) -> np.ndarray:
    coordinates = graph.coordinates_3d.detach().cpu().numpy()
    normalized = np.clip((coordinates + 1.0) * 0.5, 0.0, 1.0)
    return np.rint(normalized * (bins - 1)).astype(int)


def _occupancy(graph: PrimeGraph, bins: int, visible: int | None = None) -> np.ndarray:
    occupancy = np.zeros((bins, bins, bins), dtype=float)
    indices = _matrix_indices(graph, bins)
    count = len(indices) if visible is None else min(visible, len(indices))
    for index, (x_axis, y_axis, z_axis) in enumerate(indices[:count]):
        occupancy[x_axis, y_axis, z_axis] += 1.0 + 0.1 * graph.two_adic_depths[index].value
    return occupancy


def _save_3d_movie(path: Path, frames: int, update: Any) -> Path:
    figure = plt.figure(figsize=(7.0, 5.8), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")

    def render(frame: int):
        axis.clear()
        update(frame, axis)
        return ()

    movie = animation.FuncAnimation(figure, render, frames=frames, interval=350)
    movie.save(path, writer=animation.PillowWriter(fps=3))
    plt.close(figure)
    return path


def _draw_triadic_graph(
    axis: Any,
    graph: TriadicGrowthGraph,
    *,
    visible: int,
    title: str,
    activation: np.ndarray | None = None,
    azimuth: float = -55.0,
) -> None:
    coordinates = graph.coordinates_3d.detach().cpu().numpy()
    adjacency = graph.spatial_adjacency.detach().cpu().numpy()
    visible = min(max(1, int(visible)), len(graph.values))
    for source in range(visible):
        for target in range(source + 1, visible):
            weight = adjacency[source, target]
            if weight <= 0.0:
                continue
            axis.plot(
                coordinates[[source, target], 0],
                coordinates[[source, target], 1],
                coordinates[[source, target], 2],
                color="#7a7a7a",
                alpha=min(0.42, 0.08 + 0.7 * float(weight)),
                linewidth=0.3 + 1.4 * float(weight),
            )
    if activation is None:
        colors = [_STREAM_COLORS[kind] for kind in graph.stream_kinds[:visible]]
        sizes = 24.0 + 2.2 * np.sqrt(np.asarray(graph.values[:visible], dtype=float))
        axis.scatter(
            coordinates[:visible, 0],
            coordinates[:visible, 1],
            coordinates[:visible, 2],
            c=colors,
            s=sizes,
            edgecolors="black",
            linewidths=0.25,
            alpha=0.92,
        )
    else:
        values = np.asarray(activation[:visible], dtype=float)
        axis.scatter(
            coordinates[:visible, 0],
            coordinates[:visible, 1],
            coordinates[:visible, 2],
            c=values,
            cmap="plasma",
            vmin=0.0,
            vmax=max(float(values.max()), 1e-9),
            s=36,
            edgecolors="black",
            linewidths=0.25,
        )
    axis.set(
        title=title,
        xlabel="number magnitude",
        ylabel="TC stream kind",
        zlabel="axis depth",
        xlim=(-1.15, 1.15),
        ylim=(-1.15, 1.15),
        zlim=(-1.15, 1.15),
    )
    axis.view_init(elev=24.0, azim=azimuth)


def _triadic_matrix(graph: TriadicGrowthGraph, bins: int) -> tuple[np.ndarray, np.ndarray]:
    coordinates = graph.coordinates_3d.detach().cpu().numpy()
    indices = np.rint(np.clip((coordinates + 1.0) * 0.5, 0.0, 1.0) * (bins - 1)).astype(int)
    counts = np.zeros((bins, bins, bins, 4), dtype=float)
    for index, coordinate in enumerate(indices):
        stream = (
            "pure_even_lift",
            "first_order_odd",
            "lpf_odd_composite",
            "mixed_even_composite",
        ).index(graph.stream_kinds[index])
        counts[coordinate[0], coordinate[1], coordinate[2], stream] += 1.0
    return counts.sum(axis=-1), counts.argmax(axis=-1)


def _draw_signed_graph(
    axis: Any,
    graph: SignedTriadicGrowthGraph,
    *,
    visible_pairs: int,
    title: str,
    activation: np.ndarray | None = None,
    azimuth: float = -58.0,
) -> None:
    coordinates = graph.coordinates_3d.detach().cpu().numpy()
    adjacency = graph.spatial_adjacency.detach().cpu().numpy()
    pair_count = min(max(1, int(visible_pairs)), graph.positive_node_count)
    visible = tuple(range(pair_count)) + tuple(
        range(graph.positive_node_count, graph.positive_node_count + pair_count)
    )
    visible_set = set(visible)
    for source in visible:
        for target in range(source + 1, len(graph.values)):
            if target not in visible_set or adjacency[source, target] <= 0.0:
                continue
            cross = graph.spectrum_signs[source] != graph.spectrum_signs[target]
            axis.plot(
                coordinates[[source, target], 0],
                coordinates[[source, target], 1],
                coordinates[[source, target], 2],
                color="#8e63b6" if cross else "#6f7782",
                alpha=0.36 if cross else 0.16,
                linewidth=1.0 if cross else 0.42,
            )
    for sign, marker, label in ((1, "o", "positive"), (-1, "^", "negative")):
        indices = [index for index in visible if graph.spectrum_signs[index] == sign]
        if activation is None:
            colors = [_STREAM_COLORS[graph.stream_kinds[index]] for index in indices]
        else:
            values = np.asarray([activation[index] for index in indices], dtype=float)
            colors = plt.cm.plasma(values / max(float(np.max(activation)), 1e-9))
        axis.scatter(
            coordinates[indices, 0],
            coordinates[indices, 1],
            coordinates[indices, 2],
            c=colors,
            marker=marker,
            s=28 if sign > 0 else 34,
            edgecolors="black",
            linewidths=0.22,
            alpha=0.9,
            label=f"{label} spectrum",
        )
    axis.set(
        title=title,
        xlabel="signed number spectrum",
        ylabel="TC stream kind",
        zlabel="asymmetric structural depth",
        xlim=(-1.15, 1.15),
        ylim=(-1.25, 1.25),
        zlim=(-1.2, 1.2),
    )
    axis.view_init(elev=23.0, azim=azimuth)


def _signed_edge_rows(graph: SignedTriadicGrowthGraph) -> list[dict[str, Any]]:
    adjacency = graph.spatial_adjacency.detach().cpu().numpy()
    rows: list[dict[str, Any]] = []
    for source in range(len(graph.values)):
        for target in range(source + 1, len(graph.values)):
            if adjacency[source, target] <= 0.0:
                continue
            rows.append(
                {
                    "source_index": source,
                    "target_index": target,
                    "source_value": graph.values[source],
                    "target_value": graph.values[target],
                    "source_spectrum": "positive"
                    if graph.spectrum_signs[source] > 0
                    else "negative",
                    "target_spectrum": "positive"
                    if graph.spectrum_signs[target] > 0
                    else "negative",
                    "source_stream": graph.stream_kinds[source],
                    "target_stream": graph.stream_kinds[target],
                    "spatial_weight": float(adjacency[source, target]),
                }
            )
    return rows


def generate_pgqenn_growth_3d_artifacts(
    output_dir: str | Path,
    *,
    seed: int,
    simulation: bool,
    node_count: int | None = None,
) -> dict[str, Any]:
    """Generate matrices, projections and movies from the actual growth law."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    mode = "simulation" if simulation else "test"
    count = int(node_count or (24 if simulation else 18))
    if count < 10:
        raise ValueError("3D PGQENN growth artifacts require at least ten nodes")
    graph = CanonicalPrimeGrowth().build(count)
    prefix = f"pgqenn_{mode}_network_3d"
    coordinates = graph.coordinates_3d.detach().cpu().numpy()
    raw_adjacency = graph.adjacency.detach().cpu().numpy()
    spatial_adjacency = graph.spatial_adjacency.detach().cpu().numpy()
    bins = 6

    figures: list[Path] = []
    figure = plt.figure(figsize=(8.4, 6.8), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    _draw_graph(
        axis,
        graph,
        visible=count,
        title="PGQENN canonical 3D prime/motif growth",
    )
    figures.append(save_figure(figure, output / f"{prefix}_growth.png", dpi=180))
    plt.close(figure)

    occupancy = _occupancy(graph, bins)
    figure = plt.figure(figsize=(8.0, 6.5), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    filled = occupancy > 0.0
    colors = plt.cm.viridis(occupancy / max(float(occupancy.max()), 1.0))
    colors[..., 3] = np.where(filled, 0.88, 0.0)
    axis.voxels(filled, facecolors=colors, edgecolor="#333333", linewidth=0.35)
    axis.set(
        title="PGQENN 3D growth-matrix occupancy",
        xlabel="prime-shell bin",
        ylabel="motif bin",
        zlabel="2-adic/run bin",
    )
    figures.append(
        save_figure(figure, output / f"{prefix}_matrix_occupancy.png", dpi=180)
    )
    plt.close(figure)

    figure, axes = plt.subplots(1, 3, figsize=(13.5, 4.4), constrained_layout=True)
    projections = ((0, 1, "prime × motif"), (0, 2, "prime × depth"), (1, 2, "motif × depth"))
    depth_colors = np.asarray([item.value for item in graph.two_adic_depths])
    for axis, (x_axis, y_axis, title) in zip(axes, projections, strict=True):
        axis.scatter(
            coordinates[:, x_axis], coordinates[:, y_axis], c=depth_colors,
            cmap="viridis", s=55, edgecolors="black", linewidths=0.35,
        )
        axis.set(title=title, xlabel=graph.axis_labels[x_axis], ylabel=graph.axis_labels[y_axis])
        axis.grid(alpha=0.25)
    figures.append(
        save_figure(figure, output / f"{prefix}_axis_projections.png", dpi=175)
    )
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(11.5, 5.0), constrained_layout=True)
    first = axes[0].imshow(raw_adjacency, cmap="magma")
    axes[0].set(title="Canonical prime/motif adjacency", xlabel="node", ylabel="node")
    figure.colorbar(first, ax=axes[0], shrink=0.8)
    second = axes[1].imshow(spatial_adjacency, cmap="magma")
    axes[1].set(title="3D-localized message adjacency", xlabel="node", ylabel="node")
    figure.colorbar(second, ax=axes[1], shrink=0.8)
    figures.append(
        save_figure(figure, output / f"{prefix}_locality_adjacency.png", dpi=175)
    )
    plt.close(figure)

    node_table = save_csv(
        output / f"{prefix}_nodes.csv",
        [
            {
                "node_index": index,
                "prime": graph.primes[index],
                "motif": graph.motifs[index],
                "motif_run": graph.motif_runs[index],
                "two_adic_depth": graph.two_adic_depths[index].value,
                "prime_shell_x": float(coordinates[index, 0]),
                "mpl_tc_motif_y": float(coordinates[index, 1]),
                "two_adic_run_depth_z": float(coordinates[index, 2]),
                "canonical_degree": float(raw_adjacency[index].sum()),
                "spatial_degree": float(spatial_adjacency[index].sum()),
            }
            for index in range(count)
        ],
    )
    edge_table = save_csv(output / f"{prefix}_edges.csv", _edge_rows(graph))

    triadic = graph.triadic_growth
    if triadic is None:
        raise RuntimeError("canonical PGQENN graph did not expose its four-stream bridge")
    figure = plt.figure(figsize=(9.0, 7.0), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    _draw_triadic_graph(
        axis,
        triadic,
        visible=len(triadic.values),
        title="MPL-TC four-stream heterogeneous PGQENN growth",
    )
    for kind, color in _STREAM_COLORS.items():
        axis.scatter([], [], [], color=color, label=kind.replace("_", " "))
    axis.legend(loc="upper left", fontsize=7)
    figures.append(
        save_figure(figure, output / f"{prefix}_triadic_stream_growth.png", dpi=180)
    )
    plt.close(figure)

    triadic_occupancy, dominant_stream = _triadic_matrix(triadic, 7)
    figure = plt.figure(figsize=(8.2, 6.5), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    filled = triadic_occupancy > 0.0
    palette = np.asarray(
        [matplotlib.colors.to_rgba(color) for color in _STREAM_COLORS.values()]
    )
    facecolors = palette[dominant_stream]
    facecolors[..., 3] = np.where(filled, 0.86, 0.0)
    axis.voxels(filled, facecolors=facecolors, edgecolor="#333333", linewidth=0.25)
    axis.set(
        title="Four-stream PGQENN 3D matrix",
        xlabel="number magnitude bin",
        ylabel="stream bin",
        zlabel="axis-depth bin",
    )
    figures.append(
        save_figure(figure, output / f"{prefix}_triadic_stream_matrix.png", dpi=180)
    )
    plt.close(figure)

    triadic_node_table = save_csv(
        output / f"{prefix}_triadic_stream_nodes.csv",
        [
            {
                "node_index": index,
                "value": triadic.values[index],
                "stream_kind": triadic.stream_kinds[index],
                "domain": triadic.domains[index],
                "axis": triadic.axes[index],
                "dyadic_depth": triadic.dyadic_depths[index],
                "least_prime_factor": triadic.least_prime_factors[index],
                "cofactor": triadic.cofactors[index],
                "source_prime_index": triadic.source_prime_indices[index],
                "x_number_magnitude": float(triadic.coordinates_3d[index, 0]),
                "y_stream_kind": float(triadic.coordinates_3d[index, 1]),
                "z_axis_depth": float(triadic.coordinates_3d[index, 2]),
            }
            for index in range(len(triadic.values))
        ],
    )
    triadic_adjacency = triadic.spatial_adjacency.detach().cpu().numpy()
    triadic_edge_table = save_csv(
        output / f"{prefix}_triadic_stream_edges.csv",
        [
            {
                "source_index": source,
                "target_index": target,
                "source_value": triadic.values[source],
                "target_value": triadic.values[target],
                "source_stream": triadic.stream_kinds[source],
                "target_stream": triadic.stream_kinds[target],
                "spatial_weight": float(triadic_adjacency[source, target]),
            }
            for source in range(len(triadic.values))
            for target in range(source + 1, len(triadic.values))
            if triadic_adjacency[source, target] > 0.0
        ],
    )

    signed = graph.signed_triadic_growth
    if signed is None:
        raise RuntimeError("canonical PGQENN graph did not expose its signed lift")
    figure = plt.figure(figsize=(10.0, 7.2), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    _draw_signed_graph(
        axis,
        signed,
        visible_pairs=signed.positive_node_count,
        title="PGQENN simultaneous positive/negative Flowpoint growth",
    )
    axis.legend(loc="upper left", fontsize=8)
    figures.append(
        save_figure(
            figure, output / f"{prefix}_signed_spectrum_growth.png", dpi=180
        )
    )
    plt.close(figure)

    signed_adjacency = signed.spatial_adjacency.detach().cpu().numpy()
    split = signed.positive_node_count
    figure, axes = plt.subplots(1, 3, figsize=(14.0, 4.5), constrained_layout=True)
    signed_blocks = (
        (signed_adjacency[:split, :split], "positive MPL-TC block"),
        (signed_adjacency[split:, split:], "negative TNE lift block"),
        (signed_adjacency[:split, split:], "Flowpoint cross-spectrum bridge"),
    )
    for axis, (matrix, title) in zip(axes, signed_blocks, strict=True):
        image = axis.imshow(matrix, cmap="magma", aspect="auto")
        axis.set(title=title, xlabel="node", ylabel="node")
        figure.colorbar(image, ax=axis, shrink=0.78)
    figures.append(
        save_figure(
            figure, output / f"{prefix}_signed_spectrum_adjacency.png", dpi=175
        )
    )
    plt.close(figure)

    signed_coordinates = signed.coordinates_3d.detach().cpu().numpy()
    figure, axes = plt.subplots(1, 3, figsize=(13.6, 4.4), constrained_layout=True)
    sign_colors = np.where(np.asarray(signed.spectrum_signs) > 0, 1.0, -1.0)
    for axis, (x_axis, y_axis, title) in zip(
        axes,
        (
            (0, 1, "spectrum × stream"),
            (0, 2, "spectrum × structural depth"),
            (1, 2, "stream × structural depth"),
        ),
        strict=True,
    ):
        axis.scatter(
            signed_coordinates[:, x_axis],
            signed_coordinates[:, y_axis],
            c=sign_colors,
            cmap="coolwarm",
            vmin=-1.0,
            vmax=1.0,
            s=22,
            edgecolors="black",
            linewidths=0.18,
        )
        axis.set(
            title=title,
            xlabel=signed.axis_labels[x_axis],
            ylabel=signed.axis_labels[y_axis],
        )
        axis.grid(alpha=0.22)
    figures.append(
        save_figure(
            figure, output / f"{prefix}_signed_spectrum_projections.png", dpi=175
        )
    )
    plt.close(figure)

    signed_node_table = save_csv(
        output / f"{prefix}_signed_spectrum_nodes.csv",
        [
            {
                "node_index": index,
                "value": signed.values[index],
                "spectrum": "positive"
                if signed.spectrum_signs[index] > 0
                else "negative",
                "stream_kind": signed.stream_kinds[index],
                "source_prime_index": signed.source_prime_indices[index],
                "involution_partner_index": signed.involution_partner_indices[index],
                "x_signed_spectrum": float(signed_coordinates[index, 0]),
                "y_stream_kind": float(signed_coordinates[index, 1]),
                "z_structural_depth": float(signed_coordinates[index, 2]),
            }
            for index in range(len(signed.values))
        ],
    )
    signed_edge_table = save_csv(
        output / f"{prefix}_signed_spectrum_edges.csv",
        _signed_edge_rows(signed),
    )

    growth_movie = _save_3d_movie(
        output / f"{prefix}_growth.gif",
        count,
        lambda frame, axis: _draw_graph(
            axis,
            graph,
            visible=frame + 1,
            title=f"PGQENN 3D growth — {frame + 1}/{count} nodes",
            azimuth=-58.0 + 1.5 * frame,
        ),
    )

    def matrix_frame(frame: int, axis: Any) -> None:
        values = _occupancy(graph, bins, frame + 1)
        filled_frame = values > 0.0
        colors_frame = plt.cm.plasma(values / max(float(values.max()), 1.0))
        colors_frame[..., 3] = np.where(filled_frame, 0.9, 0.0)
        axis.voxels(
            filled_frame, facecolors=colors_frame, edgecolor="#333333", linewidth=0.3
        )
        axis.set(
            title=f"3D matrix growth — {frame + 1}/{count} nodes",
            xlabel="prime shell",
            ylabel="motif",
            zlabel="2-adic/run depth",
        )
        axis.view_init(elev=24.0, azim=-50.0 + 1.2 * frame)

    matrix_movie = _save_3d_movie(
        output / f"{prefix}_matrix_growth.gif", count, matrix_frame
    )

    normalized = spatial_adjacency / np.maximum(
        spatial_adjacency.sum(axis=1, keepdims=True), 1e-12
    )
    signal_states = [np.eye(count, dtype=float)[0]]
    for _ in range(13):
        propagated = normalized @ signal_states[-1]
        signal_states.append(0.35 * signal_states[-1] + 0.65 * propagated)

    signal_movie = _save_3d_movie(
        output / f"{prefix}_signal_propagation.gif",
        len(signal_states),
        lambda frame, axis: _draw_graph(
            axis,
            graph,
            visible=count,
            activation=np.asarray(signal_states[frame]),
            title=f"3D message propagation — step {frame + 1}/{len(signal_states)}",
            azimuth=-55.0 + 2.0 * frame,
        ),
    )
    triadic_frame_count = 24 if simulation else 18
    triadic_growth_movie = _save_3d_movie(
        output / f"{prefix}_triadic_stream_growth.gif",
        triadic_frame_count,
        lambda frame, axis: _draw_triadic_graph(
            axis,
            triadic,
            visible=int(np.ceil((frame + 1) * len(triadic.values) / triadic_frame_count)),
            title=(
                "Four-stream PGQENN growth — "
                f"step {frame + 1}/{triadic_frame_count}"
            ),
            azimuth=-58.0 + 1.8 * frame,
        ),
    )
    triadic_normalized = triadic_adjacency / np.maximum(
        triadic_adjacency.sum(axis=1, keepdims=True), 1e-12
    )
    triadic_signal_states = [np.eye(len(triadic.values), dtype=float)[0]]
    for _ in range(13):
        propagated = triadic_normalized @ triadic_signal_states[-1]
        triadic_signal_states.append(
            0.30 * triadic_signal_states[-1] + 0.70 * propagated
        )
    triadic_signal_movie = _save_3d_movie(
        output / f"{prefix}_triadic_stream_signal.gif",
        len(triadic_signal_states),
        lambda frame, axis: _draw_triadic_graph(
            axis,
            triadic,
            visible=len(triadic.values),
            activation=triadic_signal_states[frame],
            title=(
                "Four-stream message propagation — "
                f"step {frame + 1}/{len(triadic_signal_states)}"
            ),
            azimuth=-55.0 + 2.0 * frame,
        ),
    )
    signed_frame_count = 24 if simulation else 18
    signed_growth_movie = _save_3d_movie(
        output / f"{prefix}_signed_spectrum_growth.gif",
        signed_frame_count,
        lambda frame, axis: _draw_signed_graph(
            axis,
            signed,
            visible_pairs=int(
                np.ceil(
                    (frame + 1)
                    * signed.positive_node_count
                    / signed_frame_count
                )
            ),
            title=(
                "Simultaneous signed-spectrum growth — "
                f"step {frame + 1}/{signed_frame_count}"
            ),
            azimuth=-60.0 + 1.7 * frame,
        ),
    )
    signed_normalized = signed_adjacency / np.maximum(
        signed_adjacency.sum(axis=1, keepdims=True), 1e-12
    )
    signed_initial = np.zeros(len(signed.values), dtype=float)
    signed_initial[0] = 1.0
    signed_initial[signed.involution_partner_indices[0]] = 1.0
    signed_signal_states = [signed_initial]
    for _ in range(13):
        propagated = signed_normalized @ signed_signal_states[-1]
        signed_signal_states.append(
            0.28 * signed_signal_states[-1] + 0.72 * propagated
        )
    signed_signal_movie = _save_3d_movie(
        output / f"{prefix}_signed_spectrum_signal.gif",
        len(signed_signal_states),
        lambda frame, axis: _draw_signed_graph(
            axis,
            signed,
            visible_pairs=signed.positive_node_count,
            activation=signed_signal_states[frame],
            title=(
                "Signed Flowpoint message propagation — "
                f"step {frame + 1}/{len(signed_signal_states)}"
            ),
            azimuth=-56.0 + 2.0 * frame,
        ),
    )
    movies = [
        growth_movie,
        matrix_movie,
        signal_movie,
        triadic_growth_movie,
        triadic_signal_movie,
        signed_growth_movie,
        signed_signal_movie,
    ]
    tables = [
        node_table,
        edge_table,
        triadic_node_table,
        triadic_edge_table,
        signed_node_table,
        signed_edge_table,
    ]
    parameters = {
        "architecture": "PGQENN",
        "mode": mode,
        "seed": seed,
        "node_count": count,
        "matrix_bins": bins,
        "axis_labels": list(graph.axis_labels),
        "growth_mode": graph.growth_mode,
        "mpl_tc_commit": graph.dependency_commit,
        "triadic_stream_counts": triadic.stream_counts,
        "triadic_finite_limit": triadic.finite_limit,
        "triadic_module_sha256": triadic.dependency_sha256,
        "triadic_bridge_status": "experimental_finite_prefix_structural_bridge",
        "signed_spectrum_counts": signed.spectrum_counts,
        "signed_value_involution_residual": signed.value_involution_residual,
        "signed_coordinate_asymmetry": signed.coordinate_asymmetry,
        "negative_spectrum_authority": (
            "TNE Flowpoint neural lift; MPL-TC remains positive-only"
        ),
    }
    generated = [path.name for path in (*figures, *tables, *movies)]
    manifest = write_metadata(
        output / f"{prefix}_growth_manifest.json",
        {
            "architecture": "PGQENN",
            "artifact_family": "executable_3d_growth_matrix",
            "repository_start_commit": START_COMMIT,
            "repository_result_commit": git_commit(Path(__file__).resolve().parents[3]),
            "parameters": parameters,
            "parameter_hash": parameter_hash(parameters),
            "seed": seed,
            "generated_files": generated,
            "regeneration_command": (
                "python -m the_nothingness_effect.artificial_intelligence.pgqenn."
                f"{mode}.run_all_capabilities"
            ),
            "source_status": (
                "verified positive MPL-TC growth plus TNE Flowpoint signed lift"
            ),
            "claim_boundary": "finite computational support; not a formal proof substitute",
        },
    )
    return {
        "graph": graph,
        "figures": figures,
        "tables": tables,
        "animations": movies,
        "manifest": manifest,
    }
