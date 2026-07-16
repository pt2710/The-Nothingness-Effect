"""Architecture-owned 3D evidence derived from actual runtime tensors."""

from __future__ import annotations

from dataclasses import dataclass
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
from the_nothingness_effect.artificial_intelligence.shared.runtime_state import (
    ArchitectureRuntimeState,
)


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


@dataclass(frozen=True)
class SpatialProfile:
    title: str
    axis_labels: tuple[str, str, str]
    signed_meaning: str


_PROFILES = {
    "qenn": SpatialProfile(
        "QENN runtime Flowpoint/DTQC state",
        ("runtime component 1", "runtime component 2", "runtime component 3"),
        "canonical positive/negative Flowpoint orientation",
    ),
    "soinets": SpatialProfile(
        "SOInet runtime subnetwork/meta-closure state",
        ("subnetwork state", "transfer state", "meta-closure state"),
        "forward/reverse closure orientation",
    ),
    "multimodal": SpatialProfile(
        "Multimodal runtime modality/cluster state",
        ("modality state", "cluster state", "SOInet state"),
        "positive/negative carrier orientation",
    ),
}


def _resample(value: np.ndarray, size: int) -> np.ndarray:
    vector = np.asarray(value, dtype=float).reshape(-1)
    if vector.size == size:
        return vector
    if vector.size == 1:
        return np.repeat(vector, size)
    return np.interp(
        np.linspace(0.0, 1.0, size),
        np.linspace(0.0, 1.0, vector.size),
        vector,
    )


def _draw_graph(
    axis: Any,
    coordinates: np.ndarray,
    adjacency: np.ndarray,
    streams: tuple[str, ...],
    *,
    visible: int,
    title: str,
    axis_labels: tuple[str, str, str],
    activation: np.ndarray | None = None,
    azimuth: float = -58.0,
) -> None:
    visible = min(max(int(visible), 1), len(coordinates))
    for source in range(visible):
        for target in range(source + 1, visible):
            weight = float(adjacency[source, target])
            if weight <= 0.0:
                continue
            axis.plot(
                coordinates[[source, target], 0],
                coordinates[[source, target], 1],
                coordinates[[source, target], 2],
                alpha=min(0.72, 0.08 + weight),
                linewidth=0.35 + 2.2 * weight,
            )
    if activation is None:
        unique = tuple(dict.fromkeys(streams))
        colors = [unique.index(stream) for stream in streams[:visible]]
    else:
        values = np.asarray(activation[:visible], dtype=float)
        maximum = max(float(np.max(values)), 1e-9)
        colors = values / maximum
    axis.scatter(
        coordinates[:visible, 0],
        coordinates[:visible, 1],
        coordinates[:visible, 2],
        c=colors,
        cmap="plasma",
        s=38,
        edgecolors="black",
        linewidths=0.25,
    )
    axis.set(
        title=title,
        xlabel=axis_labels[0],
        ylabel=axis_labels[1],
        zlabel=axis_labels[2],
        xlim=(-1.15, 1.15),
        ylim=(-1.15, 1.15),
        zlim=(-1.15, 1.15),
    )
    axis.view_init(elev=23.0, azim=azimuth)


