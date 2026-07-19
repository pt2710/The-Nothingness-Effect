"""Training diagnostics for the no-local-RBM comprehensive evaluation."""

from __future__ import annotations

from pathlib import Path
from statistics import mean
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _save(figure: plt.Figure, path: Path) -> None:
    figure.savefig(path, dpi=170, bbox_inches="tight")
    plt.close(figure)


def plot_training_diagnostics(
    plots: Path,
    history: list[dict[str, Any]],
) -> None:
    """Render training diagnostics without implying a removed local RBM."""

    epochs = sorted({int(row["epoch"]) for row in history})
    diagnostics = (
        (
            "modality_weight_evolution.png",
            tuple(key for key in history[0] if key.startswith("weight_")),
            "Modality weight evolution",
            "weight",
        ),
        (
            "cluster_growth.png",
            ("active_clusters", "growth_events"),
            "Cluster growth",
            "count",
        ),
        (
            "global_rbm_free_energy.png",
            ("global_free_energy",),
            "Global RBM free energy after local-RBM removal",
            "free energy",
        ),
        (
            "training_hyperparameters.png",
            ("K_D", "soi_scale", "learning_rate"),
            "Dynamic training parameters",
            "value",
        ),
        (
            "gradient_and_closure.png",
            ("gradient_norm", "train_closure_penalty"),
            "Gradient and closure diagnostics",
            "value",
        ),
    )
    for filename, fields, title, ylabel in diagnostics:
        figure, axis = plt.subplots(figsize=(8, 5), constrained_layout=True)
        for field in fields:
            values = [
                mean(
                    float(row[field])
                    for row in history
                    if int(row["epoch"]) == epoch
                    and row.get(field) not in (None, "")
                )
                for epoch in epochs
            ]
            axis.plot(epochs, values, marker="o", label=field)
        axis.set(title=title, xlabel="epoch", ylabel=ylabel)
        axis.legend()
        _save(figure, plots / filename)
