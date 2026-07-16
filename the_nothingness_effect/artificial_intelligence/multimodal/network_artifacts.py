"""Runtime-derived network, axis, energy, and self-growth evidence."""

from __future__ import annotations

from pathlib import Path

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
from the_nothingness_effect.artificial_intelligence.shared.spatial_state_artifacts import (
    generate_spatial_state_artifacts,
)

from .evaluation import MultimodalEvaluation
from .model import TNETrainableMultimodalModel
from .training import MultimodalTrainingRun


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def _project(values: np.ndarray, dimensions: int = 2) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    centered = values - values.mean(axis=0, keepdims=True)
    if centered.shape[0] < 2:
        return np.pad(centered, ((0, 0), (0, max(0, dimensions - centered.shape[1]))))[:, :dimensions]
    _, singular, vectors = np.linalg.svd(centered, full_matrices=False)
    width = min(dimensions, vectors.shape[0], singular.size)
    result = centered @ vectors[:width].T
    if width < dimensions:
        result = np.pad(result, ((0, 0), (0, dimensions - width)))
    scale = max(float(np.max(np.abs(result))), 1e-12)
    return np.clip(result / scale, -1.0, 1.0)


def _normalize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float).reshape(-1)
    minimum = float(values.min())
    maximum = float(values.max())
    if maximum - minimum <= 1e-12:
        return np.clip(np.abs(values) / max(abs(maximum), 1.0), 0.0, 1.0)
    return np.clip((values - minimum) / (maximum - minimum), 0.0, 1.0)


def _resample(values: np.ndarray, size: int) -> np.ndarray:
    values = np.asarray(values, dtype=float).reshape(-1)
    if values.size == size:
        return values
    if values.size == 1:
        return np.repeat(values, size)
    return np.interp(
        np.linspace(0.0, 1.0, size),
        np.linspace(0.0, 1.0, values.size),
        values,
    )


def _save_movie(path: Path, trace: np.ndarray, draw, *, size=(7.2, 5.0)) -> Path:
    figure, axis = plt.subplots(figsize=size, constrained_layout=True)

    def render(frame: int):
        axis.clear()
        draw(frame, axis)
        return ()

    movie = animation.FuncAnimation(
        figure, render, frames=len(trace), interval=300, blit=False
    )
    movie.save(path, writer=animation.PillowWriter(fps=3))
    plt.close(figure)
    return path


