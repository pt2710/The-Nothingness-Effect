"""Plot Section 19 Figure 7 Elastic-pi ripple artifact."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def create_elastic_pi_ripple_figure(result: dict):
    x = result["x"]
    time = result["time"]
    history = result["history"]
    metrics = result["metrics"]
    indices = [0, len(time) // 3, (2 * len(time)) // 3, len(time) - 1]
    fig, (ax_wave, ax_heat) = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    for index in indices:
        ax_wave.plot(x, history[index], label=f"t={time[index]:.2f}")
    ax_wave.set_title("Figure 7: Elastic-pi ripple after ringdown")
    ax_wave.set_xlabel("x")
    ax_wave.set_ylabel("ripple amplitude")
    ax_wave.grid(True, alpha=0.25)
    ax_wave.legend()
    image = ax_heat.imshow(
        history,
        aspect="auto",
        origin="lower",
        extent=[float(x.min()), float(x.max()), float(time.min()), float(time.max())],
        cmap="RdBu_r",
    )
    ax_heat.set_title(f"Late-time Xi distortion proxy={metrics['late_time_distortion_proxy']:.3f}")
    ax_heat.set_xlabel("x")
    ax_heat.set_ylabel("time")
    fig.colorbar(image, ax=ax_heat, label="amplitude")
    fig.suptitle("Finite illustrative wavefront; not a full GR simulation", fontsize=10)
    return fig
