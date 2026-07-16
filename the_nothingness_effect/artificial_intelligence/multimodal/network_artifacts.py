"""Network, axis, energy, and self-growth visualizations for multimodal TNE."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure, write_metadata
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import (
    git_commit,
    parameter_hash,
)
from the_nothingness_effect.artificial_intelligence.shared.spatial_state_artifacts import (
    generate_spatial_state_artifacts,
)

from .evaluation import MultimodalEvaluation
from .model import TNETrainableMultimodalModel
from .training import MultimodalTrainingRun


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def _project(values: np.ndarray) -> np.ndarray:
    centered = values - values.mean(axis=0, keepdims=True)
    if centered.shape[0] < 2 or centered.shape[1] < 2:
        return np.pad(centered, ((0, 0), (0, max(0, 2 - centered.shape[1]))))[:, :2]
    _, _, vectors = np.linalg.svd(centered, full_matrices=False)
    return centered @ vectors[:2].T


def _save_movie(path: Path, frames: int, update, *, size=(7.2, 5.0)) -> Path:
    figure, axis = plt.subplots(figsize=size, constrained_layout=True)

    def render(frame: int):
        axis.clear()
        update(frame, axis)
        return ()

    movie = animation.FuncAnimation(figure, render, frames=frames, interval=300, blit=False)
    movie.save(path, writer=animation.PillowWriter(fps=3))
    plt.close(figure)
    return path


def _architecture_coordinates() -> tuple[dict[str, tuple[float, float]], tuple[tuple[str, str], ...]]:
    coordinates = {
        "color": (0.0, 0.8), "sound": (0.0, 0.0), "vision": (0.0, -0.8),
        "observation": (0.14, 0.0), "shared/private axes": (0.29, 0.0),
        "local RBMs": (0.43, 0.55), "Elastic Dubler": (0.43, -0.1),
        "growing clusters": (0.43, -0.7), "global RBM": (0.57, 0.3),
        "QENN + DTQC": (0.69, 0.65), "PGQENN + MPL-TC": (0.69, -0.2),
        "SOInet meta-closure": (0.82, 0.2), "collapse/readout": (0.94, 0.2),
    }
    edges = (
        ("color", "observation"), ("sound", "observation"), ("vision", "observation"),
        ("observation", "shared/private axes"),
        ("shared/private axes", "local RBMs"),
        ("shared/private axes", "Elastic Dubler"),
        ("shared/private axes", "growing clusters"),
        ("local RBMs", "global RBM"), ("Elastic Dubler", "global RBM"),
        ("growing clusters", "global RBM"),
        ("global RBM", "QENN + DTQC"), ("global RBM", "PGQENN + MPL-TC"),
        ("QENN + DTQC", "SOInet meta-closure"),
        ("PGQENN + MPL-TC", "SOInet meta-closure"),
        ("SOInet meta-closure", "collapse/readout"),
        ("SOInet meta-closure", "shared/private axes"),
    )
    return coordinates, edges


def _draw_architecture(axis, activation: np.ndarray, *, visible: int | None = None, title: str) -> None:
    coordinates, edges = _architecture_coordinates()
    names = tuple(coordinates)
    count = len(names) if visible is None else max(1, visible)
    active_names = set(names[:count])
    for source, target in edges:
        if source not in active_names or target not in active_names:
            continue
        source_index = names.index(source)
        axis.annotate(
            "", xy=coordinates[target], xytext=coordinates[source],
            arrowprops={
                "arrowstyle": "-|>", "lw": 0.8 + 2.5 * float(activation[source_index]),
                "color": plt.cm.viridis(float(activation[source_index])), "alpha": 0.75,
            },
        )
    palette = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00"]
    for index, name in enumerate(names[:count]):
        x, y = coordinates[name]
        axis.scatter(
            [x], [y], s=560 + 850 * float(activation[index]),
            color=palette[index % len(palette)], edgecolor="black", zorder=3,
        )
        axis.text(x, y, name, ha="center", va="center", fontsize=7.5, zorder=4)
    axis.set(xlim=(-0.06, 1.02), ylim=(-1.08, 1.08), title=title)
    axis.axis("off")


def generate_multimodal_network_artifacts(
    model: TNETrainableMultimodalModel,
    run: MultimodalTrainingRun,
    evaluation: MultimodalEvaluation,
    output_dir: str | Path,
    *,
    seed: int,
    simulation: bool,
) -> dict[str, object]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    state = evaluation.output
    if state.axis_state is None or state.cluster_state is None:
        raise RuntimeError("multimodal network artifacts require axis and cluster states")
    names = state.axis_state.modality_names
    mode = "simulation" if simulation else "test"
    prefix = f"multimodal_{mode}_network"
    figures: list[Path] = []
    movies: list[Path] = []
    tables: list[Path] = []

    architecture_activation = np.linspace(0.28, 0.96, len(_architecture_coordinates()[0]))
    figure, axis = plt.subplots(figsize=(12.0, 6.0), constrained_layout=True)
    _draw_architecture(axis, architecture_activation, title="Executable multimodal TNE network")
    figures.append(save_figure(figure, output / f"{prefix}_topology.png", dpi=180))
    plt.close(figure)

    axes = state.axis_state.mapped_axes.detach().cpu().numpy()
    projection = _project(axes.reshape(-1, axes.shape[-1]))
    modality_ids = np.tile(np.arange(len(names)), axes.shape[0])
    assignments = state.cluster_state.assignments.detach().cpu().numpy().reshape(-1)
    figure, panes = plt.subplots(1, 2, figsize=(11.5, 5.0), constrained_layout=True)
    for modality_index, name in enumerate(names):
        mask = modality_ids == modality_index
        panes[0].scatter(projection[mask, 0], projection[mask, 1], label=name, s=50, alpha=0.8)
    panes[0].set(title="Learned modality axes", xlabel="axis PC1", ylabel="axis PC2")
    panes[0].legend()
    scatter = panes[1].scatter(projection[:, 0], projection[:, 1], c=assignments, cmap="tab20", s=55)
    panes[1].set(title="Axis samples routed to growing clusters", xlabel="axis PC1", ylabel="axis PC2")
    figure.colorbar(scatter, ax=panes[1], label="cluster id")
    figures.append(save_figure(figure, output / f"{prefix}_axes_and_clusters.png", dpi=180))
    plt.close(figure)

    adjacency = state.axis_state.adjacency.detach().mean(dim=0).cpu().numpy()
    figure, panes = plt.subplots(1, 2, figsize=(10.8, 4.7), constrained_layout=True)
    image = panes[0].imshow(adjacency, cmap="viridis", vmin=0, vmax=1)
    panes[0].set(
        title="Learned axis transport", xticks=range(len(names)), yticks=range(len(names)),
        xticklabels=names, yticklabels=names,
    )
    figure.colorbar(image, ax=panes[0], label="transport weight")
    reverse = state.axis_state.reverse_adjacency.detach().mean(dim=0).cpu().numpy()
    image = panes[1].imshow(reverse @ adjacency, cmap="coolwarm", vmin=-1, vmax=1)
    panes[1].set(
        title="Forward/reverse cycle matrix", xticks=range(len(names)), yticks=range(len(names)),
        xticklabels=names, yticklabels=names,
    )
    figure.colorbar(image, ax=panes[1], label="cycle response")
    figures.append(save_figure(figure, output / f"{prefix}_axis_transport.png", dpi=180))
    plt.close(figure)

    local_weight = model.local_energy.weight.detach().cpu().numpy()
    global_weight = model.global_energy.weight.detach().cpu().numpy()
    figure, panes = plt.subplots(1, 2, figsize=(12.0, 5.0), constrained_layout=True)
    for pane, weight, title in (
        (panes[0], local_weight, "Local per-axis RBM"),
        (panes[1], global_weight, "Global cross-axis RBM"),
    ):
        visible_count, hidden_count = weight.shape
        for visible_index in range(visible_count):
            for hidden_index in range(hidden_count):
                strength = abs(float(weight[visible_index, hidden_index]))
                pane.plot(
                    [0, 1], [visible_index, hidden_index * max(1, visible_count - 1) / max(1, hidden_count - 1)],
                    color="#3182bd" if weight[visible_index, hidden_index] >= 0 else "#de2d26",
                    alpha=min(0.8, 0.12 + 8.0 * strength), linewidth=0.4 + 8.0 * strength,
                )
        pane.scatter(np.zeros(visible_count), np.arange(visible_count), s=65, color="#9ecae1", edgecolor="black")
        pane.scatter(np.ones(hidden_count), np.linspace(0, visible_count - 1, hidden_count), s=80, color="#fdae6b", edgecolor="black")
        pane.set(title=title, xticks=(0, 1), xticklabels=("visible", "hidden"), yticks=[])
    figures.append(save_figure(figure, output / f"{prefix}_rbm_bipartite.png", dpi=180))
    plt.close(figure)

    centroids = state.cluster_state.centroids.detach().cpu().numpy()
    centroid_projection = _project(centroids)
    cluster_topology = state.cluster_state.topology_adjacency.detach().cpu().numpy()
    cluster_modalities = state.cluster_state.cluster_modalities.detach().cpu().numpy()
    figure, axis = plt.subplots(figsize=(7.3, 5.6), constrained_layout=True)
    for source in range(len(centroids)):
        for target in range(source + 1, len(centroids)):
            strength = cluster_topology[source, target]
            if strength > 0.05:
                axis.plot(
                    centroid_projection[[source, target], 0],
                    centroid_projection[[source, target], 1],
                    color="#969696", alpha=float(strength), linewidth=0.5 + 2.5 * float(strength),
                )
    scatter = axis.scatter(
        centroid_projection[:, 0], centroid_projection[:, 1], c=cluster_modalities,
        cmap="Set1", s=90 + 12 * state.cluster_state.cluster_counts.cpu().numpy(), edgecolor="black",
    )
    for index, point in enumerate(centroid_projection):
        axis.text(point[0], point[1], f"C{index}", ha="center", va="center", fontsize=7)
    axis.set(title="Self-grown cluster topology", xlabel="centroid PC1", ylabel="centroid PC2")
    figure.colorbar(scatter, ax=axis, label="modality axis")
    figures.append(save_figure(figure, output / f"{prefix}_cluster_topology.png", dpi=180))
    plt.close(figure)

    local_energy = state.local_rbm_state.free_energy.detach().cpu().numpy()
    global_energy = state.global_rbm_state.free_energy.detach().cpu().numpy()
    figure, axis = plt.subplots(figsize=(8.4, 4.8), constrained_layout=True)
    axis.plot(np.sort(local_energy), label="local-axis free energy", marker=".")
    axis.plot(
        np.linspace(0, max(1, len(local_energy) - 1), len(global_energy)),
        np.sort(global_energy), label="global cross-axis free energy", marker="o",
    )
    axis.set(title="RBM energy landscape over evaluated samples", xlabel="ordered state", ylabel="free energy")
    axis.legend()
    figures.append(save_figure(figure, output / f"{prefix}_energy_landscape.png", dpi=180))
    plt.close(figure)

    tables.append(
        save_csv(
            output / f"{prefix}_cluster_growth.csv",
            [
                {
                    "epoch": item.epoch, "active_clusters": item.cluster_count,
                    "growth_events": item.growth_event_count,
                    "local_free_energy": item.local_free_energy,
                    "global_free_energy": item.global_free_energy,
                }
                for item in run.history
            ],
        )
    )
    tables.append(
        save_csv(
            output / f"{prefix}_cluster_state.csv",
            [
                {
                    "cluster_id": index,
                    "modality": names[int(state.cluster_state.cluster_modalities[index])],
                    "usage_count": int(state.cluster_state.cluster_counts[index]),
                    "mean_connectivity": float(cluster_topology[index].mean()),
                }
                for index in range(state.cluster_state.active_clusters)
            ],
        )
    )

    frames = max(12, len(run.history))
    movies.append(
        _save_movie(
            output / f"{prefix}_topology_activation.gif",
            frames,
            lambda frame, axis: _draw_architecture(
                axis,
                np.clip(
                    architecture_activation
                    * (0.55 + 0.45 * np.sin(2 * np.pi * frame / frames + np.arange(len(architecture_activation))) ** 2),
                    0.03, 1.0,
                ),
                title=f"Multimodal network activation — frame {frame + 1}/{frames}",
            ),
            size=(10.5, 5.5),
        )
    )
    movies.append(
        _save_movie(
            output / f"{prefix}_topology_growth.gif",
            len(_architecture_coordinates()[0]),
            lambda frame, axis: _draw_architecture(
                axis, architecture_activation, visible=frame + 1,
                title=f"Multimodal network assembly — {frame + 1} active components",
            ),
            size=(10.5, 5.5),
        )
    )

    axis_history = np.asarray([item.axis_snapshot for item in run.history], dtype=float)
    flattened_history = axis_history.reshape(-1, axis_history.shape[-1])
    projected_history = _project(flattened_history).reshape(
        axis_history.shape[0], axis_history.shape[1], 2
    )
    movies.append(
        _save_movie(
            output / f"{prefix}_axis_learning.gif",
            len(run.history),
            lambda frame, axis: (
                axis.scatter(
                    projected_history[frame, :, 0], projected_history[frame, :, 1],
                    c=np.arange(projected_history.shape[1]) % 4, cmap="tab10", s=55,
                ),
                axis.set(title=f"Learned multimodal axis field — epoch {frame}", xlabel="PC1", ylabel="PC2"),
            ),
        )
    )

    centroid_history = [np.asarray(item.cluster_centroids, dtype=float) for item in run.history]
    common_centroids = np.concatenate([value for value in centroid_history if value.size], axis=0)
    center = common_centroids.mean(axis=0, keepdims=True)
    _, _, basis_vectors = np.linalg.svd(common_centroids - center, full_matrices=False)
    basis = basis_vectors[:2].T

    def draw_cluster_growth(frame: int, axis) -> None:
        points = (centroid_history[frame] - center) @ basis
        axis.scatter(points[:, 0], points[:, 1], c=np.arange(len(points)), cmap="tab20", s=100, edgecolor="black")
        for index, point in enumerate(points):
            axis.text(point[0], point[1], f"C{index}", ha="center", va="center", fontsize=7)
        axis.set(title=f"Cluster self-growth — epoch {frame}, {len(points)} clusters", xlabel="PC1", ylabel="PC2")

    movies.append(
        _save_movie(
            output / f"{prefix}_cluster_growth.gif", len(run.history), draw_cluster_growth
        )
    )

    visible = state.axis_state.mapped_axes.detach().reshape(-1, state.axis_state.mapped_axes.shape[-1]).cpu().numpy()
    reconstructed = state.local_rbm_state.visible_reconstruction.detach().cpu().numpy()

    def draw_rbm_reconstruction(frame: int, axis) -> None:
        fraction = frame / 11
        candidate = (1 - fraction) * visible[0] + fraction * reconstructed[0]
        axis.plot(visible[0], marker="o", label="axis visible")
        axis.plot(candidate, marker="s", label="mean-field reconstruction")
        axis.set(title=f"RBM visible/hidden/visible transition — {fraction:.2f}", xlabel="axis coordinate", ylabel="value")
        axis.legend()

    movies.append(
        _save_movie(
            output / f"{prefix}_rbm_reconstruction.gif", 12, draw_rbm_reconstruction
        )
    )

    spatial_growth = generate_spatial_state_artifacts(
        "multimodal", output, seed=seed, simulation=simulation
    )
    tables.extend(spatial_growth["tables"])
    figures.extend(spatial_growth["figures"])
    movies.extend(spatial_growth["animations"])
    extra_manifests = [spatial_growth["manifest"]]

    parameters = {
        "architecture": "TNE Trainable Multimodal SOInet",
        "mode": mode, "seed": seed, "modalities": list(names),
        "axis_dim": int(state.axis_state.mapped_axes.shape[-1]),
        "active_clusters": state.cluster_state.active_clusters,
        "local_rbm": [model.local_energy.visible_dim, model.local_energy.hidden_dim],
        "global_rbm": [model.global_energy.visible_dim, model.global_energy.hidden_dim],
        "executable_3d_growth": True,
        "architecture_specific_3d_semantics": True,
    }
    generated = [path.name for path in (*tables, *figures, *movies, *extra_manifests)]
    manifest = write_metadata(
        output / f"{prefix}_manifest.json",
        {
            "architecture": parameters["architecture"],
            "artifact_family": "axes_energy_clusters_and_network",
            "repository_start_commit": START_COMMIT,
            "repository_result_commit": git_commit(Path(__file__).resolve().parents[3]),
            "parameters": parameters,
            "parameter_hash": parameter_hash(parameters),
            "seed": seed,
            "generated_files": generated,
            "regeneration_command": (
                "python -m the_nothingness_effect.artificial_intelligence.multimodal."
                f"{mode}.run_pipeline"
            ),
            "source_status": "synthetic_deterministic_training_and_network_state",
            "rbm_source_status": "external_numerical_realization_not_tne_source_law",
        },
    )
    return {
        "tables": tables,
        "figures": figures,
        "animations": movies,
        "extra_manifests": extra_manifests,
        "spatial_growth": spatial_growth,
        "manifest": manifest,
    }
