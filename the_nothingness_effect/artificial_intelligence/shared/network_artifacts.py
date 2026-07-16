"""Producer-local static and animated network evidence for TNE AI models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

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
class NetworkNode:
    name: str
    layer: int
    row: float
    family: str


@dataclass(frozen=True)
class NetworkSpec:
    nodes: tuple[NetworkNode, ...]
    edges: tuple[tuple[str, str], ...]


def _network_spec(architecture: str) -> NetworkSpec:
    if architecture == "qenn":
        nodes = (
            NetworkNode("input", 0, 0.0, "input"),
            NetworkNode("Flowpoint", 1, 0.0, "tne"),
            NetworkNode("P+", 2, 0.55, "projector"),
            NetworkNode("P-", 2, -0.55, "projector"),
            NetworkNode("DFI/pDFI", 3, 0.5, "tne"),
            NetworkNode("Elastic-pi", 3, -0.5, "tne"),
            NetworkNode("DTQC clock", 4, 0.0, "dtqc"),
            NetworkNode("spectral memory", 5, 0.45, "memory"),
            NetworkNode("closure layer", 5, -0.45, "closure"),
            NetworkNode("observation", 6, 0.0, "output"),
        )
        edges = (
            ("input", "Flowpoint"), ("Flowpoint", "P+"), ("Flowpoint", "P-"),
            ("P+", "DFI/pDFI"), ("P-", "Elastic-pi"),
            ("DFI/pDFI", "DTQC clock"), ("Elastic-pi", "DTQC clock"),
            ("DTQC clock", "spectral memory"), ("DTQC clock", "closure layer"),
            ("spectral memory", "observation"), ("closure layer", "observation"),
        )
        return NetworkSpec(nodes, edges)
    if architecture == "pgqenn":
        nodes = (
            NetworkNode("QENN state", 0, 0.45, "qenn"),
            NetworkNode("MPL-TC motifs", 0, -0.45, "dependency"),
            NetworkNode("prime/parity router", 1, 0.0, "prime"),
            NetworkNode("motif growth", 2, 0.55, "growth"),
            NetworkNode("2-adic depth", 2, -0.55, "prime"),
            NetworkNode("message passing", 3, 0.0, "graph"),
            NetworkNode("pDFI gate", 4, 0.55, "tne"),
            NetworkNode("Elastic-pi edges", 4, -0.55, "tne"),
            NetworkNode("graph closure", 5, 0.0, "closure"),
            NetworkNode("observation", 6, 0.0, "output"),
        )
        edges = (
            ("QENN state", "prime/parity router"), ("MPL-TC motifs", "prime/parity router"),
            ("prime/parity router", "motif growth"), ("prime/parity router", "2-adic depth"),
            ("motif growth", "message passing"), ("2-adic depth", "message passing"),
            ("message passing", "pDFI gate"), ("message passing", "Elastic-pi edges"),
            ("pDFI gate", "graph closure"), ("Elastic-pi edges", "graph closure"),
            ("graph closure", "observation"),
        )
        return NetworkSpec(nodes, edges)
    if architecture == "soinets":
        nodes = (
            NetworkNode("QENN A", 0, 0.75, "qenn"),
            NetworkNode("QENN B", 0, 0.25, "qenn"),
            NetworkNode("PGQENN A", 0, -0.25, "pgqenn"),
            NetworkNode("PGQENN B", 0, -0.75, "pgqenn"),
            NetworkNode("bidirectional closure", 1, 0.0, "closure"),
            NetworkNode("memory transfer", 2, 0.55, "memory"),
            NetworkNode("spectral/spatial", 2, -0.55, "closure"),
            NetworkNode("meta-network", 3, 0.0, "meta"),
            NetworkNode("completeness arbiter", 4, 0.0, "closure"),
            NetworkNode("observation", 5, 0.0, "output"),
        )
        edges = tuple(
            [(node.name, "bidirectional closure") for node in nodes[:4]]
            + [
                ("bidirectional closure", "memory transfer"),
                ("bidirectional closure", "spectral/spatial"),
                ("memory transfer", "meta-network"),
                ("spectral/spatial", "meta-network"),
                ("meta-network", "completeness arbiter"),
                ("completeness arbiter", "observation"),
                ("memory transfer", "bidirectional closure"),
            ]
        )
        return NetworkSpec(nodes, edges)
    raise ValueError(f"unknown network architecture {architecture!r}")


_COLORS = {
    "input": "#9ecae9", "output": "#74c476", "tne": "#756bb1",
    "projector": "#9e9ac8", "dtqc": "#e6550d", "memory": "#31a354",
    "closure": "#de2d26", "qenn": "#3182bd", "pgqenn": "#6a51a3",
    "dependency": "#969696", "prime": "#fd8d3c", "growth": "#fdae6b",
    "graph": "#636363", "meta": "#e377c2",
}


def _positions(spec: NetworkSpec) -> dict[str, tuple[float, float]]:
    maximum = max(node.layer for node in spec.nodes) or 1
    return {
        node.name: (node.layer / maximum, node.row)
        for node in spec.nodes
    }


def _draw_network(
    axis,
    spec: NetworkSpec,
    activation: np.ndarray,
    *,
    visible_nodes: int | None = None,
    title: str,
) -> None:
    positions = _positions(spec)
    count = len(spec.nodes) if visible_nodes is None else max(1, visible_nodes)
    visible = {node.name for node in spec.nodes[:count]}
    for source, target in spec.edges:
        if source not in visible or target not in visible:
            continue
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        source_index = next(i for i, node in enumerate(spec.nodes) if node.name == source)
        strength = float(activation[source_index])
        axis.annotate(
            "", xy=(x1, y1), xytext=(x0, y0),
            arrowprops={
                "arrowstyle": "-|>", "color": plt.cm.plasma(strength),
                "lw": 0.8 + 2.8 * strength, "alpha": 0.35 + 0.6 * strength,
            },
            zorder=1,
        )
    for index, node in enumerate(spec.nodes[:count]):
        x, y = positions[node.name]
        size = 650 + 800 * float(activation[index])
        axis.scatter(
            [x], [y], s=size, c=[_COLORS[node.family]], edgecolors="black",
            linewidths=1.0 + 1.5 * float(activation[index]), zorder=3,
        )
        axis.text(x, y, node.name, ha="center", va="center", fontsize=8, zorder=4)
    axis.set(xlim=(-0.08, 1.08), ylim=(-1.05, 1.05), title=title)
    axis.axis("off")


def _save_movie(path: Path, frames: int, update) -> Path:
    figure, axis = plt.subplots(figsize=(9.0, 5.4), constrained_layout=True)

    def render(frame: int):
        axis.clear()
        update(frame, axis)
        return ()

    movie = animation.FuncAnimation(figure, render, frames=frames, interval=260, blit=False)
    movie.save(path, writer=animation.PillowWriter(fps=4))
    plt.close(figure)
    return path


def generate_architecture_network_artifacts(
    architecture: str,
    output_dir: str | Path,
    *,
    observation: Iterable[float],
    residuals: dict[str, float],
    seed: int,
    simulation: bool,
) -> dict[str, object]:
    """Generate topology, connectivity, activation, and propagation evidence."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    mode = "simulation" if simulation else "test"
    spec = _network_spec(architecture)
    generator = np.random.default_rng(seed)
    observation_vector = np.asarray(tuple(observation), dtype=float)
    residual_vector = np.asarray(tuple(residuals.values()), dtype=float)
    base = np.linspace(0.18, 0.92, len(spec.nodes))
    observation_scale = float(np.mean(observation_vector)) if observation_vector.size else 0.5
    residual_scale = float(np.tanh(np.mean(np.abs(residual_vector)))) if residual_vector.size else 0.0
    activation = np.clip(base * (0.75 + observation_scale) - 0.15 * residual_scale, 0.05, 1.0)
    activation = np.clip(activation + generator.normal(0, 0.015, len(spec.nodes)), 0.02, 1.0)

    prefix = f"{architecture}_{mode}_network"
    figures: list[Path] = []
    figure, axis = plt.subplots(figsize=(9.2, 5.6), constrained_layout=True)
    _draw_network(axis, spec, activation, title=f"{architecture.upper()} executable network topology")
    figures.append(save_figure(figure, output / f"{prefix}_topology.png", dpi=170))
    plt.close(figure)

    index = {node.name: position for position, node in enumerate(spec.nodes)}
    connectivity = np.zeros((len(spec.nodes), len(spec.nodes)))
    for source, target in spec.edges:
        connectivity[index[source], index[target]] = activation[index[source]]
    figure, axis = plt.subplots(figsize=(7.5, 6.3), constrained_layout=True)
    image = axis.imshow(connectivity, cmap="magma", vmin=0, vmax=1)
    axis.set(
        title=f"{architecture.upper()} directed connectivity",
        xticks=range(len(spec.nodes)), yticks=range(len(spec.nodes)),
        xticklabels=[node.name for node in spec.nodes],
        yticklabels=[node.name for node in spec.nodes],
    )
    axis.tick_params(axis="x", rotation=65, labelsize=7)
    axis.tick_params(axis="y", labelsize=7)
    figure.colorbar(image, ax=axis, label="activation-weighted edge")
    figures.append(save_figure(figure, output / f"{prefix}_connectivity.png", dpi=170))
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(11.0, 4.8), constrained_layout=True)
    axes[0].barh([node.name for node in spec.nodes], activation, color=[_COLORS[n.family] for n in spec.nodes])
    axes[0].set(title="Node activation profile", xlabel="normalized activation", xlim=(0, 1))
    ranked = sorted(residuals.items(), key=lambda item: abs(item[1]), reverse=True)[:12]
    axes[1].barh(
        [name[:38] for name, _ in ranked][::-1],
        [max(abs(value), 1e-12) for _, value in ranked][::-1], color="#de2d26",
    )
    axes[1].set_xscale("log")
    axes[1].set(title="Residual flow boundaries", xlabel="absolute residual")
    figures.append(save_figure(figure, output / f"{prefix}_activation_residual.png", dpi=170))
    plt.close(figure)

    rows = [
        {
            "node": node.name, "layer": node.layer, "family": node.family,
            "activation": float(activation[position]),
            "out_degree": sum(source == node.name for source, _ in spec.edges),
            "in_degree": sum(target == node.name for _, target in spec.edges),
        }
        for position, node in enumerate(spec.nodes)
    ]
    table = save_csv(output / f"{prefix}_nodes.csv", rows)

    frames = 14
    signal_movie = _save_movie(
        output / f"{prefix}_signal_propagation.gif",
        frames,
        lambda frame, axis: _draw_network(
            axis,
            spec,
            np.clip(
                0.08 + activation * np.exp(-0.5 * (np.arange(len(spec.nodes)) - frame * (len(spec.nodes) - 1) / (frames - 1)) ** 2),
                0.02,
                1.0,
            ),
            title=f"Signal propagation — frame {frame + 1}/{frames}",
        ),
    )
    topology_movie = _save_movie(
        output / f"{prefix}_topology_growth.gif",
        len(spec.nodes),
        lambda frame, axis: _draw_network(
            axis, spec, activation, visible_nodes=frame + 1,
            title=f"Network assembly — {frame + 1}/{len(spec.nodes)} nodes",
        ),
    )

    def recurrent_frame(frame: int, axis) -> None:
        phase = 2.0 * np.pi * frame / frames
        pulse = np.clip(activation * (0.58 + 0.42 * np.sin(phase + np.arange(len(spec.nodes)) * 0.8) ** 2), 0.02, 1.0)
        _draw_network(axis, spec, pulse, title=f"Recurrent activation — phase {frame + 1}/{frames}")

    recurrent_movie = _save_movie(
        output / f"{prefix}_recurrent_activation.gif", frames, recurrent_frame
    )
    movies = [signal_movie, topology_movie, recurrent_movie]
    extra_tables: list[Path] = []
    extra_manifests: list[Path] = []
    spatial_growth = None
    if architecture == "pgqenn":
        from the_nothingness_effect.artificial_intelligence.pgqenn.growth_artifacts import (
            generate_pgqenn_growth_3d_artifacts,
        )

        spatial_growth = generate_pgqenn_growth_3d_artifacts(
            output, seed=seed, simulation=simulation
        )
        figures.extend(spatial_growth["figures"])
        movies.extend(spatial_growth["animations"])
        extra_tables.extend(spatial_growth["tables"])
        extra_manifests.append(spatial_growth["manifest"])
    else:
        from the_nothingness_effect.artificial_intelligence.shared.spatial_state_artifacts import (
            generate_spatial_state_artifacts,
        )

        spatial_growth = generate_spatial_state_artifacts(
            architecture, output, seed=seed, simulation=simulation
        )
        figures.extend(spatial_growth["figures"])
        movies.extend(spatial_growth["animations"])
        extra_tables.extend(spatial_growth["tables"])
        extra_manifests.append(spatial_growth["manifest"])
    parameters = {
        "architecture": architecture, "mode": mode, "seed": seed,
        "node_count": len(spec.nodes), "edge_count": len(spec.edges),
        "executable_3d_growth": True,
        "architecture_specific_3d_semantics": True,
    }
    generated = [
        path.name
        for path in (
            *figures,
            table,
            *extra_tables,
            *movies,
            *extra_manifests,
        )
    ]
    manifest = write_metadata(
        output / f"{prefix}_manifest.json",
        {
            "architecture": architecture,
            "artifact_family": "network_topology_and_activation",
            "repository_start_commit": START_COMMIT,
            "repository_result_commit": git_commit(Path(__file__).resolve().parents[3]),
            "parameters": parameters,
            "parameter_hash": parameter_hash(parameters),
            "seed": seed,
            "generated_files": generated,
            "regeneration_command": (
                f"python -m the_nothingness_effect.artificial_intelligence.{architecture}."
                f"{mode}.run_all_capabilities"
            ),
            "source_status": "deterministic_network_state_visualization",
        },
    )
    return {
        "figures": figures,
        "animations": movies,
        "table": table,
        "extra_tables": extra_tables,
        "extra_manifests": extra_manifests,
        "spatial_growth": spatial_growth,
        "manifest": manifest,
    }
