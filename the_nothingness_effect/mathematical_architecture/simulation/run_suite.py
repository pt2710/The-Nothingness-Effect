"""Generate compact Mathematical Closure evidence and provenance manifests."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure
from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ComplexId,
    SimulationResult,
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.artifacts import (
    write_artifact_manifest,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import (
    build_manifest,
    git_commit,
)

from ..a_level import (
    APPENDIX,
    APPENDIX_SHA256,
    OperationCovarianceInput,
    OrientationInput,
    PhaseCoordinateInput,
    PiApproximationInput,
    pi_approximation,
)
from ..b_level import (
    ApproximationHarmonicInput,
    ArithmeticOrientationInput,
    approximation_harmonic_geometry,
)
from ..c_level import SignedPolarFieldInput, signed_polar_field
from ..contracts import mathematical_closure_contracts


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


def run_suite(
    output_dir: str | Path,
    *,
    seed: int = 0,
) -> dict[str, Path | list[Path]]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    orders = (2, 4, 8, 16, 32)
    approximations = [
        pi_approximation(PiApproximationInput(order)) for order in orders
    ]
    harmonic_input = ApproximationHarmonicInput(
        16,
        (),
        (0.0, 0.25, 0.5, 0.75, 1.0),
        (1.0 + 0j, 0.2 + 0.1j),
        1.0,
    )
    harmonic = approximation_harmonic_geometry(harmonic_input)
    field_input = SignedPolarFieldInput(
        2.0,
        1.0 + 0j,
        16,
        (),
        harmonic_input.times,
        1.0,
    )
    field = signed_polar_field(field_input)
    phase_samples = tuple(
        np.exp(2j * np.pi * np.arange(8) / 8)
    )
    inputs = (
        OrientationInput(3.0),
        OperationCovarianceInput(
            lambda x, y: x * y,
            (2.0, 3.0),
            0,
        ),
        PiApproximationInput(32),
        PhaseCoordinateInput(1.0 + 0j, 0.0, phase_samples),
        ArithmeticOrientationInput(
            lambda x, y: x * y,
            (2.0, 3.0),
            (1, 0),
            0,
        ),
        harmonic_input,
        field_input,
    )
    evaluations = tuple(
        evaluate_contract(contract, source)
        for contract, source in zip(
            mathematical_closure_contracts(),
            inputs,
            strict=True,
        )
    )
    residuals = {
        str(evaluation.complex_id): (
            0.0
            if evaluation.residual is None
            else float(evaluation.residual.norm)
        )
        for evaluation in evaluations
    }
    statuses = {
        str(evaluation.complex_id): evaluation.status
        for evaluation in evaluations
    }
    metrics = [
        {
            "theorem_complex_id": complex_id,
            "residual": residuals[complex_id],
            "closure_status": statuses[complex_id].value,
            "claim_boundary": (
                "finite computational support; not a formal proof substitute"
            ),
        }
        for complex_id in COMPLEX_IDS
    ]
    metrics_path = save_csv(
        output / "mathematical_closure_metrics.csv",
        metrics,
    )
    figure, axes = plt.subplots(
        1,
        2,
        figsize=(9, 3.5),
        constrained_layout=True,
    )
    axes[0].loglog(
        orders,
        [item.actual_error for item in approximations],
        marker="o",
    )
    axes[0].set(
        title="Finite pi residual",
        xlabel="order",
        ylabel="absolute error",
    )
    axes[1].plot(
        field.times,
        [item.real for item in field.field],
        marker="o",
        label="real",
    )
    axes[1].plot(
        field.times,
        [item.imag for item in field.field],
        marker="s",
        label="imag",
    )
    axes[1].set(
        title="Signed-polar field",
        xlabel="spatial time",
    )
    axes[1].legend()
    figure_path = save_figure(
        figure,
        output / "mathematical_closure_trace.png",
        dpi=160,
    )
    plt.close(figure)

    result_commit = git_commit(Path(__file__).resolve().parents[3])
    manifests: list[Path] = []
    for complex_id in COMPLEX_IDS:
        result = SimulationResult(
            ComplexId(complex_id),
            statuses[complex_id],
            {"orders": list(orders), "harmonic_order": 16},
            seed,
            {"absolute": 1e-10},
            (float(residuals[complex_id]),),
            (metrics_path.name, figure_path.name),
            {
                "authority_bound": True,
                "candidate_not_formal_attainment": not mathematical_closure_contracts()[
                    COMPLEX_IDS.index(complex_id)
                ].exact_semantics,
            },
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
                    regeneration_command=(
                        "python -m the_nothingness_effect."
                        "mathematical_architecture.simulation "
                        f"--output {output.as_posix()}"
                    ),
                ),
            )
        )
    return {
        "metrics": metrics_path,
        "figure": figure_path,
        "manifests": manifests,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "artifacts",
    )
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    outputs = run_suite(args.output, seed=args.seed)
    print(outputs["metrics"])
    print(outputs["figure"])
    print(f"manifests={len(outputs['manifests'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