def _draw_signed(
    axis: Any,
    coordinates: np.ndarray,
    adjacency: np.ndarray,
    *,
    pair_count: int,
    visible_pairs: int,
    title: str,
    axis_labels: tuple[str, str, str],
    activation: np.ndarray | None = None,
    azimuth: float = -60.0,
) -> None:
    visible_pairs = min(max(int(visible_pairs), 1), pair_count)
    visible = tuple(range(visible_pairs)) + tuple(
        range(pair_count, pair_count + visible_pairs)
    )
    visible_set = set(visible)
    for source in visible:
        for target in range(source + 1, len(coordinates)):
            weight = float(adjacency[source, target])
            if target not in visible_set or weight <= 0.0:
                continue
            cross = (source < pair_count) != (target < pair_count)
            axis.plot(
                coordinates[[source, target], 0],
                coordinates[[source, target], 1],
                coordinates[[source, target], 2],
                alpha=0.45 if cross else min(0.35, 0.05 + weight),
                linewidth=1.0 if cross else 0.4 + weight,
            )
    for sign, offset, marker, label in (
        (1, 0, "o", "positive/forward"),
        (-1, pair_count, "^", "negative/reverse"),
    ):
        indices = np.arange(offset, offset + visible_pairs)
        values = (
            np.full(visible_pairs, float(sign))
            if activation is None
            else np.asarray(activation[indices], dtype=float)
        )
        axis.scatter(
            coordinates[indices, 0],
            coordinates[indices, 1],
            coordinates[indices, 2],
            c=values,
            cmap="coolwarm",
            marker=marker,
            s=34,
            edgecolors="black",
            linewidths=0.22,
            label=label,
        )
    axis.set(
        title=title,
        xlabel=f"signed {axis_labels[0]}",
        ylabel=axis_labels[1],
        zlabel=axis_labels[2],
        xlim=(-1.15, 1.15),
        ylim=(-1.15, 1.15),
        zlim=(-1.15, 1.15),
    )
    axis.view_init(elev=23.0, azim=azimuth)