def _architecture_coordinates() -> tuple[dict[str, tuple[float, float]], tuple[tuple[str, str], ...]]:
    coordinates = {
        "color": (0.0, 0.8),
        "sound": (0.0, 0.0),
        "vision": (0.0, -0.8),
        "observation": (0.14, 0.0),
        "shared/private axes": (0.29, 0.0),
        "local RBMs": (0.43, 0.55),
        "Elastic Dubler": (0.43, -0.1),
        "growing clusters": (0.43, -0.7),
        "global RBM": (0.57, 0.3),
        "QENN + DTQC": (0.69, 0.65),
        "PGQENN + MPL-TC": (0.69, -0.2),
        "SOInet meta-closure": (0.82, 0.2),
        "collapse/readout": (0.94, 0.2),
    }
    edges = (
        ("color", "observation"),
        ("sound", "observation"),
        ("vision", "observation"),
        ("observation", "shared/private axes"),
        ("shared/private axes", "local RBMs"),
        ("shared/private axes", "Elastic Dubler"),
        ("shared/private axes", "growing clusters"),
        ("local RBMs", "global RBM"),
        ("Elastic Dubler", "global RBM"),
        ("growing clusters", "global RBM"),
        ("global RBM", "QENN + DTQC"),
        ("global RBM", "PGQENN + MPL-TC"),
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
        strength = float(activation[source_index])
        axis.annotate(
            "",
            xy=coordinates[target],
            xytext=coordinates[source],
            arrowprops={
                "arrowstyle": "-|>",
                "lw": 0.8 + 2.5 * strength,
                "color": plt.cm.viridis(strength),
                "alpha": 0.75,
            },
        )
    for index, name in enumerate(names[:count]):
        x, y = coordinates[name]
        axis.scatter(
            [x],
            [y],
            s=560 + 850 * float(activation[index]),
            c=[plt.cm.plasma(float(activation[index]))],
            edgecolor="black",
            zorder=3,
        )
        axis.text(x, y, name, ha="center", va="center", fontsize=7.5, zorder=4)
    axis.set(xlim=(-0.06, 1.02), ylim=(-1.08, 1.08), title=title)
    axis.axis("off")


def _runtime_snapshot(state, run: MultimodalTrainingRun) -> ArchitectureRuntimeState:
    mapped = state.axis_state.mapped_axes.detach().cpu().numpy()
    names = tuple(state.axis_state.modality_names)
    modality_state = mapped.mean(axis=0)
    coordinates = _project(modality_state, dimensions=3)
    adjacency = state.axis_state.adjacency.detach().mean(dim=0).cpu().numpy()
    adjacency = np.asarray(adjacency, dtype=float)
    np.fill_diagonal(adjacency, 0.0)
    history = np.asarray([item.modality_weights for item in run.history], dtype=float)
    if history.ndim != 2 or history.shape[1] != len(names):
        history = np.repeat(np.ones((1, len(names))) / len(names), 10, axis=0)
    if len(history) < 10:
        history = np.tile(history, (int(np.ceil(10 / len(history))), 1))[:10]
    history = np.stack([_normalize(row) for row in history])
    activation = _normalize(history[-1])
    signed_coordinates = np.concatenate((coordinates, -coordinates), axis=0)
    count = len(coordinates)
    signed_adjacency = np.zeros((2 * count, 2 * count), dtype=float)
    signed_adjacency[:count, :count] = adjacency
    signed_adjacency[count:, count:] = adjacency
    partner_weights = 0.2 + 0.7 * activation
    indices = np.arange(count)
    signed_adjacency[indices, count + indices] = partner_weights
    signed_adjacency[count + indices, indices] = partner_weights
    partner = np.concatenate((count + indices, indices))
    return ArchitectureRuntimeState(
        architecture="multimodal",
        node_activation=activation,
        activation_trace=history,
        coordinates=coordinates,
        adjacency=adjacency,
        streams=names,
        signed_coordinates=signed_coordinates,
        signed_adjacency=signed_adjacency,
        partner=partner,
    )


def _architecture_trace(state, run: MultimodalTrainingRun, size: int) -> np.ndarray:
    observation = state.observation.detach().cpu().numpy().reshape(-1)
    rows = []
    for item in run.history:
        raw = np.asarray(
            [
                *item.modality_weights,
                item.cluster_count,
                item.local_free_energy,
                item.global_free_energy,
                item.K_D,
                item.soi_scale,
                item.train_accuracy,
                item.validation_accuracy,
                item.train_total_loss,
                item.validation_loss,
                *observation,
            ],
            dtype=float,
        )
        rows.append(_normalize(_resample(raw, size)))
    trace = np.stack(rows)
    if len(trace) < 12:
        trace = np.tile(trace, (int(np.ceil(12 / len(trace))), 1))[:12]
    return trace


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

    topology_names = tuple(_architecture_coordinates()[0])
    trace = _architecture_trace(state, run, len(topology_names))
    activation = trace[-1]
    figure, axis = plt.subplots(figsize=(12.0, 6.0), constrained_layout=True)
    _draw_architecture(axis, activation, title="Runtime multimodal TNE network")
    figures.append(save_figure(figure, output / f"{prefix}_topology.png", dpi=180))
    plt.close(figure)

    axes_state = state.axis_state.mapped_axes.detach().cpu().numpy()
    projection = _project(axes_state.reshape(-1, axes_state.shape[-1]))
    modality_ids = np.tile(np.arange(len(names)), axes_state.shape[0])
    assignments = state.cluster_state.assignments.detach().cpu().numpy().reshape(-1)
    figure, panes = plt.subplots(1, 2, figsize=(11.5, 5.0), constrained_layout=True)
    for modality_index, name in enumerate(names):
        mask = modality_ids == modality_index
        panes[0].scatter(projection[mask, 0], projection[mask, 1], label=name, s=50)
    panes[0].set(title="Learned modality axes", xlabel="axis PC1", ylabel="axis PC2")
    panes[0].legend()
    scatter = panes[1].scatter(
        projection[:, 0], projection[:, 1], c=assignments, cmap="tab20", s=55
    )
    panes[1].set(title="Runtime cluster assignments", xlabel="axis PC1", ylabel="axis PC2")
    figure.colorbar(scatter, ax=panes[1], label="cluster id")
    figures.append(save_figure(figure, output / f"{prefix}_axes_and_clusters.png", dpi=180))
    plt.close(figure)

    adjacency = state.axis_state.adjacency.detach().mean(dim=0).cpu().numpy()
    reverse = state.axis_state.reverse_adjacency.detach().mean(dim=0).cpu().numpy()
    figure, panes = plt.subplots(1, 2, figsize=(10.8, 4.7), constrained_layout=True)
    for pane, matrix, title in (
        (panes[0], adjacency, "Learned axis transport"),
        (panes[1], reverse @ adjacency, "Forward/reverse cycle matrix"),
    ):
        image = pane.imshow(matrix, cmap="viridis")
        pane.set(title=title, xticks=range(len(names)), yticks=range(len(names)))
        pane.set_xticklabels(names)
        pane.set_yticklabels(names)
        figure.colorbar(image, ax=pane)
    figures.append(save_figure(figure, output / f"{prefix}_axis_transport.png", dpi=180))
    plt.close(figure)

    local_weight = model.local_energy.weight.detach().cpu().numpy()
    global_weight = model.global_energy.weight.detach().cpu().numpy()
    figure, panes = plt.subplots(1, 2, figsize=(12.0, 5.0), constrained_layout=True)
    for pane, weight, title in (
        (panes[0], local_weight, "Local per-axis RBM"),
        (panes[1], global_weight, "Global cross-axis RBM"),
    ):
        pane.imshow(weight, cmap="coolwarm", aspect="auto")
        pane.set(title=title, xlabel="hidden", ylabel="visible")
    figures.append(save_figure(figure, output / f"{prefix}_rbm_bipartite.png", dpi=180))
    plt.close(figure)

    centroids = state.cluster_state.centroids.detach().cpu().numpy()
    centroid_projection = _project(centroids)
    cluster_topology = state.cluster_state.topology_adjacency.detach().cpu().numpy()
    cluster_modalities = state.cluster_state.cluster_modalities.detach().cpu().numpy()
    figure, axis = plt.subplots(figsize=(7.3, 5.6), constrained_layout=True)
    for source in range(len(centroids)):
        for target in range(source + 1, len(centroids)):
            strength = float(cluster_topology[source, target])
            if strength > 0.05:
                axis.plot(
                    centroid_projection[[source, target], 0],
                    centroid_projection[[source, target], 1],
                    alpha=strength,
                    linewidth=0.5 + 2.5 * strength,
                )
    axis.scatter(
        centroid_projection[:, 0],
        centroid_projection[:, 1],
        c=cluster_modalities,
        cmap="Set1",
        s=90 + 12 * state.cluster_state.cluster_counts.cpu().numpy(),
        edgecolor="black",
    )
    axis.set(title="Self-grown runtime cluster topology", xlabel="PC1", ylabel="PC2")
    figures.append(save_figure(figure, output / f"{prefix}_cluster_topology.png", dpi=180))
    plt.close(figure)

    local_energy = state.local_rbm_state.free_energy.detach().cpu().numpy()
    global_energy = state.global_rbm_state.free_energy.detach().cpu().numpy()
    figure, axis = plt.subplots(figsize=(8.4, 4.8), constrained_layout=True)
    axis.plot(np.sort(local_energy), label="local-axis free energy", marker=".")
    axis.plot(
        np.linspace(0, max(1, len(local_energy) - 1), len(global_energy)),
        np.sort(global_energy),
        label="global cross-axis free energy",
        marker="o",
    )
    axis.set(title="Runtime RBM energy landscape", xlabel="ordered state", ylabel="free energy")
    axis.legend()
    figures.append(save_figure(figure, output / f"{prefix}_energy_landscape.png", dpi=180))
    plt.close(figure)

    tables.append(
        save_csv(
            output / f"{prefix}_cluster_growth.csv",
            [
                {
                    "epoch": item.epoch,
                    "active_clusters": item.cluster_count,
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

    movies.append(
        _save_movie(
            output / f"{prefix}_topology_activation.gif",
            trace,
            lambda frame, axis: _draw_architecture(
                axis,
                trace[frame],
                title=f"Runtime multimodal activation — frame {frame + 1}/{len(trace)}",
            ),
            size=(10.5, 5.5),
        )
    )
    cumulative = np.maximum.accumulate(trace, axis=0)
    movies.append(
        _save_movie(
            output / f"{prefix}_topology_growth.gif",
            cumulative,
            lambda frame, axis: _draw_architecture(
                axis,
                cumulative[frame],
                visible=min(frame + 1, len(topology_names)),
                title=f"Runtime network exposure — frame {frame + 1}/{len(cumulative)}",
            ),
            size=(10.5, 5.5),
        )
    )

    axis_history = np.asarray([item.axis_snapshot for item in run.history], dtype=float)
    projected_history = np.stack(
        [_project(frame.reshape(-1, frame.shape[-1])) for frame in axis_history]
    )
    if len(projected_history) < 2:
        projected_history = np.repeat(projected_history, 2, axis=0)
    movies.append(
        _save_movie(
            output / f"{prefix}_axis_learning.gif",
            projected_history,
            lambda frame, axis: (
                axis.scatter(
                    projected_history[frame, :, 0],
                    projected_history[frame, :, 1],
                    c=np.arange(projected_history.shape[1]) % max(len(names), 1),
                    cmap="tab10",
                    s=55,
                ),
                axis.set(title=f"Learned axis field — epoch {frame}", xlabel="PC1", ylabel="PC2"),
            ),
        )
    )

    centroid_history = [np.asarray(item.cluster_centroids, dtype=float) for item in run.history]
    if len(centroid_history) < 2:
        centroid_history = centroid_history * 2
    common = np.concatenate([value for value in centroid_history if value.size], axis=0)
    center = common.mean(axis=0, keepdims=True)
    _, _, vectors = np.linalg.svd(common - center, full_matrices=False)
    basis = vectors[:2].T

    def draw_cluster_growth(frame: int, axis) -> None:
        points = (centroid_history[frame] - center) @ basis
        axis.scatter(points[:, 0], points[:, 1], c=np.arange(len(points)), cmap="tab20", s=100)
        axis.set(title=f"Runtime cluster growth — epoch {frame}", xlabel="PC1", ylabel="PC2")

    movies.append(
        _save_movie(
            output / f"{prefix}_cluster_growth.gif",
            np.arange(len(centroid_history))[:, None],
            draw_cluster_growth,
        )
    )

    visible = state.axis_state.mapped_axes.detach().reshape(
        -1, state.axis_state.mapped_axes.shape[-1]
    ).cpu().numpy()
    reconstructed = state.local_rbm_state.visible_reconstruction.detach().cpu().numpy()
    transition = np.linspace(0.0, 1.0, 12)[:, None]

    def draw_rbm(frame: int, axis) -> None:
        fraction = float(transition[frame, 0])
        candidate = (1.0 - fraction) * visible[0] + fraction * reconstructed[0]
        axis.plot(visible[0], marker="o", label="axis visible")
        axis.plot(candidate, marker="s", label="runtime reconstruction")
        axis.set(title=f"RBM visible/hidden/visible transition — {fraction:.2f}")
        axis.legend()

    movies.append(
        _save_movie(
            output / f"{prefix}_rbm_reconstruction.gif",
            transition,
            draw_rbm,
        )
    )

    runtime_state = _runtime_snapshot(state, run)
    spatial_growth = generate_spatial_state_artifacts(
        "multimodal",
        output,
        runtime_state=runtime_state,
        seed=seed,
        simulation=simulation,
    )
    tables.extend(spatial_growth["tables"])
    figures.extend(spatial_growth["figures"])
    movies.extend(spatial_growth["animations"])
    extra_manifests = [spatial_growth["manifest"]]

    parameters = {
        "architecture": "TNE Trainable Multimodal SOInet",
        "mode": mode,
        "seed": seed,
        "modalities": list(names),
        "axis_dim": int(state.axis_state.mapped_axes.shape[-1]),
        "active_clusters": state.cluster_state.active_clusters,
        "local_rbm": [model.local_energy.visible_dim, model.local_energy.hidden_dim],
        "global_rbm": [model.global_energy.visible_dim, model.global_energy.hidden_dim],
        "network_state_source": "trained_runtime_tensors",
        "executable_3d_growth": True,
        "architecture_specific_3d_semantics": True,
    }
    generated = [
        path.name for path in (*tables, *figures, *movies, *extra_manifests)
    ]
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
            "source_status": "runtime_derived_training_and_network_state",
            "rbm_source_status": "external_numerical_realization_not_tne_source_law",
            "claim_boundary": "finite trained runtime evidence; not a formal proof substitute",
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
