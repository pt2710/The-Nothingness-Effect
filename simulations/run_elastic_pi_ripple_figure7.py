"""Generate Section 19 Figure 7 Elastic-pi ripple artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from equations.elastic_pi_ripples import RippleParams, simulate_elastic_pi_ripple
from utils.output_io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz, write_metadata
from visualizations.plot_elastic_pi_ripple import create_elastic_pi_ripple_figure


def run(
    output_dir: str | Path = "outputs",
    steps: int | None = None,
    quick: bool = False,
) -> dict[str, Path | bool]:
    root = Path(output_dir)
    params = RippleParams(n=160 if quick else 320, steps=90 if quick else (steps or 260))
    result = simulate_elastic_pi_ripple(params)
    figure_path = root / "figures" / "section19" / "figure7_elastic_pi_ripple_ringdown.png"
    data_path = root / "data" / "elastic_pi_ripples" / "figure7_ripple_history.npz"
    metrics_path = root / "metrics" / "section19" / "figure7_ripple_metrics.csv"
    metadata_path = root / "data" / "elastic_pi_ripples" / "figure7_metadata.json"
    save_npz(data_path, x=result["x"], time=result["time"], history=result["history"])
    metrics = result["metrics"]
    save_csv(metrics_path, [{"section": "19.4", "figure": "7", **metrics, "claim_boundary": CLAIM_BOUNDARY}])
    fig = create_elastic_pi_ripple_figure(result)
    save_figure(fig, figure_path)
    plt.close(fig)
    write_metadata(
        metadata_path,
        {
            "section": "19.4",
            "figure": "7",
            "paper_caption_target": (
                "Propagation and attenuation of an elastic-pi ripple after black-hole ringdown. "
                "Waveform distortion/nonlinear term Xi visible at late times."
            ),
            "script": "simulations.run_elastic_pi_ripple_figure7",
            "equations_module": "equations.elastic_pi_ripples",
            "parameters": params.__dict__,
            "random_seed": None,
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
    parser = argparse.ArgumentParser(description="Generate finite illustrative Section 19 Figure 7 artifacts.")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.output_dir, steps=args.steps, quick=args.quick)
    print(f"Generated Figure 7 artifact: {result['figure']}")
    print(f"Scope: {CLAIM_BOUNDARY}")


if __name__ == "__main__":
    main()
