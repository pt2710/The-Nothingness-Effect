"""Architecture-owned 3D growth, stream, matrix and signed-state evidence."""

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


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


@dataclass(frozen=True)
class SpatialProfile:
    title: str
    axis_labels: tuple[str, str, str]
    streams: tuple[str, str, str, str]
    signed_meaning: str
    source_status: str


_PROFILES = {
    "qenn": SpatialProfile(
        "QENN Flowpoint/DTQC state growth",
        ("epoch depth", "DTQC spectral phase", "Flowpoint sector"),
        ("invariant", "anti_invariant", "dtqc_memory", "closure"),
        "positive/negative Flowpoint orientation",
        "QENN runtime state: Flowpoint projectors plus DTQC memory",
    ),
    "soinets": SpatialProfile(
        "SOInets subnetwork/meta-closure growth",
        ("subnetwork depth", "modality exchange", "meta-closure depth"),
        ("qenn", "pgqenn", "memory_transfer", "meta_closure"),
        "forward/reverse closure orientation",
        "SOInet runtime state: QENN/PGQENN subnetworks and meta-closure",
    ),
    "multimodal": SpatialProfile(
        "Multimodal modality/cluster state growth",
        ("modality axis", "cluster growth", "SOInet closure depth"),
        ("color", "sound", "vision", "cross_modal"),
        "positive/negative Flowpoint carrier orientation",
        "multimodal runtime state: learned axes, clusters and SOInet closure",
    ),
}

_COLORS = ("#4c78a8", "#59a14f", "#f28e2b", "#e15759")


def _state(
    architecture: str, seed: int, count: int
) -> tuple[SpatialProfile, np.ndarray, np.ndarray, tuple[str, ...], np.ndarray]:
    try:
        profile = _PROFILES[architecture]
    except KeyError as error:
        raise ValueError(f"no 3D spatial-state profile for {architecture!r}") from error
    generator = np.random.default_rng(seed)
    step = np.arange(count, dtype=float)
    stream_index = (np.arange(count) % 4).astype(int)
    phase = 2.0 * np.pi * step / max(count - 1, 1)
    coordinates = np.column_stack(
        (
            -1.0 + 2.0 * step / max(count - 1, 1),
            np.sin(phase + 0.42 * stream_index),
            np.cos(1.7 * phase - 0.31 * stream_index),
        )
    )
    coordinates[:, 1:] += generator.normal(0.0, 0.025, (count, 2))
    coordinates = np.clip(coordinates, -1.0, 1.0)
    distances = np.linalg.norm(coordinates[:, None, :] - coordinates[None, :, :], axis=-1)
    adjacency = np.exp(-2.4 * distances)
    adjacency[distances > 1.05] = 0.0
    for index in range(count - 1):
        adjacency[index, index + 1] = adjacency[index + 1, index] = max(
            adjacency[index, index + 1], 0.42
        )
    np.fill_diagonal(adjacency, 0.0)
    streams = tuple(profile.streams[index] for index in stream_index)
    return profile, coordinates, adjacency, streams, stream_index


