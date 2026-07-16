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
    AdmissibilityData,
    CompletenessInput,
    NoetherData,
    ProtectedTransportData,
    SheafData,
    SplittingData,
    TerminalData,
    contracts,
)
from the_nothingness_effect.the_completeness_theorem.simulation.godel_boundary import (
    godel_boundary_system,
)
from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ComplexId,
    SimulationResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.artifacts import (
    write_artifact_manifest,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import (
    build_manifest,
    git_commit,
)


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def fixture() -> CompletenessInput:
    state = np.array([1.0, -0.5, 2.0, 0.75, 0.0, 0.0])
    closure = np.diag([1.0, 1.0, 1.0, 1.0, 0.0, 0.0])
    parity = np.diag([1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
    identity = np.eye(state.size)
    embedding = np.concatenate((np.eye(4), np.zeros((4, 2))), axis=1)
    certificate = np.array([0.25, -0.5, 0.75, 1.0, 0.0, 0.0])
    return CompletenessInput(
        godel_boundary_system(),
        state,
        closure,
        parity,
        (1, 0, 1, 1, 0, 1),
        np.arange(state.size, dtype=float),
        AdmissibilityData(
            diameter=1.0,
            infinity_istate=np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            infinity_involution=np.diag([-1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
            observation_outcome_bit=0,
            theorem_bit=1,
        ),
        SplittingData(
            update_trajectory=(state.copy(), state.copy(), state.copy()),
            embedding=embedding,
            retraction=embedding.T,
        ),
        ProtectedTransportData(
            protected_state=state,
            pullback_operator=parity,
        ),
        NoetherData(
            global_noether_map=identity,
            local_noether_map=identity,
            constant_injection=identity,
            transgression_map=identity,
            temporal_difference_map=identity,
            boundary_flux=np.zeros(state.size),
            common_codomain="charge-change",
        ),
        SheafData(
            local_certificates=(certificate.copy(), certificate.copy(), certificate.copy()),
            transition_maps=(identity, identity, identity),
            cover_complete=True,
            descent_data_fixed=True,
        ),
        TerminalData(
            admissibility_representation_class=np.array([0.0, 0.0]),
            invariance_conservation_class=np.array([0.0, 0.0]),
            observable_samples=np.array([3.0, 3.0, 3.0]),
            endomorphism_samples=np.array([0.0, 0.0]),
        ),
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
        closure_result = evaluation.output
        axis.plot(closure_result.spatial_domain, closure_result.local_operator)
        axis.set(title=closure_result.law_name.replace("_", " "), xlabel="certificate index")
    figure = save_figure(fig, output / "completeness_certificate_closures.png", dpi=160)
    plt.close(fig)
    commit = git_commit(Path(__file__).resolve().parents[3])
    manifests = []
    for contract, evaluation in evaluations:
        residual = () if evaluation.residual is None else evaluation.residual.vector
        result = SimulationResult(
            ComplexId(str(contract.complex_id)),
            evaluation.status,
            {
                "fixture": "finite-completeness-v2",
                "state_dimension": len(value.state),
                "typed_descent": True,
                "terminal_factorization": True,
            },
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
                    regeneration_command=(
                        "python -m the_nothingness_effect.the_completeness_theorem.simulation.run_contract_suite "
                        f"--output {output.as_posix()}"
                    ),
                ),
            )
        )
    return {"metrics": metrics, "figure": figure, "manifests": manifests}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "artifacts",
    )
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    print(run_suite(args.output, seed=args.seed))
