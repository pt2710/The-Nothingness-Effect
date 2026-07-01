"""Shared plotting helpers for empirical comparisons."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from equations.artifact_io import save_figure


def plot_series_comparison(
    x: np.ndarray,
    observed: np.ndarray,
    predicted: np.ndarray,
    output_path: str | Path,
    *,
    title: str,
    xlabel: str,
    ylabel: str,
    uncertainty: np.ndarray | None = None,
    baseline: np.ndarray | None = None,
    observed_label: str = "fixture observable",
    predicted_label: str = "TNE proxy prediction",
    baseline_label: str = "baseline model",
) -> Path:
    fig, ax = plt.subplots(figsize=(7.4, 4.8), constrained_layout=True)
    if uncertainty is not None:
        ax.fill_between(x, observed - uncertainty, observed + uncertainty, color="#9ecae1", alpha=0.35, label="fixture uncertainty")
    ax.plot(x, observed, color="#1f77b4", linewidth=2, marker="o", label=observed_label)
    ax.plot(x, predicted, color="#d62728", linewidth=2, marker="s", label=predicted_label)
    if baseline is not None:
        ax.plot(x, baseline, color="#2ca02c", linewidth=1.8, linestyle="--", label=baseline_label)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    save_figure(fig, output_path, dpi=220)
    plt.close(fig)
    return Path(output_path)


def plot_residuals(
    x: np.ndarray,
    residuals: np.ndarray,
    output_path: str | Path,
    *,
    title: str,
    xlabel: str,
    ylabel: str = "residual",
) -> Path:
    fig, ax = plt.subplots(figsize=(7.4, 4.2), constrained_layout=True)
    ax.axhline(0.0, color="black", linewidth=0.8, linestyle="--")
    ax.plot(x, residuals, color="#9467bd", linewidth=2, marker="o")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.25)
    save_figure(fig, output_path, dpi=220)
    plt.close(fig)
    return Path(output_path)


def plot_grouped_bars(
    labels: list[str],
    observed: np.ndarray,
    predicted: np.ndarray,
    output_path: str | Path,
    *,
    title: str,
    ylabel: str,
) -> Path:
    x = np.arange(len(labels))
    width = 0.36
    fig, ax = plt.subplots(figsize=(7.2, 4.8), constrained_layout=True)
    ax.bar(x - width / 2, observed, width, label="fixture observable", color="#1f77b4")
    ax.bar(x + width / 2, predicted, width, label="TNE proxy", color="#d62728")
    ax.set_xticks(x, labels)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="best")
    save_figure(fig, output_path, dpi=220)
    plt.close(fig)
    return Path(output_path)


def plot_scalar_diagnostics(
    labels: list[str],
    values: list[float],
    output_path: str | Path,
    *,
    title: str,
    ylabel: str,
) -> Path:
    fig, ax = plt.subplots(figsize=(6.4, 4.4), constrained_layout=True)
    ax.bar(labels, values, color=["#d62728", "#1f77b4", "#2ca02c"][: len(labels)])
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y", alpha=0.25)
    save_figure(fig, output_path, dpi=220)
    plt.close(fig)
    return Path(output_path)
