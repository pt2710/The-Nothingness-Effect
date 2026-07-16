"""Generate deterministic trajectory-derived DTQC evidence.

The simulation keeps the historical ``simulation_inventory.json`` entry point,
but it now also runs the neural operator, saves runtime diagnostics, and renders
an animation from the actual returned trajectory tensors.
"""

from __future__ import annotations

import csv
from importlib import import_module
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import torch

from ..neural_operator import DTQCInflationLayer


def _decagonal_field(size: int = 32) -> torch.Tensor:
    axis = torch.linspace(-torch.pi, torch.pi, size)
    y, x = torch.meshgrid(axis, axis, indexing="ij")
    field = torch.zeros_like(x)
    for index in range(10):
        angle = 2.0 * torch.pi * index / 10.0
        field = field + torch.cos(2.4 * (torch.cos(angle) * x + torch.sin(angle) * y))
    field = field / 10.0
    return 0.25 + (field - field.amin()) / (field.amax() - field.amin()).clamp_min(1e-7)


def _save_summary_figure(path: Path, initial: np.ndarray, final: np.ndarray) -> None:
    diffraction = np.fft.fftshift(np.abs(np.fft.fft2(final)))
    figure, axes = plt.subplots(1, 3, figsize=(11.2, 3.5), constrained_layout=True)
    axes[0].imshow(initial, origin="lower", cmap="viridis")
    axes[0].set_title("initial decagonal carrier")
    axes[1].imshow(final, origin="lower", cmap="viridis")
    axes[1].set_title("transported DTQC state")
    axes[2].imshow(np.log1p(diffraction), origin="lower", cmap="magma")
    axes[2].set_title("final diffraction")
    for axis in axes:
        axis.axis("off")
    figure.savefig(path, dpi=150)
    plt.close(figure)


def _save_animation(path: Path, frames: np.ndarray) -> None:
    figure, axis = plt.subplots(figsize=(5.2, 4.5), constrained_layout=True)
    image = axis.imshow(frames[0], origin="lower", cmap="viridis", animated=True)
    title = axis.set_title("DTQC trajectory — step 1")
    axis.axis("off")

    def update(frame: int):
        image.set_data(frames[frame])
        title.set_text(f"DTQC trajectory — step {frame + 1}/{len(frames)}")
        return image, title

    movie = animation.FuncAnimation(figure, update, frames=len(frames), interval=180, blit=True)
    movie.save(path, writer=animation.PillowWriter(fps=5))
    plt.close(figure)


def run(output_dir=None):
    imported = import_module(
        "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture."
        "discrete_time_quasicrystals_in_the_flowpoint"
    )
    output = Path(output_dir) if output_dir else Path(__file__).resolve().parent / "artifacts"
    output.mkdir(parents=True, exist_ok=True)
    theorem_root = Path(imported.__file__).resolve().parent / "theorem_complex"
    theorem_count = len(list(theorem_root.glob("*/*/manifest.json")))

    torch.manual_seed(0)
    initial = _decagonal_field()
    elastic_gain = 1.0 + 0.12 * initial.mean(dim=-1, keepdim=True)
    with torch.no_grad():
        state = DTQCInflationLayer(time_steps=12, support_fraction=0.55)(
            initial, elastic_gain=elastic_gain
        )
    if state.trajectory is None or state.order_parameters is None:
        raise RuntimeError("DTQC simulation requires a returned temporal trajectory")

    trajectory = state.trajectory.detach().cpu().numpy()
    summary_figure = output / "dtqc_runtime_summary.png"
    animation_path = output / "dtqc_runtime_trajectory.gif"
    trace_path = output / "dtqc_runtime_trace.csv"
    manifest_path = output / "dtqc_runtime_manifest.json"
    inventory_path = output / "simulation_inventory.json"
    _save_summary_figure(summary_figure, initial.numpy(), trajectory[-1])
    _save_animation(animation_path, trajectory)

    with trace_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("step", "flowpoint_sector", "drive_phase", "field_mean", "field_std"),
        )
        writer.writeheader()
        for step, frame in enumerate(trajectory):
            writer.writerow(
                {
                    "step": step,
                    "flowpoint_sector": float(state.flowpoint_sector[step]),
                    "drive_phase": float(state.drive_phase[step]),
                    "field_mean": float(np.mean(frame)),
                    "field_std": float(np.std(frame)),
                }
            )

    metrics = {name: float(value.detach().cpu()) for name, value in state.order_parameters.items()}
    manifest_path.write_text(
        json.dumps(
            {
                "module": (
                    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
                    "discrete_time_quasicrystals_in_the_flowpoint"
                ),
                "source_status": "trajectory_derived_numerical_candidate",
                "seed": 0,
                "time_steps": int(state.trajectory.shape[0]),
                "order_parameters": metrics,
                "input_leakage": float(state.input_leakage.detach().cpu()),
                "generated_files": [summary_figure.name, animation_path.name, trace_path.name],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    inventory_path.write_text(
        json.dumps(
            {
                "module": (
                    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
                    "discrete_time_quasicrystals_in_the_flowpoint"
                ),
                "theorem_complexes": theorem_count,
                "seed": 0,
                "runtime_manifest": manifest_path.name,
                "trajectory_frames": int(state.trajectory.shape[0]),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return inventory_path


if __name__ == "__main__":
    print(run())
