"""Generate trajectory-derived DTQC and bounded Floquet-reference evidence."""

from __future__ import annotations

import csv
from importlib import import_module
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import torch

from ..finite_floquet_reference import (
    CLAIM_BOUNDARY,
    finite_floquet_benchmark,
    simulate_finite_floquet,
)
from ..neural_operator import DTQCInflationLayer


def _decagonal_field(size: int = 32) -> torch.Tensor:
    axis = torch.linspace(-torch.pi, torch.pi, size)
    y, x = torch.meshgrid(axis, axis, indexing="ij")
    field = torch.zeros_like(x)
    for index in range(10):
        angle = 2.0 * math.pi * index / 10.0
        field = field + torch.cos(
            2.4 * (math.cos(angle) * x + math.sin(angle) * y)
        )
    field = field / 10.0
    return 0.25 + (field - field.amin()) / (
        field.amax() - field.amin()
    ).clamp_min(1e-7)


def _save_summary_figure(
    path: Path, initial: np.ndarray, final: np.ndarray
) -> None:
    diffraction = np.fft.fftshift(np.abs(np.fft.fft2(final)))
    figure, axes = plt.subplots(
        1, 3, figsize=(11.2, 3.5), constrained_layout=True
    )
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

    movie = animation.FuncAnimation(
        figure, update, frames=len(frames), interval=180, blit=True
    )
    movie.save(path, writer=animation.PillowWriter(fps=5))
    plt.close(figure)


def _save_floquet_figure(path: Path, canonical, ablation) -> None:
    figure, axes = plt.subplots(
        1, 2, figsize=(10.0, 3.8), constrained_layout=True
    )
    axes[0].plot(canonical.signal.detach().cpu().numpy(), label="near-pi drive")
    axes[0].plot(
        ablation.signal.detach().cpu().numpy(),
        "--",
        label="Flowpoint pulse removed",
    )
    axes[0].set(
        title="Finite spin-chain stroboscopic magnetization",
        xlabel="Floquet period",
        ylabel="mean Z magnetization",
    )
    axes[0].legend()
    axes[0].grid(alpha=0.25)
    axes[1].plot(
        canonical.frequencies.detach().cpu().numpy(),
        canonical.temporal_power.detach().cpu().numpy(),
        label="near-pi drive",
    )
    axes[1].plot(
        ablation.frequencies.detach().cpu().numpy(),
        ablation.temporal_power.detach().cpu().numpy(),
        "--",
        label="pulse removed",
    )
    axes[1].set(
        title="Finite temporal power spectrum",
        xlabel="cycles per period",
        ylabel="power",
    )
    axes[1].legend()
    axes[1].grid(alpha=0.25)
    figure.savefig(path, dpi=155)
    plt.close(figure)


def run(output_dir=None):
    imported = import_module(
        "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture."
        "discrete_time_quasicrystals_in_the_flowpoint"
    )
    output = (
        Path(output_dir)
        if output_dir
        else Path(__file__).resolve().parent / "artifacts"
    )
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
    floquet_path = output / "dtqc_finite_floquet_reference.csv"
    floquet_figure = output / "dtqc_finite_floquet_reference.png"
    floquet_manifest = output / "dtqc_finite_floquet_reference.json"
    manifest_path = output / "dtqc_runtime_manifest.json"
    inventory_path = output / "simulation_inventory.json"
    _save_summary_figure(summary_figure, initial.numpy(), trajectory[-1])
    _save_animation(animation_path, trajectory)

    with trace_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "step",
                "flowpoint_sector",
                "drive_phase",
                "field_mean",
                "field_std",
            ),
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

    benchmark_rows = finite_floquet_benchmark(seeds=(0, 1, 2))
    with floquet_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(benchmark_rows[0]))
        writer.writeheader()
        writer.writerows(benchmark_rows)
    canonical = simulate_finite_floquet(seed=0, flowpoint_enabled=True)
    ablation = simulate_finite_floquet(seed=0, flowpoint_enabled=False)
    _save_floquet_figure(floquet_figure, canonical, ablation)
    floquet_manifest.write_text(
        json.dumps(
            {
                "source_status": "finite_many_body_floquet_reference",
                "spin_count": canonical.spin_count,
                "periods": canonical.periods,
                "seed_count": len(benchmark_rows),
                "unitarity_residual": float(canonical.unitarity_residual),
                "period_two_correlation": float(canonical.period_two_correlation),
                "subharmonic_fraction": float(canonical.subharmonic_fraction),
                "flowpoint_ablation_subharmonic_fraction": float(
                    ablation.subharmonic_fraction
                ),
                "claim_boundary": CLAIM_BOUNDARY,
                "generated_files": [floquet_path.name, floquet_figure.name],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    metrics = {
        name: float(value.detach().cpu())
        for name, value in state.order_parameters.items()
    }
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
                "finite_floquet_reference_manifest": floquet_manifest.name,
                "claim_boundary": (
                    "phenomenological DTQC trajectory plus bounded finite Floquet "
                    "reference; not a formal physical existence proof"
                ),
                "generated_files": [
                    summary_figure.name,
                    animation_path.name,
                    trace_path.name,
                    floquet_path.name,
                    floquet_figure.name,
                    floquet_manifest.name,
                ],
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
                "finite_floquet_reference": floquet_manifest.name,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return inventory_path


if __name__ == "__main__":
    print(run())
