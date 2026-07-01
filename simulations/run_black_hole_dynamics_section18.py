"""Generate Section 18 finite black-hole dynamics support artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from equations.black_hole_dynamics import BlackHoleParams, simulate_black_hole_dynamics
from utils.output_io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz, write_metadata
from visualizations.plot_black_hole_dynamics import (
    create_entropic_horizon_figure,
    create_feasibility_figure,
    create_hawking_like_radiation_figure,
    create_observer_memory_figure,
)


def run(
    output_dir: str | Path = "outputs",
    grid_size: int | None = None,
    steps: int | None = None,
    quick: bool = False,
) -> dict[str, object]:
    root = Path(output_dir)
    params = BlackHoleParams(
        grid_size=96 if quick else (grid_size or 256),
        steps=45 if quick else (steps or 120),
    )
    result = simulate_black_hole_dynamics(params)
    data_path = root / "data" / "black_hole_dynamics" / "section18_black_hole_trace.npz"
    metrics_path = root / "metrics" / "section18" / "section18_black_hole_metrics.csv"
    feasibility_path = root / "metrics" / "section18" / "section18_feasibility_metrics.csv"
    metadata_path = root / "data" / "black_hole_dynamics" / "section18_metadata.json"
    figure_paths = {
        "elastic_pi_entropic_horizon": root
        / "figures"
        / "section18"
        / "section18_elastic_pi_entropic_horizon.png",
        "hawking_like_entropic_radiation": root
        / "figures"
        / "section18"
        / "section18_hawking_like_entropic_radiation.png",
        "observer_horizon_memory": root
        / "figures"
        / "section18"
        / "section18_observer_horizon_memory.png",
        "computational_feasibility": root
        / "figures"
        / "section18"
        / "section18_computational_feasibility.png",
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
    save_csv(
        feasibility_path,
        [
            {"metric": "grid_size", "value": metrics["grid_size"], "claim_boundary": CLAIM_BOUNDARY},
            {"metric": "steps", "value": metrics["steps"], "claim_boundary": CLAIM_BOUNDARY},
            {"metric": "stable", "value": metrics["stable"], "claim_boundary": CLAIM_BOUNDARY},
        ],
    )
    figures = [
        (create_entropic_horizon_figure(result), figure_paths["elastic_pi_entropic_horizon"]),
        (create_hawking_like_radiation_figure(result), figure_paths["hawking_like_entropic_radiation"]),
        (create_observer_memory_figure(result), figure_paths["observer_horizon_memory"]),
        (create_feasibility_figure(result), figure_paths["computational_feasibility"]),
    ]
    for fig, path in figures:
        save_figure(fig, path)
        plt.close(fig)
    write_metadata(
        metadata_path,
        {
            "section": "18.6 and 18.13",
            "figure": "Section 18 computational artifacts",
            "paper_caption_target": (
                "Elastic pi horizon, Hawking-like entropic radiation, observer horizon memory, "
                "and computational feasibility support artifacts."
            ),
            "script": "simulations.run_black_hole_dynamics_section18",
            "equations_module": "equations.black_hole_dynamics",
            "parameters": params.__dict__,
            "random_seed": None,
            "output_files": {
                "figures": {key: str(value.as_posix()) for key, value in figure_paths.items()},
                "data": str(data_path.as_posix()),
                "metrics": str(metrics_path.as_posix()),
                "feasibility_metrics": str(feasibility_path.as_posix()),
            },
        },
    )
    return {
        "figures": figure_paths,
        "data": data_path,
        "metrics": metrics_path,
        "feasibility_metrics": feasibility_path,
        "metadata": metadata_path,
        "passed_validation": bool(metrics["stable"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate finite illustrative Section 18 artifacts.")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--grid-size", type=int, default=None)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.output_dir, grid_size=args.grid_size, steps=args.steps, quick=args.quick)
    print(f"Generated Section 18 artifacts: {len(result['figures'])} figures")
    print(f"Scope: {CLAIM_BOUNDARY}")


if __name__ == "__main__":
    main()
