"""Run Elastic-pi ripple simulation and save artifacts in this folder."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from equations.artifact_io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz, write_metadata
from equations.elastic_pi_ripples.elastic_pi_ripples import RippleParams, simulate_elastic_pi_ripple


SCRIPT_DIR = Path(__file__).resolve().parent


def _metadata_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def create_figure(result):
    x = result["x"]
    time = result["time"]
    history = result["history"]
    metrics = result["metrics"]
    indices = [0, len(time) // 3, (2 * len(time)) // 3, len(time) - 1]
    fig, (ax_wave, ax_heat) = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    for index in indices:
        ax_wave.plot(x, history[index], label=f"t={time[index]:.2f}")
    ax_wave.set_title("Figure 7: Elastic-pi ripple after ringdown")
    ax_wave.set_xlabel("x")
    ax_wave.set_ylabel("ripple amplitude")
    ax_wave.grid(True, alpha=0.25)
    ax_wave.legend()
    image = ax_heat.imshow(history, aspect="auto", origin="lower", extent=[float(x.min()), float(x.max()), float(time.min()), float(time.max())], cmap="RdBu_r")
    ax_heat.set_title(f"Late-time Xi distortion proxy={metrics['late_time_distortion_proxy']:.3f}")
    ax_heat.set_xlabel("x")
    ax_heat.set_ylabel("time")
    fig.colorbar(image, ax=ax_heat, label="amplitude")
    fig.suptitle(f"Finite illustrative wavefront; {CLAIM_BOUNDARY}", fontsize=9)
    return fig


def run(output_dir: str | Path | None = None, steps: int | None = None, quick: bool = False) -> dict[str, Path | bool]:
    root = Path(output_dir) if output_dir is not None else SCRIPT_DIR
    params = RippleParams(n=160 if quick else 320, steps=90 if quick else (steps or 260))
    result = simulate_elastic_pi_ripple(params)
    figure_path = root / "figure7_elastic_pi_ripple_ringdown.png"
    data_path = root / "figure7_ripple_history.npz"
    metrics_path = root / "figure7_ripple_metrics.csv"
    metadata_path = root / "figure7_metadata.json"
    save_npz(data_path, x=result["x"], time=result["time"], history=result["history"])
    metrics = result["metrics"]
    save_csv(metrics_path, [{"section": "19.4", "figure": "7", **metrics, "claim_boundary": CLAIM_BOUNDARY}])
    fig = create_figure(result)
    save_figure(fig, figure_path)
    plt.close(fig)
    write_metadata(
        metadata_path,
        {
            "section": "19.4",
            "figure": "7",
            "paper_caption_target": "Propagation and attenuation of an elastic-pi ripple after black-hole ringdown. Waveform distortion/nonlinear term Xi visible at late times.",
            "script": "equations.elastic_pi_ripples.simulation.simulate_elastic_pi_ripples",
            "equations_module": "equations.elastic_pi_ripples.elastic_pi_ripples",
            "parameters": params.__dict__,
            "random_seed": None,
            "output_directory": _metadata_path(root),
        },
    )
    return {"figure": figure_path, "data": data_path, "metrics": metrics_path, "metadata": metadata_path, "passed_validation": metrics["nan_count"] == 0}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Elastic-pi ripple artifacts.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.output_dir, steps=args.steps, quick=args.quick)
    print(f"Generated Elastic-pi ripple simulation artifacts in {result['figure'].parent}")
    print(f"Scope: {CLAIM_BOUNDARY}")


if __name__ == "__main__":
    main()
