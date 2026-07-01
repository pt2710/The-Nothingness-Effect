"""Plot Section 16 Figure 6 locality-driven spiral artifact."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def create_locality_spiral_figure(history: np.ndarray, metrics: dict[str, float]):
    initial = history[0]
    final = history[-1]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8), constrained_layout=True)
    axes[0].scatter(initial[:, 0], initial[:, 1], s=10, alpha=0.75, color="#4c78a8")
    axes[0].set_title("Initial finite particle field")
    axes[1].scatter(final[:, 0], final[:, 1], s=10, alpha=0.8, color="#f58518")
    axes[1].set_title("Final locality-weighted state")
    stride = max(1, history.shape[1] // 80)
    for particle_path in history[:, ::stride, :].transpose(1, 0, 2):
        axes[2].plot(particle_path[:, 0], particle_path[:, 1], linewidth=0.5, alpha=0.35)
    axes[2].scatter(final[:, 0], final[:, 1], s=6, color="#54a24b", alpha=0.65)
    axes[2].set_title("Trajectory traces")
    for ax in axes:
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True, alpha=0.2)
    fig.suptitle(
        "Figure 6: Simulation of spiral structure emergence under locality-driven gravity\n"
        f"Finite illustrative simulation; spiral order={metrics['spiral_order_parameter']:.3f}",
        fontsize=11,
    )
    return fig
