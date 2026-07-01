"""Plots for finite Section 18 black-hole dynamics artifacts."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def create_entropic_horizon_figure(result: dict):
    r = result["r"]
    pi_time = result["pi_E_time"]
    horizon = result["horizon_radius"]
    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    ax.plot(r, pi_time[0], label="initial pi_E")
    ax.plot(r, pi_time[len(pi_time) // 2], label="mid pi_E")
    ax.plot(r, pi_time[-1], label="final pi_E")
    ax.axvline(horizon[0], color="#e45756", linestyle="--", label="initial horizon proxy")
    ax.set_title("Section 18: Elastic pi and entropic horizon proxy")
    ax.set_xlabel("radial coordinate r")
    ax.set_ylabel("Elastic pi profile")
    ax.grid(True, alpha=0.25)
    ax.legend()
    return fig


def create_hawking_like_radiation_figure(result: dict):
    time = result["time"]
    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    ax.plot(time, result["temperature_proxy"], label="temperature proxy", linewidth=2)
    ax.plot(time, result["flux_proxy"], label="flux proxy", linewidth=2)
    ax.set_title("Section 18: Hawking-like entropic radiation proxy")
    ax.set_xlabel("normalized time")
    ax.set_ylabel("finite proxy value")
    ax.grid(True, alpha=0.25)
    ax.legend()
    return fig


def create_observer_memory_figure(result: dict):
    time = result["time"]
    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    ax.plot(time, result["observer_distance"], label="observer-to-horizon distance")
    ax.plot(time, result["memory"], label="gravitational memory proxy")
    ax.set_title("Section 18: Observer horizon and memory trace")
    ax.set_xlabel("normalized time")
    ax.set_ylabel("finite proxy value")
    ax.grid(True, alpha=0.25)
    ax.legend()
    return fig


def create_feasibility_figure(result: dict):
    metrics = result["metrics"]
    labels = ["grid", "steps", "max T", "max flux", "final memory"]
    values = [
        metrics["grid_size"],
        metrics["steps"],
        metrics["max_temperature_proxy"],
        metrics["max_flux_proxy"],
        metrics["final_memory"],
    ]
    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    ax.bar(labels, values, color="#4c78a8")
    ax.set_title("Section 18: Computational feasibility metrics")
    ax.set_ylabel("metric value")
    ax.tick_params(axis="x", rotation=20)
    return fig
