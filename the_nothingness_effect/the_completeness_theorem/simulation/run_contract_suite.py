"""Generate compact artifacts for all fifteen completeness contracts."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure
from the_nothingness_effect.the_completeness_theorem.contracts import (
    APPENDIX,
    APPENDIX_SHA256,
    CompletenessInput,
    contracts,
)
from the_nothingness_effect.the_completeness_theorem.simulation.godel_boundary import godel_boundary_system
from the_nothingness_effect._runtime.theorem_complex_runtime import ComplexId, SimulationResult
from the_nothingness_effect._runtime.theorem_complex_runtime.artifacts import write_artifact_manifest
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import build_manifest, git_commit


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def fixture() -> CompletenessInput:
    state = np.array([1.0, -0.5, 2.0, 0.75, -1.25, 0.4])
    return CompletenessInput(
        godel_boundary_system(),
        state,
        np.diag([1.0, 1.0, 1.0, 1.0, 0.0, 0.0]),
        np.diag([1.0, -1.0, 1.0, -1.0, 1.0, -1.0]),
        (1, 0, 1, 1, 0, 1),
        np.arange(state.size, dtype=float),
    )


def run_suite(output_dir: str | Path, *, seed: int = 0):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    value = fixture()
    evaluations = [(contract, evaluate_contract(contract, value)) for contract in contracts()]
    records = [
        {
            "theorem_complex_id": str(contract.complex_id),
            "level": contract.level.value,
            "residual_norm": 0.0 if evaluation.residual is None else evaluation.residual.norm,
            "closure_status": evaluation.status.value,
            "exact_semantics": contract.exact_semantics,
        }
        for contract, evaluation in evaluations
    ]
    metrics = save_csv(output / "completeness_contract_metrics.csv", records)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), constrained_layout=True)
    for axis, (_, evaluation) in zip(axes, evaluations[-2:], strict=True):
        closure = evaluation.output
        axis.plot(closure.spatial_domain, closure.local_operator)
        axis.set(title=closure.law_name.replace("_", " "), xlabel="certificate index")
    figure = save_figure(fig, output / "completeness_certificate_closures.png", dpi=160)
    plt.close(fig)
    commit = git_commit(Path(__file__).resolve().parents[3])
    manifests = []
    for contract, evaluation in evaluations:
        residual = () if evaluation.residual is None else evaluation.residual.vector
        result = SimulationResult(
            ComplexId(str(contract.complex_id)),
            evaluation.status,
            {"fixture": "finite-completeness-v1", "state_dimension": len(value.state)},
            seed,
            {"absolute": 1e-10},
            tuple(float(item) for item in residual),
            (metrics.name, figure.name),
            {"formal_proof_substitute": False, "exact_semantics": contract.exact_semantics},
        )
        manifests.append(
            write_artifact_manifest(
                output / f"{contract.complex_id}_manifest.json",
                build_manifest(
                    result,
                    appendix_filename=APPENDIX,
                    appendix_source_sha256=APPENDIX_SHA256,
                    repository_start_commit=START_COMMIT,
                    repository_result_commit=commit,
                    regeneration_command=f"python -m the_nothingness_effect.the_completeness_theorem.simulation.run_contract_suite --output {output.as_posix()}",
                ),
            )
        )
    return {"metrics": metrics, "figure": figure, "manifests": manifests}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts/completeness"))
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    print(run_suite(args.output, seed=args.seed))
