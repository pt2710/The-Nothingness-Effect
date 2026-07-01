"""Generate Section 16 Figure 6 locality-driven spiral artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from equations.locality_driven_gravity import (
    LocalityGravityParams,
    compute_spiral_metrics,
    simulate_locality_spiral,
)
from utils.output_io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz, write_metadata
from visualizations.plot_locality_spiral import create_locality_spiral_figure


def run(
    output_dir: str | Path = "outputs",
    seed: int = 2710,
    steps: int | None = None,
    quick: bool = False,
) -> dict[str, Path | bool]:
    root = Path(output_dir)
    params = LocalityGravityParams(
        n_particles=120 if quick else 240,
        steps=60 if quick else (steps or 180),
    )
    result = simulate_locality_spiral(params=params, seed=seed)
    metrics = compute_spiral_metrics(result["history"])
    figure_path = root / "figures" / "section16" / "figure6_locality_driven_spiral.png"
    data_path = root / "data" / "locality_driven_gravity" / "figure6_spiral_particles.npz"
    metrics_path = root / "metrics" / "section16" / "figure6_spiral_metrics.csv"
    metadata_path = root / "data" / "locality_driven_gravity" / "figure6_metadata.json"

    save_npz(
        data_path,
        history=result["history"],
        positions=result["positions"],
        velocities=result["velocities"],
    )
    save_csv(metrics_path, [{"section": "16.4", "figure": "6", **metrics, "claim_boundary": CLAIM_BOUNDARY}])
    fig = create_locality_spiral_figure(result["history"], metrics)
    save_figure(fig, figure_path)
    plt.close(fig)
    write_metadata(
        metadata_path,
        {
            "section": "16.4",
            "figure": "6",
            "paper_caption_target": "Simulation of spiral structure emergence under locality-driven gravity.",
            "script": "simulations.run_locality_spiral_figure6",
            "equations_module": "equations.locality_driven_gravity",
            "parameters": params.__dict__,
            "random_seed": seed,
            "output_files": {
                "figure": str(figure_path.as_posix()),
                "data": str(data_path.as_posix()),
                "metrics": str(metrics_path.as_posix()),
            },
        },
    )
    return {
        "figure": figure_path,
        "data": data_path,
        "metrics": metrics_path,
        "metadata": metadata_path,
        "passed_validation": metrics["nan_count"] == 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate finite illustrative Section 16 Figure 6 artifacts.")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--seed", type=int, default=2710)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.output_dir, seed=args.seed, steps=args.steps, quick=args.quick)
    print(f"Generated Figure 6 artifact: {result['figure']}")
    print(f"Scope: {CLAIM_BOUNDARY}")


if __name__ == "__main__":
    main()