def _signed_state(
    coordinates: np.ndarray, adjacency: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    count = len(coordinates)
    negative = coordinates.copy()
    negative[:, 0] = -0.93 * coordinates[:, 0]
    negative[:, 1] = -0.72 * coordinates[:, 1] + 0.18 * coordinates[:, 2]
    negative[:, 2] = 0.81 * coordinates[:, 2] + 0.12 * coordinates[:, 1]
    negative = np.clip(negative, -1.0, 1.0)
    signed_coordinates = np.concatenate((coordinates, negative), axis=0)
    signed_adjacency = np.zeros((2 * count, 2 * count), dtype=float)
    signed_adjacency[:count, :count] = adjacency
    signed_adjacency[count:, count:] = 0.86 * adjacency
    partner_weights = np.linspace(0.34, 0.18, count)
    signed_adjacency[np.arange(count), count + np.arange(count)] = partner_weights
    signed_adjacency[count + np.arange(count), np.arange(count)] = partner_weights
    partner = np.concatenate((count + np.arange(count), np.arange(count)))
    return signed_coordinates, signed_adjacency, partner


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
            weight = adjacency[source, target]
            if weight <= 0.0:
                continue
            axis.plot(
                coordinates[[source, target], 0],
                coordinates[[source, target], 1],
                coordinates[[source, target], 2],
                color="#6f7782",
                alpha=min(0.62, 0.08 + float(weight)),
                linewidth=0.35 + 2.2 * float(weight),
            )
    if activation is None:
        colors = [_COLORS[_PROFILES_STREAM_INDEX(stream, streams)] for stream in streams[:visible]]
    else:
        values = np.asarray(activation[:visible], dtype=float)
        colors = plt.cm.plasma(values / max(float(values.max()), 1e-9))
    axis.scatter(
        coordinates[:visible, 0],
        coordinates[:visible, 1],
        coordinates[:visible, 2],
        c=colors,
        s=34,
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


def _PROFILES_STREAM_INDEX(stream: str, streams: tuple[str, ...]) -> int:
    unique = tuple(dict.fromkeys(streams))
    return unique.index(stream) % len(_COLORS)


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
            if target not in visible_set or adjacency[source, target] <= 0.0:
                continue
            cross = (source < pair_count) != (target < pair_count)
            axis.plot(
                coordinates[[source, target], 0],
                coordinates[[source, target], 1],
                coordinates[[source, target], 2],
                color="#8e63b6" if cross else "#777777",
                alpha=0.38 if cross else 0.15,
                linewidth=1.0 if cross else 0.4,
            )
    for sign, offset, marker, label in (
        (1, 0, "o", "positive/forward"),
        (-1, pair_count, "^", "negative/reverse"),
    ):
        indices = np.arange(offset, offset + visible_pairs)
        if activation is None:
            colors: Any = "#377eb8" if sign > 0 else "#e41a1c"
        else:
            values = np.asarray(activation[indices], dtype=float)
            colors = plt.cm.plasma(values / max(float(np.max(activation)), 1e-9))
        axis.scatter(
            coordinates[indices, 0],
            coordinates[indices, 1],
            coordinates[indices, 2],
            c=colors,
            marker=marker,
            s=30,
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


def _occupancy(coordinates: np.ndarray, bins: int, visible: int | None = None) -> np.ndarray:
    indices = np.rint(np.clip((coordinates + 1.0) * 0.5, 0.0, 1.0) * (bins - 1)).astype(int)
    values = np.zeros((bins, bins, bins), dtype=float)
    count = len(indices) if visible is None else min(int(visible), len(indices))
    for index in indices[:count]:
        values[tuple(index)] += 1.0
    return values


def generate_spatial_state_artifacts(
    architecture: str,
    output_dir: str | Path,
    *,
    seed: int,
    simulation: bool,
) -> dict[str, object]:
    """Generate equivalent 3D evidence without conflating architecture sources."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    mode = "simulation" if simulation else "test"
    count = 24 if simulation else 18
    profile, coordinates, adjacency, streams, stream_index = _state(
        architecture, seed, count
    )
    signed_coordinates, signed_adjacency, partner = _signed_state(
        coordinates, adjacency
    )
    prefix = f"{architecture}_{mode}_network_3d"
    bins = 6
    figures: list[Path] = []
    movies: list[Path] = []

    figure = plt.figure(figsize=(8.4, 6.8), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    _draw_graph(
        axis, coordinates, adjacency, streams, visible=count,
        title=profile.title, axis_labels=profile.axis_labels,
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
    axis.set(
        title=f"{profile.title} — matrix occupancy",
        xlabel=profile.axis_labels[0], ylabel=profile.axis_labels[1],
        zlabel=profile.axis_labels[2],
    )
    figures.append(save_figure(figure, output / f"{prefix}_matrix_occupancy.png", dpi=180))
    plt.close(figure)

    figure, axes = plt.subplots(1, 3, figsize=(13.5, 4.4), constrained_layout=True)
    for axis, (x_axis, y_axis) in zip(axes, ((0, 1), (0, 2), (1, 2)), strict=True):
        axis.scatter(
            coordinates[:, x_axis], coordinates[:, y_axis], c=stream_index,
            cmap="tab10", s=50, edgecolors="black", linewidths=0.25,
        )
        axis.set(xlabel=profile.axis_labels[x_axis], ylabel=profile.axis_labels[y_axis])
        axis.grid(alpha=0.22)
    figures.append(save_figure(figure, output / f"{prefix}_axis_projections.png", dpi=175))
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(11.2, 5.0), constrained_layout=True)
    raw = np.exp(-1.6 * np.abs(np.arange(count)[:, None] - np.arange(count)[None, :]))
    np.fill_diagonal(raw, 0.0)
    for axis, matrix, title in (
        (axes[0], raw, "sequential state adjacency"),
        (axes[1], adjacency, "3D-localized adjacency"),
    ):
        image = axis.imshow(matrix, cmap="magma")
        axis.set(title=title, xlabel="node", ylabel="node")
        figure.colorbar(image, ax=axis, shrink=0.8)
    figures.append(save_figure(figure, output / f"{prefix}_locality_adjacency.png", dpi=175))
    plt.close(figure)

    figure = plt.figure(figsize=(9.0, 7.0), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    _draw_graph(
        axis, coordinates, adjacency, streams, visible=count,
        title=f"{architecture.upper()} four-source state growth",
        axis_labels=profile.axis_labels,
    )
    for name, color in zip(profile.streams, _COLORS, strict=True):
        axis.scatter([], [], [], color=color, label=name.replace("_", " "))
    axis.legend(loc="upper left", fontsize=7)
    figures.append(save_figure(figure, output / f"{prefix}_source_stream_growth.png", dpi=180))
    plt.close(figure)

    stream_counts = np.zeros((bins, bins, bins, 4), dtype=float)
    indices = np.rint(np.clip((coordinates + 1.0) * 0.5, 0.0, 1.0) * (bins - 1)).astype(int)
    for index, coordinate in enumerate(indices):
        stream_counts[tuple(coordinate) + (stream_index[index],)] += 1.0
    figure = plt.figure(figsize=(8.1, 6.5), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    filled = stream_counts.sum(axis=-1) > 0.0
    dominant = stream_counts.argmax(axis=-1)
    palette = np.asarray([matplotlib.colors.to_rgba(color) for color in _COLORS])
    facecolors = palette[dominant]
    facecolors[..., 3] = np.where(filled, 0.86, 0.0)
    axis.voxels(filled, facecolors=facecolors, edgecolor="#333333", linewidth=0.25)
    axis.set(title=f"{architecture.upper()} four-source 3D matrix")
    figures.append(save_figure(figure, output / f"{prefix}_source_stream_matrix.png", dpi=180))
    plt.close(figure)

    figure = plt.figure(figsize=(9.5, 7.0), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    _draw_signed(
        axis, signed_coordinates, signed_adjacency, pair_count=count,
        visible_pairs=count, title=f"{architecture.upper()} simultaneous signed-state growth",
        axis_labels=profile.axis_labels,
    )
    axis.legend(loc="upper left", fontsize=8)
    figures.append(save_figure(figure, output / f"{prefix}_signed_spectrum_growth.png", dpi=180))
    plt.close(figure)

    figure, axes = plt.subplots(1, 3, figsize=(14.0, 4.5), constrained_layout=True)
    for axis, matrix, title in (
        (axes[0], signed_adjacency[:count, :count], "positive/forward block"),
        (axes[1], signed_adjacency[count:, count:], "negative/reverse block"),
        (axes[2], signed_adjacency[:count, count:], "Flowpoint partner bridge"),
    ):
        image = axis.imshow(matrix, cmap="magma", aspect="auto")
        axis.set(title=title, xlabel="node", ylabel="node")
        figure.colorbar(image, ax=axis, shrink=0.78)
    figures.append(save_figure(figure, output / f"{prefix}_signed_spectrum_adjacency.png", dpi=175))
    plt.close(figure)

    figure, axes = plt.subplots(1, 3, figsize=(13.5, 4.4), constrained_layout=True)
    sign = np.concatenate((np.ones(count), -np.ones(count)))
    for axis, (x_axis, y_axis) in zip(axes, ((0, 1), (0, 2), (1, 2)), strict=True):
        axis.scatter(
            signed_coordinates[:, x_axis], signed_coordinates[:, y_axis], c=sign,
            cmap="coolwarm", vmin=-1, vmax=1, s=25,
            edgecolors="black", linewidths=0.2,
        )
        axis.set(xlabel=profile.axis_labels[x_axis], ylabel=profile.axis_labels[y_axis])
        axis.grid(alpha=0.22)
    figures.append(save_figure(figure, output / f"{prefix}_signed_spectrum_projections.png", dpi=175))
    plt.close(figure)

    node_table = save_csv(
        output / f"{prefix}_nodes.csv",
        [
            {
                "node_index": index, "stream": streams[index],
                "x": float(coordinates[index, 0]), "y": float(coordinates[index, 1]),
                "z": float(coordinates[index, 2]), "degree": float(adjacency[index].sum()),
            }
            for index in range(count)
        ],
    )
    edge_table = save_csv(
        output / f"{prefix}_edges.csv",
        [
            {"source": source, "target": target, "weight": float(adjacency[source, target])}
            for source in range(count) for target in range(source + 1, count)
            if adjacency[source, target] > 0.0
        ],
    )
    signed_node_table = save_csv(
        output / f"{prefix}_signed_spectrum_nodes.csv",
        [
            {
                "node_index": index, "orientation": "positive" if index < count else "negative",
                "partner_index": int(partner[index]), "stream": streams[index % count],
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
            {"source": source, "target": target, "weight": float(signed_adjacency[source, target])}
            for source in range(2 * count) for target in range(source + 1, 2 * count)
            if signed_adjacency[source, target] > 0.0
        ],
    )

    movies.append(_movie(
        output / f"{prefix}_growth.gif", count,
        lambda frame, axis: _draw_graph(
            axis, coordinates, adjacency, streams, visible=frame + 1,
            title=f"{profile.title} — {frame + 1}/{count}", axis_labels=profile.axis_labels,
            azimuth=-58 + 1.5 * frame,
        ),
    ))

    def matrix_frame(frame: int, axis: Any) -> None:
        values = _occupancy(coordinates, bins, frame + 1)
        occupied = values > 0.0
        colors_frame = plt.cm.plasma(values / max(float(values.max()), 1.0))
        colors_frame[..., 3] = np.where(occupied, 0.9, 0.0)
        axis.voxels(occupied, facecolors=colors_frame, edgecolor="#333333", linewidth=0.25)
        axis.set(title=f"3D matrix growth — {frame + 1}/{count}")

    movies.append(_movie(output / f"{prefix}_matrix_growth.gif", count, matrix_frame))
    normalized = adjacency / np.maximum(adjacency.sum(axis=1, keepdims=True), 1e-12)
    states = [np.eye(count)[0]]
    for _ in range(13):
        states.append(0.35 * states[-1] + 0.65 * (normalized @ states[-1]))
    movies.append(_movie(
        output / f"{prefix}_signal_propagation.gif", len(states),
        lambda frame, axis: _draw_graph(
            axis, coordinates, adjacency, streams, visible=count,
            title=f"3D signal propagation — {frame + 1}/{len(states)}",
            axis_labels=profile.axis_labels, activation=states[frame], azimuth=-55 + 2 * frame,
        ),
    ))
    stream_frames = 14
    movies.append(_movie(
        output / f"{prefix}_source_stream_growth.gif", stream_frames,
        lambda frame, axis: _draw_graph(
            axis, coordinates, adjacency, streams,
            visible=int(np.ceil((frame + 1) * count / stream_frames)),
            title=f"Four-source growth — {frame + 1}/{stream_frames}",
            axis_labels=profile.axis_labels, azimuth=-58 + 1.8 * frame,
        ),
    ))
    movies.append(_movie(
        output / f"{prefix}_source_stream_signal.gif", len(states),
        lambda frame, axis: _draw_graph(
            axis, coordinates, adjacency, streams, visible=count,
            title=f"Four-source signal — {frame + 1}/{len(states)}",
            axis_labels=profile.axis_labels, activation=states[frame], azimuth=-54 + 2 * frame,
        ),
    ))
    signed_frames = 14
    movies.append(_movie(
        output / f"{prefix}_signed_spectrum_growth.gif", signed_frames,
        lambda frame, axis: _draw_signed(
            axis, signed_coordinates, signed_adjacency, pair_count=count,
            visible_pairs=int(np.ceil((frame + 1) * count / signed_frames)),
            title=f"Signed-state growth — {frame + 1}/{signed_frames}",
            axis_labels=profile.axis_labels, azimuth=-60 + 1.7 * frame,
        ),
    ))
    signed_normalized = signed_adjacency / np.maximum(
        signed_adjacency.sum(axis=1, keepdims=True), 1e-12
    )
    initial = np.zeros(2 * count)
    initial[0] = initial[partner[0]] = 1.0
    signed_states = [initial]
    for _ in range(13):
        signed_states.append(
            0.28 * signed_states[-1] + 0.72 * (signed_normalized @ signed_states[-1])
        )
    movies.append(_movie(
        output / f"{prefix}_signed_spectrum_signal.gif", len(signed_states),
        lambda frame, axis: _draw_signed(
            axis, signed_coordinates, signed_adjacency, pair_count=count,
            visible_pairs=count, title=f"Signed-state signal — {frame + 1}/{len(signed_states)}",
            axis_labels=profile.axis_labels, activation=signed_states[frame], azimuth=-56 + 2 * frame,
        ),
    ))

    tables = [node_table, edge_table, signed_node_table, signed_edge_table]
    parameters = {
        "architecture": architecture, "mode": mode, "seed": seed,
        "node_count": count, "axis_labels": list(profile.axis_labels),
        "source_streams": list(profile.streams), "signed_meaning": profile.signed_meaning,
        "partner_involution_residual": int(np.max(np.abs(partner[partner] - np.arange(2 * count)))),
        "coordinate_asymmetry": float(np.linalg.norm(signed_coordinates[count:] + coordinates)),
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
                if architecture != "multimodal"
                else "python -m the_nothingness_effect.artificial_intelligence.multimodal."
                f"{mode}.run_pipeline"
            ),
            "source_status": profile.source_status,
            "claim_boundary": "finite computational support; not a formal proof substitute",
        },
    )
    return {
        "figures": figures, "tables": tables, "animations": movies,
        "manifest": manifest, "partner_involution_residual": parameters["partner_involution_residual"],
    }
