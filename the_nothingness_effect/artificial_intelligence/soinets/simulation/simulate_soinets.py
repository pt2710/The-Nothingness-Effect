"""Generate SOInet metrics and visual evidence from actual model states."""

from __future__ import annotations

import csv
from importlib import import_module
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import torch

from ..evaluation import evaluate_classification, forward_classification_batch
from ..model import SOInetModel
from ..training import fit_classification


def _dataset(seed: int = 0) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    generator = torch.Generator().manual_seed(seed)
    node_axis = torch.linspace(0.15, 1.0, 6)
    qenn_samples = []
    pgqenn_samples = []
    for label in range(3):
        phase = float(label) * torch.pi / 3.0
        features = torch.stack(
            (
                node_axis,
                node_axis.square(),
                torch.sin((label + 1.0) * node_axis + phase),
                torch.cos((label + 1.0) * node_axis - phase),
            ),
            dim=-1,
        )
        noise = 0.005 * torch.randn(features.shape, generator=generator)
        qenn_samples.append(features + noise)
        pgqenn_samples.append(1.08 * features + 0.005 * torch.randn(features.shape, generator=generator))
    return torch.stack(qenn_samples), torch.stack(pgqenn_samples), torch.arange(3)


def _save_figure(
    path: Path,
    evaluation,
    meta_states: np.ndarray,
    adjacency: np.ndarray,
) -> None:
    figure, axes = plt.subplots(1, 3, figsize=(12.0, 3.8), constrained_layout=True)
    image = axes[0].imshow(evaluation.probabilities.detach().cpu().numpy(), vmin=0.0, vmax=1.0, cmap="viridis")
    axes[0].set(title="SOInet task probabilities", xlabel="class", ylabel="sample")
    figure.colorbar(image, ax=axes[0])
    hidden = axes[1].imshow(meta_states, aspect="auto", cmap="coolwarm")
    axes[1].set(title="Runtime meta states", xlabel="hidden coordinate", ylabel="sample")
    figure.colorbar(hidden, ax=axes[1])
    graph = axes[2].imshow(adjacency, vmin=0.0, vmax=max(1.0, float(adjacency.max())), cmap="magma")
    axes[2].set(title="Runtime meta adjacency", xlabel="state", ylabel="state")
    figure.colorbar(graph, ax=axes[2])
    figure.savefig(path, dpi=155)
    plt.close(figure)


def _save_animation(path: Path, meta_states: np.ndarray, probabilities: np.ndarray) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(8.4, 3.5), constrained_layout=True)
    hidden = axes[0].imshow(meta_states[:1], aspect="auto", cmap="coolwarm", animated=True)
    probability = axes[1].bar(np.arange(probabilities.shape[1]), probabilities[0])
    axes[0].set(title="Observed SOInet meta state", xlabel="hidden coordinate", ylabel="sample")
    axes[1].set(title="Observation/collapse probabilities", xlabel="class", ylim=(0.0, 1.0))

    def update(frame: int):
        hidden.set_data(meta_states[frame : frame + 1])
        axes[0].set_ylabel(f"sample {frame}")
        for bar, value in zip(probability, probabilities[frame], strict=True):
            bar.set_height(float(value))
        return (hidden, *probability)

    movie = animation.FuncAnimation(
        figure,
        update,
        frames=len(meta_states),
        interval=450,
        blit=False,
    )
    movie.save(path, writer=animation.PillowWriter(fps=2))
    plt.close(figure)


def run(output_dir=None):
    imported = import_module("the_nothingness_effect.artificial_intelligence.soinets")
    output = Path(output_dir) if output_dir else Path(__file__).resolve().parent / "artifacts"
    output.mkdir(parents=True, exist_ok=True)
    theorem_root = Path(imported.__file__).resolve().parent / "theorem_complex"
    theorem_count = len(list(theorem_root.glob("*/*/manifest.json")))

    torch.manual_seed(0)
    qenn, pgqenn, targets = _dataset()
    model = SOInetModel(4, 6, 3, qenn_count=1, pgqenn_count=1)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    history = fit_classification(
        model,
        optimizer,
        (qenn, pgqenn, targets),
        (qenn, pgqenn, targets),
        epochs=1,
        closure_weight=0.01,
    )
    evaluation = evaluate_classification(model, qenn, pgqenn, targets)
    model.eval()
    with torch.no_grad():
        _, _, outputs = forward_classification_batch(model, qenn, pgqenn)
    meta_states = torch.stack([item.meta_state for item in outputs]).detach().cpu().numpy()
    adjacency = outputs[0].meta_adjacency.detach().cpu().numpy()
    probabilities = evaluation.probabilities.detach().cpu().numpy()

    history_path = output / "soinets_runtime_training.csv"
    sample_path = output / "soinets_runtime_predictions.csv"
    figure_path = output / "soinets_runtime_state.png"
    animation_path = output / "soinets_runtime_state.gif"
    manifest_path = output / "soinets_runtime_manifest.json"
    inventory_path = output / "simulation_inventory.json"

    with history_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(history[0].__dict__))
        writer.writeheader()
        writer.writerows(item.__dict__ for item in history)
    with sample_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("sample", "target", "prediction", "confidence", "closure_status"),
        )
        writer.writeheader()
        for index in range(len(targets)):
            writer.writerow(
                {
                    "sample": index,
                    "target": int(targets[index]),
                    "prediction": int(evaluation.predictions[index]),
                    "confidence": float(evaluation.probabilities[index].max()),
                    "closure_status": evaluation.closure_statuses[index],
                }
            )

    _save_figure(figure_path, evaluation, meta_states, adjacency)
    _save_animation(animation_path, meta_states, probabilities)
    manifest_path.write_text(
        json.dumps(
            {
                "module": "the_nothingness_effect/artificial_intelligence/soinets",
                "source_status": "runtime_derived_architecture_coupled_fixture",
                "architecture_coupled_metrics": True,
                "seed": 0,
                "task_metrics": {
                    "loss": float(evaluation.loss),
                    "accuracy": float(evaluation.accuracy),
                    "mean_confidence": float(evaluation.mean_confidence),
                },
                "closure_statuses": list(evaluation.closure_statuses),
                "generated_files": [
                    history_path.name,
                    sample_path.name,
                    figure_path.name,
                    animation_path.name,
                ],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    inventory_path.write_text(
        json.dumps(
            {
                "module": "the_nothingness_effect/artificial_intelligence/soinets",
                "theorem_complexes": theorem_count,
                "seed": 0,
                "runtime_manifest": manifest_path.name,
                "architecture_coupled_metrics": True,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return inventory_path


if __name__ == "__main__":
    print(run())