def _movie(path: Path, frames: int, update: Any) -> Path:
    figure = plt.figure(figsize=(7.0, 5.8), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")

    def render(frame: int):
        axis.clear()
        update(frame, axis)
        return ()

    result = animation.FuncAnimation(figure, render, frames=frames, interval=330)
    result.save(path, writer=animation.PillowWriter(fps=3))
    plt.close(figure)
    return path


def _occupancy(
    coordinates: np.ndarray, bins: int, visible: int | None = None
) -> np.ndarray:
    indices = np.rint(
        np.clip((coordinates + 1.0) * 0.5, 0.0, 1.0) * (bins - 1)
    ).astype(int)
    values = np.zeros((bins, bins, bins), dtype=float)
    count = len(indices) if visible is None else min(int(visible), len(indices))
    for index in indices[:count]:
        values[tuple(index)] += 1.0
    return values


def generate_spatial_state_artifacts(
    architecture: str,
    output_dir: str | Path,
    *,
    runtime_state: ArchitectureRuntimeState,
    seed: int,
    simulation: bool,
) -> dict[str, object]:
    """Generate 3D evidence exclusively from the supplied runtime snapshot."""

    if architecture not in _PROFILES:
        raise ValueError(f"no 3D spatial-state profile for {architecture!r}")
    if runtime_state.architecture != architecture:
        raise ValueError("runtime-state architecture does not match spatial producer")
    profile = _PROFILES[architecture]
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    mode = "simulation" if simulation else "test"
    coordinates = np.asarray(runtime_state.coordinates, dtype=float)
    adjacency = np.asarray(runtime_state.adjacency, dtype=float)
    streams = tuple(runtime_state.streams)
    signed_coordinates = np.asarray(runtime_state.signed_coordinates, dtype=float)
    signed_adjacency = np.asarray(runtime_state.signed_adjacency, dtype=float)
    partner = np.asarray(runtime_state.partner, dtype=int)
    count = len(coordinates)
    if count < 2 or adjacency.shape != (count, count):
        raise ValueError("runtime spatial state requires at least two aligned nodes")
    if len(streams) != count:
        streams = tuple(streams[index % len(streams)] for index in range(count))
    trace = np.stack(
        [_resample(row, count) for row in runtime_state.activation_trace]
    )
    prefix = f"{architecture}_{mode}_network_3d"
    bins = 6
    figures: list[Path] = []
    movies: list[Path] = []

    figure = plt.figure(figsize=(8.4, 6.8), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    _draw_graph(
        axis,
        coordinates,
        adjacency,
        streams,
        visible=count,
        title=profile.title,
        axis_labels=profile.axis_labels,
        activation=trace[-1],
    )
    figures.append(save_figure(figure, output / f"{prefix}_growth.png", dpi=180))
    plt.close(figure)

    occupancy = _occupancy(coordinates, bins)
    figure = plt.figure(figsize=(8.0, 6.5), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    filled = occupancy > 0.0
    colors = plt.cm.viridis(occupancy / max(float(occupancy.max()), 1.0))
    colors[..., 3] = np.where(filled, 0.88, 0.0)
    axis.voxels(filled, facecolors=colors, edgecolor="#333333", linewidth=0.3)
    axis.set(title=f"{profile.title} — runtime occupancy")
    figures.append(
        save_figure(figure, output / f"{prefix}_matrix_occupancy.png", dpi=180)
    )
    plt.close(figure)

    figure, axes = plt.subplots(1, 3, figsize=(13.5, 4.4), constrained_layout=True)
    stream_names = tuple(dict.fromkeys(streams))
    stream_index = np.asarray([stream_names.index(stream) for stream in streams])
    for axis, (x_axis, y_axis) in zip(
        axes, ((0, 1), (0, 2), (1, 2)), strict=True
    ):
        axis.scatter(
            coordinates[:, x_axis],
            coordinates[:, y_axis],
            c=stream_index,
            cmap="tab10",
            s=50,
            edgecolors="black",
            linewidths=0.25,
        )
        axis.set(
            xlabel=profile.axis_labels[x_axis], ylabel=profile.axis_labels[y_axis]
        )
        axis.grid(alpha=0.22)
    figures.append(
        save_figure(figure, output / f"{prefix}_axis_projections.png", dpi=175)
    )
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(11.2, 5.0), constrained_layout=True)
    covariance = np.abs(coordinates @ coordinates.T)
    np.fill_diagonal(covariance, 0.0)
    for axis, matrix, title in (
        (axes[0], covariance, "runtime coordinate covariance"),
        (axes[1], adjacency, "runtime model adjacency"),
    ):
        image = axis.imshow(matrix, cmap="magma")
        axis.set(title=title, xlabel="state", ylabel="state")
        figure.colorbar(image, ax=axis, shrink=0.8)
    figures.append(
        save_figure(figure, output / f"{prefix}_locality_adjacency.png", dpi=175)
    )
    plt.close(figure)

    figure = plt.figure(figsize=(9.0, 7.0), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    _draw_graph(
        axis,
        coordinates,
        adjacency,
        streams,
        visible=count,
        title=f"{architecture.upper()} runtime source-state growth",
        axis_labels=profile.axis_labels,
        activation=trace[-1],
    )
    figures.append(
        save_figure(figure, output / f"{prefix}_source_stream_growth.png", dpi=180)
    )
    plt.close(figure)

    stream_counts = np.zeros((bins, bins, bins, max(len(stream_names), 1)))
    indices = np.rint(
        np.clip((coordinates + 1.0) * 0.5, 0.0, 1.0) * (bins - 1)
    ).astype(int)
    for index, coordinate in enumerate(indices):
        stream_counts[tuple(coordinate) + (stream_index[index],)] += 1.0
    figure = plt.figure(figsize=(8.1, 6.5), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    filled = stream_counts.sum(axis=-1) > 0.0
    dominant = stream_counts.argmax(axis=-1)
    facecolors = plt.cm.tab10(dominant / max(len(stream_names) - 1, 1))
    facecolors[..., 3] = np.where(filled, 0.86, 0.0)
    axis.voxels(filled, facecolors=facecolors, edgecolor="#333333", linewidth=0.25)
    axis.set(title=f"{architecture.upper()} runtime source-state matrix")
    figures.append(
        save_figure(figure, output / f"{prefix}_source_stream_matrix.png", dpi=180)
    )
    plt.close(figure)

    figure = plt.figure(figsize=(9.5, 7.0), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    _draw_signed(
        axis,
        signed_coordinates,
        signed_adjacency,
        pair_count=count,
        visible_pairs=count,
        title=f"{architecture.upper()} runtime signed-state lift",
        axis_labels=profile.axis_labels,
    )
    axis.legend(loc="upper left", fontsize=8)
    figures.append(
        save_figure(figure, output / f"{prefix}_signed_spectrum_growth.png", dpi=180)
    )
    plt.close(figure)

    figure, axes = plt.subplots(1, 3, figsize=(14.0, 4.5), constrained_layout=True)
    for axis, matrix, title in (
        (axes[0], signed_adjacency[:count, :count], "positive/forward block"),
        (axes[1], signed_adjacency[count:, count:], "negative/reverse block"),
        (axes[2], signed_adjacency[:count, count:], "Flowpoint partner bridge"),
    ):
        image = axis.imshow(matrix, cmap="magma", aspect="auto")
        axis.set(title=title, xlabel="state", ylabel="state")
        figure.colorbar(image, ax=axis, shrink=0.78)
    figures.append(
        save_figure(
            figure, output / f"{prefix}_signed_spectrum_adjacency.png", dpi=175
        )
    )
    plt.close(figure)

    figure, axes = plt.subplots(1, 3, figsize=(13.5, 4.4), constrained_layout=True)
    sign = np.concatenate((np.ones(count), -np.ones(count)))
    for axis, (x_axis, y_axis) in zip(
        axes, ((0, 1), (0, 2), (1, 2)), strict=True
    ):
        axis.scatter(
            signed_coordinates[:, x_axis],
            signed_coordinates[:, y_axis],
            c=sign,
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
            s=25,
            edgecolors="black",
            linewidths=0.2,
        )
        axis.set(
            xlabel=profile.axis_labels[x_axis], ylabel=profile.axis_labels[y_axis]
        )
        axis.grid(alpha=0.22)
    figures.append(
        save_figure(
            figure, output / f"{prefix}_signed_spectrum_projections.png", dpi=175
        )
    )
    plt.close(figure)

    node_table = save_csv(
        output / f"{prefix}_nodes.csv",
        [
            {
                "node_index": index,
                "stream": streams[index],
                "x": float(coordinates[index, 0]),
                "y": float(coordinates[index, 1]),
                "z": float(coordinates[index, 2]),
                "degree": float(adjacency[index].sum()),
                "state_source": "runtime_output_tensor",
            }
            for index in range(count)
        ],
    )
    edge_table = save_csv(
        output / f"{prefix}_edges.csv",
        [
            {"source": source, "target": target, "weight": float(adjacency[source, target])}
            for source in range(count)
            for target in range(source + 1, count)
            if adjacency[source, target] > 0.0
        ],
    )
    signed_node_table = save_csv(
        output / f"{prefix}_signed_spectrum_nodes.csv",
        [
            {
                "node_index": index,
                "orientation": "positive" if index < count else "negative",
                "partner_index": int(partner[index]),
                "stream": streams[index % count],
                "x": float(signed_coordinates[index, 0]),
                "y": float(signed_coordinates[index, 1]),
                "z": float(signed_coordinates[index, 2]),
            }
            for index in range(2 * count)
        ],
    )
    signed_edge_table = save_csv(
        output / f"{prefix}_signed_spectrum_edges.csv",
        [
            {
                "source": source,
                "target": target,
                "weight": float(signed_adjacency[source, target]),
            }
            for source in range(2 * count)
            for target in range(source + 1, 2 * count)
            if signed_adjacency[source, target] > 0.0
        ],
    )

    movies.append(
        _movie(
            output / f"{prefix}_growth.gif",
            count,
            lambda frame, axis: _draw_graph(
                axis,
                coordinates,
                adjacency,
                streams,
                visible=frame + 1,
                title=f"{profile.title} — {frame + 1}/{count}",
                axis_labels=profile.axis_labels,
                activation=trace[min(frame, len(trace) - 1)],
                azimuth=-58 + 1.5 * frame,
            ),
        )
    )

    def matrix_frame(frame: int, axis: Any) -> None:
        visible = int(np.ceil((frame + 1) * count / max(len(trace), 1)))
        values = _occupancy(coordinates, bins, visible)
        occupied = values > 0.0
        colors_frame = plt.cm.plasma(values / max(float(values.max()), 1.0))
        colors_frame[..., 3] = np.where(occupied, 0.9, 0.0)
        axis.voxels(
            occupied, facecolors=colors_frame, edgecolor="#333333", linewidth=0.25
        )
        axis.set(title=f"Runtime 3D matrix — frame {frame + 1}/{len(trace)}")

    movies.append(
        _movie(output / f"{prefix}_matrix_growth.gif", len(trace), matrix_frame)
    )
    movies.append(
        _movie(
            output / f"{prefix}_signal_propagation.gif",
            len(trace),
            lambda frame, axis: _draw_graph(
                axis,
                coordinates,
                adjacency,
                streams,
                visible=count,
                title=f"Runtime state trace — {frame + 1}/{len(trace)}",
                axis_labels=profile.axis_labels,
                activation=trace[frame],
                azimuth=-55 + 2 * frame,
            ),
        )
    )
    movies.append(
        _movie(
            output / f"{prefix}_source_stream_growth.gif",
            count,
            lambda frame, axis: _draw_graph(
                axis,
                coordinates,
                adjacency,
                streams,
                visible=frame + 1,
                title=f"Runtime source-state exposure — {frame + 1}/{count}",
                axis_labels=profile.axis_labels,
                activation=trace[min(frame, len(trace) - 1)],
                azimuth=-58 + 1.8 * frame,
            ),
        )
    )
    movies.append(
        _movie(
            output / f"{prefix}_source_stream_signal.gif",
            len(trace),
            lambda frame, axis: _draw_graph(
                axis,
                coordinates,
                adjacency,
                streams,
                visible=count,
                title=f"Runtime source-state signal — {frame + 1}/{len(trace)}",
                axis_labels=profile.axis_labels,
                activation=trace[frame],
                azimuth=-54 + 2 * frame,
            ),
        )
    )
    signed_frames = max(10, count)
    movies.append(
        _movie(
            output / f"{prefix}_signed_spectrum_growth.gif",
            signed_frames,
            lambda frame, axis: _draw_signed(
                axis,
                signed_coordinates,
                signed_adjacency,
                pair_count=count,
                visible_pairs=int(np.ceil((frame + 1) * count / signed_frames)),
                title=f"Runtime signed-state lift — {frame + 1}/{signed_frames}",
                axis_labels=profile.axis_labels,
                azimuth=-60 + 1.7 * frame,
            ),
        )
    )
    signed_trace = np.concatenate((trace, trace), axis=1)
    movies.append(
        _movie(
            output / f"{prefix}_signed_spectrum_signal.gif",
            len(signed_trace),
            lambda frame, axis: _draw_signed(
                axis,
                signed_coordinates,
                signed_adjacency,
                pair_count=count,
                visible_pairs=count,
                title=f"Runtime signed-state signal — {frame + 1}/{len(signed_trace)}",
                axis_labels=profile.axis_labels,
                activation=signed_trace[frame],
                azimuth=-56 + 2 * frame,
            ),
        )
    )

    tables = [node_table, edge_table, signed_node_table, signed_edge_table]
    partner_residual = int(
        np.max(np.abs(partner[partner] - np.arange(2 * count)))
    )
    parameters = {
        "architecture": architecture,
        "mode": mode,
        "seed": seed,
        "node_count": count,
        "axis_labels": list(profile.axis_labels),
        "source_streams": list(dict.fromkeys(streams)),
        "signed_meaning": profile.signed_meaning,
        "partner_involution_residual": partner_residual,
        "coordinate_asymmetry": float(
            np.linalg.norm(signed_coordinates[count:] + coordinates)
        ),
        "state_source": runtime_state.source_status,
    }
    generated = [path.name for path in (*figures, *tables, *movies)]
    manifest = write_metadata(
        output / f"{prefix}_growth_manifest.json",
        {
            "architecture": architecture,
            "artifact_family": "architecture_specific_3d_growth_matrix",
            "repository_start_commit": START_COMMIT,
            "repository_result_commit": git_commit(Path(__file__).resolve().parents[3]),
            "parameters": parameters,
            "parameter_hash": parameter_hash(parameters),
            "seed": seed,
            "generated_files": generated,
            "regeneration_command": (
                "python -m the_nothingness_effect.artificial_intelligence."
                f"{architecture}.{mode}.run_all_capabilities"
            ),
            "source_status": "runtime_derived_spatial_state",
            "claim_boundary": "finite observed model state; not a formal proof substitute",
        },
    )
    return {
        "figures": figures,
        "tables": tables,
        "animations": movies,
        "manifest": manifest,
        "partner_involution_residual": partner_residual,
    }
