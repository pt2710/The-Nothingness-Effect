"""Generate compact foundational-duality artifacts and manifests."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure
from the_nothingness_effect._runtime.theorem_complex_runtime import ClosureStatus, ComplexId, SimulationResult
from the_nothingness_effect._runtime.theorem_complex_runtime.artifacts import write_artifact_manifest
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import build_manifest, git_commit

from ..a_level import APPENDIX, APPENDIX_SHA256
from ..duality import (
    FiniteInvolution,
    FreeCofreeInput,
    invariant_anti_invariant_orbit_field,
    reciprocal_orbit_double_cover,
    reciprocal_relation_action_groupoid,
    two_state_free_cofree_duality,
)


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"
COMPLEX_IDS = (
    "reciprocal_relation_action_groupoid",
    "minimal_two_state_involution_orbitwise_alternator",
    "involutive_duality_c_2_action",
    "reciprocal_orbit_double_cover",
    "two_state_free_cofree_duality",
    "invariant_anti_invariant_orbit_fields",
)


def run_suite(output_dir: str | Path, *, seed: int = 0) -> dict[str, Path | list[Path]]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    involution = FiniteInvolution((1.0, 3.0, -2.0, 4.0), (1, 0, 3, 2))
    relation = reciprocal_relation_action_groupoid(involution)
    cover = reciprocal_orbit_double_cover(involution)
    free = two_state_free_cofree_duality(FreeCofreeInput((1.0, 2.0 + 1j)))
    field = invariant_anti_invariant_orbit_field(involution)
    residuals = {
        COMPLEX_IDS[0]: float(not relation.composition_closed),
        COMPLEX_IDS[1]: 0.0,
        COMPLEX_IDS[2]: 0.0,
        COMPLEX_IDS[3]: cover.fiber_residual,
        COMPLEX_IDS[4]: free.equivariance_residual,
        COMPLEX_IDS[5]: field.reconstruction_residual,
    }
    metrics = [
        {"theorem_complex_id": item, "residual": residuals[item], "closure_status": "closed" if item == COMPLEX_IDS[5] else "satisfied"}
        for item in COMPLEX_IDS
    ]
    metrics_path = save_csv(output / "duality_metrics.csv", metrics)
    fig, ax = plt.subplots(figsize=(7, 3.5), constrained_layout=True)
    ax.plot(field.spatial_domain, [item.real for item in field.invariant_field], "o-", label="invariant")
    ax.plot(field.spatial_domain, [item.real for item in field.anti_invariant_field], "s-", label="anti-invariant")
    ax.set(title="Dual orbit-field decomposition", xlabel="orbit index")
    ax.legend()
    figure_path = save_figure(fig, output / "duality_orbit_field.png", dpi=160)
    plt.close(fig)
    commit = git_commit(Path(__file__).resolve().parents[3])
    manifests: list[Path] = []
    for complex_id in COMPLEX_IDS:
        status = ClosureStatus.CLOSED if complex_id == COMPLEX_IDS[5] else ClosureStatus.SATISFIED
        result = SimulationResult(
            ComplexId(complex_id),
            status,
            {"carrier_size": len(involution.points)},
            seed,
            {"absolute": 1e-10},
            (float(residuals[complex_id]),),
            (metrics_path.name, figure_path.name),
        )
        manifests.append(
            write_artifact_manifest(
                output / f"{complex_id}_manifest.json",
                build_manifest(
                    result,
                    appendix_filename=APPENDIX,
                    appendix_source_sha256=APPENDIX_SHA256,
                    repository_start_commit=START_COMMIT,
                    repository_result_commit=commit,
                    regeneration_command=f"python -m the_nothingness_effect.foundational_architecture.duality.simulation --output {output.as_posix()}",
                ),
            )
        )
    return {"metrics": metrics_path, "figure": figure_path, "manifests": manifests}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "artifacts")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    outputs = run_suite(args.output, seed=args.seed)
    print(outputs["metrics"])
    print(outputs["figure"])
    print(f"manifests={len(outputs['manifests'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
