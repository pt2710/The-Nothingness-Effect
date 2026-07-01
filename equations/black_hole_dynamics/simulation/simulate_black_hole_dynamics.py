"""Run black-hole dynamics proxy simulation and save artifacts in this folder."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from equations.artifact_io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz, write_metadata
from equations.black_hole_dynamics.black_hole_dynamics import BlackHoleParams, simulate_black_hole_dynamics


SCRIPT_DIR = Path(__file__).resolve().parent


def _metadata_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _horizon_figure(result):
    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    r = result["r"]
    pi_time = result["pi_E_time"]
    horizon = result["horizon_radius"]
    ax.plot(r, pi_time[0], label="initial pi_E")
    ax.plot(r, pi_time[len(pi_time) // 2], label="mid pi_E")
    ax.plot(r, pi_time[-1], label="final pi_E")
    ax.axvline(horizon[0], color="#e45756", linestyle="--", label="initial horizon proxy")
    ax.set_title("Section 18: Elastic-pi entropic horizon proxy")
    ax.set_xlabel("radial coordinate r")
    ax.set_ylabel("normalized Elastic-pi profile")
    ax.grid(True, alpha=0.25)
    ax.legend()
    return fig


def _radiation_figure(result):
    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    ax.plot(result["time"], result["temperature_proxy"], label="temperature proxy")
    ax.plot(result["time"], result["flux_proxy"], label="flux proxy")
    ax.set_title("Section 18: Hawking-like entropic radiation proxy")
    ax.set_xlabel("normalized time")
    ax.set_ylabel("finite proxy value")
    ax.grid(True, alpha=0.25)
    ax.legend()
    return fig


def _memory_figure(result):
    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    ax.plot(result["time"], result["observer_distance"], label="observer-to-horizon distance")
    ax.plot(result["time"], result["memory"], label="memory proxy")
    ax.set_title("Section 18: Observer horizon and memory trace")
    ax.set_xlabel("normalized time")
    ax.set_ylabel("finite proxy value")
    ax.grid(True, alpha=0.25)
    ax.legend()
    return fig


def _feasibility_figure(result):
    metrics = result["metrics"]
    labels = ["grid", "steps", "max T", "max flux", "final memory"]
    values = [metrics["grid_size"], metrics["steps"], metrics["max_temperature_proxy"], metrics["max_flux_proxy"], metrics["final_memory"]]
    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    ax.bar(labels, values, color="#4c78a8")
    ax.set_title("Section 18: Computational feasibility metrics")
    ax.set_ylabel("metric value")
    ax.tick_params(axis="x", rotation=20)
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
