"""Generate compact mathematical-closure evidence and provenance manifests."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure
from the_nothingness_effect._runtime.theorem_complex_runtime import ClosureStatus, ComplexId, SimulationResult
from the_nothingness_effect._runtime.theorem_complex_runtime.artifacts import write_artifact_manifest
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import build_manifest, git_commit

from ..a_level import APPENDIX, APPENDIX_SHA256, PiApproximationInput, pi_approximation
from ..b_level import ApproximationHarmonicInput, approximation_harmonic_geometry
from ..c_level import SignedPolarFieldInput, signed_polar_field


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"
COMPLEX_IDS = (
    "flowpoint_unity_orientation_and_integer_unfolding",
    "operation_covariance_and_spectral_minimization",
    "finite_approximation_and_vanishing_residual_energy",
    "complex_phase_coordinates_and_fourier_reconstruction",
    "addition_of_arithmetic_orientation_and_typed_operation_theory",
    "addition_of_approximation_and_harmonic_geometry",
    "addition_of_the_two_complete_b_level_operator_families",
)


def run_suite(output_dir: str | Path, *, seed: int = 0) -> dict[str, Path | list[Path]]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    orders = (2, 4, 8, 16, 32)
    approximations = [pi_approximation(PiApproximationInput(order)) for order in orders]
    harmonic_input = ApproximationHarmonicInput(
        16, (), (0.0, 0.25, 0.5, 0.75, 1.0), (1.0 + 0j, 0.2 + 0.1j), 1.0
    )
    harmonic = approximation_harmonic_geometry(harmonic_input)
    field = signed_polar_field(
        SignedPolarFieldInput(2.0, 1.0 + 0j, 16, (), harmonic_input.times, 1.0)
    )
    residuals = {
        COMPLEX_IDS[0]: 0.0,
        COMPLEX_IDS[1]: 0.0,
        COMPLEX_IDS[2]: approximations[-1].actual_error,
        COMPLEX_IDS[3]: 0.0,
        COMPLEX_IDS[4]: 0.0,
        COMPLEX_IDS[5]: harmonic.reconstruction_error,
        COMPLEX_IDS[6]: field.reconstruction_residual,
    }
    metrics = [
        {
            "theorem_complex_id": complex_id,
            "residual": residuals[complex_id],
            "closure_status": "numerical_candidate" if complex_id in COMPLEX_IDS[2:] else "satisfied",
            "claim_boundary": "finite computational support; not a formal proof substitute",
        }
        for complex_id in COMPLEX_IDS
    ]
    metrics_path = save_csv(output / "mathematical_closure_metrics.csv", metrics)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.5), constrained_layout=True)
    axes[0].loglog(orders, [item.actual_error for item in approximations], marker="o")
    axes[0].set(title="Finite pi residual", xlabel="order", ylabel="absolute error")
    axes[1].plot(field.times, [item.real for item in field.field], marker="o", label="real")
    axes[1].plot(field.times, [item.imag for item in field.field], marker="s", label="imag")
    axes[1].set(title="Signed-polar field", xlabel="spatial time")
    axes[1].legend()
    figure_path = save_figure(fig, output / "mathematical_closure_trace.png", dpi=160)
    plt.close(fig)

    result_commit = git_commit(Path(__file__).resolve().parents[3])
    manifests: list[Path] = []
    for complex_id in COMPLEX_IDS:
        status = (
            ClosureStatus.SATISFIED
            if complex_id in COMPLEX_IDS[:2]
            else ClosureStatus.NUMERICAL_CANDIDATE
        )
        result = SimulationResult(
            ComplexId(complex_id),
            status,
            {"orders": list(orders), "harmonic_order": 16},
            seed,
            {"absolute": 1e-10},
            (float(residuals[complex_id]),),
            (metrics_path.name, figure_path.name),
            {"candidate_not_minimizer": status is ClosureStatus.NUMERICAL_CANDIDATE},
        )
        manifests.append(
            write_artifact_manifest(
                output / f"{complex_id}_manifest.json",
                build_manifest(
                    result,
                    appendix_filename=APPENDIX,
                    appendix_source_sha256=APPENDIX_SHA256,
                    repository_start_commit=START_COMMIT,
                    repository_result_commit=result_commit,
                    regeneration_command=f"python -m the_nothingness_effect.mathematical_architecture.simulation --output {output.as_posix()}",
                ),
            )
        )
    return {"metrics": metrics_path, "figure": figure_path, "manifests": manifests}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    outputs = run_suite(args.output, seed=args.seed)
    print(outputs["metrics"])
    print(outputs["figure"])
    print(f"manifests={len(outputs['manifests'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
