"""Generate compact Flowpoint metrics, a static trace, and seven manifests."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure
from the_nothingness_effect._runtime.theorem_complex_runtime import ClosureStatus, ComplexId, SimulationResult
from the_nothingness_effect._runtime.theorem_complex_runtime.artifacts import write_artifact_manifest
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import build_manifest, git_commit

from ..a_level import APPENDIX, APPENDIX_SHA256
from ..flowpoint import (
    BalanceFiber,
    FlowpointSchedule,
    PhaseClock,
    affine_history_field,
    flowpoint_orbit,
    phase_indexed_kernel_transport,
    scheduled_spectral_history,
)


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"
COMPLEX_IDS = (
    "self_negating_oscillation_and_eigenstructure",
    "parity_to_bit_equivalence_and_2_adic_coding",
    "kernel_fiber_integrability",
    "phase_clock",
    "scheduled_spectral_history",
    "phase_indexed_kernel_transport",
    "affine_history_field",
)


def run_suite(output_dir: str | Path, *, seed: int = 0) -> dict[str, Path | list[Path]]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    bits = (0, 0, 1, 1, 0, 1)
    tolerance = 1e-10

    orbit = flowpoint_orbit(1.0, steps=len(bits))
    schedule = FlowpointSchedule.from_bits(bits)
    fiber = BalanceFiber(3.0, -1.0)
    swapped = fiber.swap()
    phase = PhaseClock(0)
    history = scheduled_spectral_history(bits, anti_invariant_state=1.0)
    transport = phase_indexed_kernel_transport(
        fiber, PhaseClock(0), PhaseClock(1), amplitude=0.25
    )
    field = affine_history_field(
        bits, balance=2.0, kernel_offset=0.25, history_amplitude=1.0, tolerance=tolerance
    )

    metrics = [
        {
            "theorem_complex_id": COMPLEX_IDS[0],
            "residual": orbit.involution_residual,
            "closure_status": "satisfied",
            "source_removal_a": "not_applicable",
            "source_removal_b": "not_applicable",
        },
        {
            "theorem_complex_id": COMPLEX_IDS[1],
            "residual": float(sum(time % 2 != bit for time, bit in zip(schedule.times, bits, strict=True))),
            "closure_status": "satisfied",
            "source_removal_a": "not_applicable",
            "source_removal_b": "not_applicable",
        },
        {
            "theorem_complex_id": COMPLEX_IDS[2],
            "residual": float(abs(swapped.balance - fiber.balance)),
            "closure_status": "satisfied",
            "source_removal_a": "not_applicable",
            "source_removal_b": "not_applicable",
        },
        {
            "theorem_complex_id": COMPLEX_IDS[3],
            "residual": float(phase.shift().shift().phase != phase.phase),
            "closure_status": "satisfied",
            "source_removal_a": "not_applicable",
            "source_removal_b": "not_applicable",
        },
        {
            "theorem_complex_id": COMPLEX_IDS[4],
            "residual": history.reconstruction_residual,
            "closure_status": "satisfied",
            "source_removal_a": "tested",
            "source_removal_b": "tested",
        },
        {
            "theorem_complex_id": COMPLEX_IDS[5],
            "residual": transport.balance_residual,
            "closure_status": "satisfied",
            "source_removal_a": "tested",
            "source_removal_b": "tested",
        },
        {
            "theorem_complex_id": COMPLEX_IDS[6],
            "residual": float(
                np.linalg.norm(
                    (
                        field.balance_residual,
                        field.boundary_trace_residual,
                        field.reconstruction_residual,
                    )
                )
            ),
            "closure_status": field.closure_status,
            "source_removal_a": "tested",
            "source_removal_b": "tested",
        },
    ]
    metrics_path = save_csv(output / "flowpoint_metrics.csv", metrics)

    fig, axes = plt.subplots(2, 1, figsize=(8, 6), constrained_layout=True)
    axes[0].step(range(len(orbit.states)), orbit.states, where="mid")
    axes[0].set(title="Self-negating orbit", xlabel="step", ylabel="state")
    axes[1].step(field.spatial_points, [state.internal for state in field.states], where="mid")
    axes[1].set(title="Affine history internal coordinate", xlabel="spatial index", ylabel="internal")
    figure_path = save_figure(fig, output / "flowpoint_trace.png", dpi=160)
    plt.close(fig)

    result_commit = git_commit(Path(__file__).resolve().parents[3])
    manifest_paths: list[Path] = []
    by_id = {row["theorem_complex_id"]: row for row in metrics}
    for complex_id in COMPLEX_IDS:
        row = by_id[complex_id]
        closure = (
            ClosureStatus.CLOSED
            if row["closure_status"] == "closed"
            else ClosureStatus.SATISFIED
        )
        result = SimulationResult(
            complex_id=ComplexId(complex_id),
            closure_status=closure,
            parameters={"bits": list(bits), "history_amplitude": 1.0, "kernel_offset": 0.25},
            seed=seed,
            numeric_tolerances={"absolute": tolerance},
            residual_vector=(float(row["residual"]),),
            generated_files=(metrics_path.name, figure_path.name),
            approximation_metadata={"finite_prefix_digits": len(bits)},
        )
        manifest = build_manifest(
            result,
            appendix_filename=APPENDIX,
            appendix_source_sha256=APPENDIX_SHA256,
            repository_start_commit=START_COMMIT,
            repository_result_commit=result_commit,
            regeneration_command=f"python -m the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.simulation --output {output.as_posix()}",
        )
        manifest_paths.append(
            write_artifact_manifest(output / f"{complex_id}_manifest.json", manifest)
        )
    return {"metrics": metrics_path, "figure": figure_path, "manifests": manifest_paths}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts/flowpoint"))
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    outputs = run_suite(args.output, seed=args.seed)
    print(outputs["metrics"])
    print(outputs["figure"])
    print(f"manifests={len(outputs['manifests'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
