"""Plot Section 23 Noether validation artifacts."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def create_kd_flux_figure(flux_result: dict):
    time = flux_result["time"]
    rx = flux_result["rx"]
    metrics = flux_result["metrics"]
    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    ax.plot(time, rx, label="Rx(t)", linewidth=2)
    ax.axhline(rx[0], color="black", linestyle="--", label="Rx(0)")
    ax.set_title(
        "Figure 48: KD flux Rx(t) under fp phase shift\n"
        f"max deviation={metrics['rx_max_deviation']:.3e}"
    )
    ax.set_xlabel("time")
    ax.set_ylabel("KD flux Rx")
    ax.grid(True, alpha=0.25)
    ax.legend()
    return fig


def create_fp_gauss_figure(gauss_result: dict):
    residual = gauss_result["residual"]
    metrics = gauss_result["metrics"]
    fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)
    image = ax.imshow(residual, origin="lower", cmap="magma")
    ax.set_title(
        "Figure 49: fp-Gauss identity check on 128^2 grid\n"
        f"||div(pi_E grad theta)||_inf={metrics['gauss_residual_inf_norm']:.3e}"
    )
    ax.set_xlabel("grid x")
    ax.set_ylabel("grid y")
    fig.colorbar(image, ax=ax, label="residual")
    return fig
