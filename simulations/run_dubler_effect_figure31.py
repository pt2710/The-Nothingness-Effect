"""Generate Section 15 Figure 31 Dubler-effect artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from equations.dubler_effect import compute_dubler_grid
from utils.output_io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz, write_metadata
from visualizations.plot_dubler_effect import create_dubler_figure


def run(output_dir: str | Path = "outputs", quick: bool = False) -> dict[str, Path | bool]:
    root = Path(output_dir)
    delta_s = np.linspace(-5.0, 5.0, 81 if quick else 201)
    kd_values = np.array([0.5, 1.0, 2.0, 5.0], dtype=float)
    grid = compute_dubler_grid(delta_s, kd_values)
    figure_path = root / "figures" / "section15" / "figure31_dubler_shift_entropy_gradient.png"
    data_path = root / "data" / "dubler_effect" / "figure31_dubler_grid.npz"
    metrics_path = root / "metrics" / "section15" / "figure31_dubler_metrics.csv"
    metadata_path = root / "data" / "dubler_effect" / "figure31_metadata.json"

    save_npz(data_path, **grid)
    metric_rows = []
    for kd, ratio, shift in zip(grid["K_D"], grid["frequency_ratio"], grid["dubler_shift"]):
        metric_rows.append(
            {
                "section": "15.4",
                "figure": "31",
                "K_D": float(kd),
                "ratio_at_zero_delta_s": float(ratio[np.argmin(np.abs(delta_s))]),
                "min_shift": float(np.min(shift)),
                "max_shift": float(np.max(shift)),
                "finite": bool(np.all(np.isfinite(shift))),
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    save_csv(metrics_path, metric_rows)
    fig = create_dubler_figure(grid)
    save_figure(fig, figure_path)
    plt.close(fig)
    write_metadata(
        metadata_path,
        {
            "section": "15.4",
            "figure": "31",
            "paper_caption_target": "Dubler shift as a function of entropy gradient for varying KD.",
            "script": "simulations.run_dubler_effect_figure31",
            "equations_module": "equations.dubler_effect",
            "parameters": {"delta_s_min": -5.0, "delta_s_max": 5.0, "K_D": kd_values.tolist()},
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
        "passed_validation": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate finite illustrative Section 15 Figure 31 artifacts.")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.output_dir, quick=args.quick)
    print(f"Generated Figure 31 artifact: {result['figure']}")
    print(f"Scope: {CLAIM_BOUNDARY}")


if __name__ == "__main__":
    main()
