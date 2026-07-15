"""Run black-hole dynamics proxy simulation and save artifacts in this folder."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from tne_runtime.artifacts.io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz, write_metadata
from equations.black_hole_dynamics.black_hole_dynamics import BlackHoleParams, simulate_black_hole_dynamics


SCRIPT_DIR = Path(__file__).resolve().parent


def _metadata_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _horizon_figure(result):
    fig, ax = plt.subplots(figsize=(8.2, 5.2), constrained_layout=True)
    r = result["r"]
    pi_time = result["pi_E_time"]
    horizon = result["horizon_radius"]
    threshold = float(np.nanmean(pi_time[:, 0]) * 0.0 + 0.36)
    colors = ["#4c78a8", "#72b7b2", "#f58518"]
    labels = ["initial", "mid", "final"]
    indices = [0, len(pi_time) // 2, len(pi_time) - 1]
    for color, label, index in zip(colors, labels, indices):
        ax.plot(r, pi_time[index], color=color, linewidth=2, label=f"{label} pi_E(r)")
        if np.isfinite(horizon[index]):
            y_value = np.interp(horizon[index], r, pi_time[index])
            ax.scatter([horizon[index]], [y_value], color=color, s=35, zorder=4)
            ax.axvline(horizon[index], color=color, linestyle="--", linewidth=1.1, alpha=0.7)
    ax.axhline(threshold, color="#b279a2", linestyle=":", linewidth=1.6, label="threshold")
    ax.set_title("Section 18: Finite illustrative entropic horizon crossing")
    ax.set_xlabel("radial coordinate r")
    ax.set_ylabel("normalized Elastic-pi profile")
    ax.grid(True, alpha=0.25)
    ax.legend()
    return fig


def _radiation_figure(result):
    fig, ax_left = plt.subplots(figsize=(8.2, 5.2), constrained_layout=True)
    ax_right = ax_left.twinx()
    line_temp = ax_left.plot(
        result["time"],
        result["temperature_proxy"],
        color="#4c78a8",
        linewidth=2,
        label="temperature proxy",
    )[0]
    line_flux = ax_right.plot(
        result["time"],
        result["flux_proxy"],
        color="#f58518",
        linewidth=2,
        label="flux proxy",
    )[0]
    ax_left.set_title("Section 18: Hawking-like entropic radiation proxy")
    ax_left.set_xlabel("normalized time")
    ax_left.set_ylabel("temperature proxy", color=line_temp.get_color())
    ax_right.set_ylabel("flux proxy", color=line_flux.get_color())
    ax_left.grid(True, alpha=0.25)
    ax_left.legend([line_temp, line_flux], [line_temp.get_label(), line_flux.get_label()], loc="upper right")
    return fig


def _memory_figure(result):
    fig, ax_left = plt.subplots(figsize=(8.2, 5.2), constrained_layout=True)
    ax_right = ax_left.twinx()
    line_distance = ax_left.plot(
        result["time"],
        result["observer_distance"],
        color="#54a24b",
        linewidth=2,
        label="observer-to-horizon distance",
    )[0]
    line_memory = ax_right.plot(
        result["time"],
        result["memory"],
        color="#e45756",
        linewidth=2,
        label="memory proxy",
    )[0]
    ax_left.set_title("Section 18: Observer horizon and memory trace")
    ax_left.set_xlabel("normalized time")
    ax_left.set_ylabel("observer distance", color=line_distance.get_color())
    ax_right.set_ylabel("memory proxy", color=line_memory.get_color())
    ax_left.grid(True, alpha=0.25)
    ax_left.legend([line_distance, line_memory], [line_distance.get_label(), line_memory.get_label()], loc="upper right")
    return fig


def _feasibility_figure(result):
    metrics = result["metrics"]
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.6), constrained_layout=True)
    comp_labels = ["grid", "steps"]
    comp_values = [metrics["grid_size"], metrics["steps"]]
    proxy_labels = ["max T", "max flux", "final memory"]
    proxy_values = [metrics["max_temperature_proxy"], metrics["max_flux_proxy"], metrics["final_memory"]]
    axes[0].bar(comp_labels, comp_values, color="#4c78a8")
    axes[0].set_title("Computational scale")
    axes[0].set_ylabel("count")
    axes[1].bar(proxy_labels, proxy_values, color=["#72b7b2", "#f58518", "#e45756"])
    axes[1].set_title("Proxy metrics")
    axes[1].set_ylabel("finite proxy value")
    fig.suptitle("Section 18: Computational feasibility summary", fontsize=12)
    return fig


def run(
    output_dir: str | Path | None = None,
    grid_size: int | None = None,
    steps: int | None = None,
    quick: bool = False,
) -> dict[str, object]:
    root = Path(output_dir) if output_dir is not None else SCRIPT_DIR
    params = BlackHoleParams(grid_size=96 if quick else (grid_size or 256), steps=45 if quick else (steps or 120))
    result = simulate_black_hole_dynamics(params)
    data_path = root / "section18_black_hole_trace.npz"
    metrics_path = root / "section18_black_hole_metrics.csv"
    feasibility_path = root / "section18_feasibility_metrics.csv"
    metadata_path = root / "section18_metadata.json"
    figure_paths = {
        "elastic_pi_entropic_horizon": root / "section18_elastic_pi_entropic_horizon.png",
        "hawking_like_entropic_radiation": root / "section18_hawking_like_entropic_radiation.png",
        "observer_horizon_memory": root / "section18_observer_horizon_memory.png",
        "computational_feasibility": root / "section18_computational_feasibility.png",
    }
    save_npz(
        data_path,
        r=result["r"],
        time=result["time"],
        entropy_time=result["entropy_time"],
        pi_E_time=result["pi_E_time"],
        horizon_radius=result["horizon_radius"],
        temperature_proxy=result["temperature_proxy"],
        flux_proxy=result["flux_proxy"],
        observer_path=result["observer_path"],
        observer_distance=result["observer_distance"],
        memory=result["memory"],
    )
    metrics = result["metrics"]
    save_csv(metrics_path, [{"section": "18.6/18.13", **metrics, "claim_boundary": CLAIM_BOUNDARY}])
    save_csv(feasibility_path, [{"metric": key, "value": value, "claim_boundary": CLAIM_BOUNDARY} for key, value in metrics.items()])
    for fig, path in [
        (_horizon_figure(result), figure_paths["elastic_pi_entropic_horizon"]),
        (_radiation_figure(result), figure_paths["hawking_like_entropic_radiation"]),
        (_memory_figure(result), figure_paths["observer_horizon_memory"]),
        (_feasibility_figure(result), figure_paths["computational_feasibility"]),
    ]:
        save_figure(fig, path)
        plt.close(fig)
    write_metadata(
        metadata_path,
        {
            "section": "18.6 and 18.13",
            "paper_caption_target": "Elastic-pi horizon, Hawking-like entropic radiation, observer horizon memory, and computational feasibility support artifacts.",
            "script": "equations.black_hole_dynamics.simulation.simulate_black_hole_dynamics",
            "equations_module": "equations.black_hole_dynamics.black_hole_dynamics",
            "parameters": params.__dict__,
            "random_seed": None,
            "output_directory": _metadata_path(root),
        },
    )
    return {"figures": figure_paths, "data": data_path, "metrics": metrics_path, "feasibility_metrics": feasibility_path, "metadata": metadata_path, "passed_validation": bool(metrics["stable"])}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate black-hole dynamics support artifacts.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--grid-size", type=int, default=None)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.output_dir, grid_size=args.grid_size, steps=args.steps, quick=args.quick)
    print(f"Generated black-hole dynamics simulation artifacts in {result['data'].parent}")
    print(f"Scope: {CLAIM_BOUNDARY}")


if __name__ == "__main__":
    main()
