"""Plot Section 15 Figure 31 Dubler-effect support artifact."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def create_dubler_figure(grid: dict[str, np.ndarray]):
    delta_s = grid["delta_s"]
    kd_values = grid["K_D"]
    shifts = grid["dubler_shift"]

    fig, (ax_curve, ax_heat) = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    for kd, shift in zip(kd_values, shifts):
        ax_curve.plot(delta_s, shift, label=f"K_D={kd:g}", linewidth=2)
    ax_curve.axhline(0.0, color="black", linewidth=0.8, linestyle="--")
    ax_curve.set_title("Figure 31: Dubler shift vs entropy gradient")
    ax_curve.set_xlabel("Entropy gradient delta S")
    ax_curve.set_ylabel("Dubler shift f_A/f_B - 1")
    ax_curve.grid(True, alpha=0.25)
    ax_curve.legend()

    image = ax_heat.imshow(
        shifts,
        aspect="auto",
        origin="lower",
        extent=[float(delta_s.min()), float(delta_s.max()), 0, len(kd_values) - 1],
        cmap="coolwarm",
    )
    ax_heat.set_yticks(range(len(kd_values)), [f"{kd:g}" for kd in kd_values])
    ax_heat.set_title("Finite illustrative shift grid")
    ax_heat.set_xlabel("Entropy gradient delta S")
    ax_heat.set_ylabel("K_D")
    fig.colorbar(image, ax=ax_heat, label="Dubler shift")
    fig.suptitle("Numerical support figure; not a formal proof substitute", fontsize=10)
    return fig
