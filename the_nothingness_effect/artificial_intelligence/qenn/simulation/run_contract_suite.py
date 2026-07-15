"""Generate compact QENN residual artifacts and theorem-level manifests."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import torch

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure
from the_nothingness_effect.artificial_intelligence.qenn.contracts import APPENDIX, APPENDIX_SHA256, QENNContractInput, contracts
from the_nothingness_effect._runtime.theorem_complex_runtime import ComplexId, SimulationResult
from the_nothingness_effect._runtime.theorem_complex_runtime.artifacts import write_artifact_manifest
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import build_manifest, git_commit


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def fixture(seed: int = 0) -> QENNContractInput:
    generator = torch.Generator().manual_seed(seed)
    base = torch.linspace(0.2, 1.4, 16)
    signal = base.repeat(6, 1) + 0.03 * torch.randn((6, 16), generator=generator)
    return QENNContractInput(signal)


def run_suite(output_dir: str | Path, *, seed: int = 0):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    value = fixture(seed)
    evaluations = [(contract, evaluate_contract(contract, value)) for contract in contracts()]
    rows = [{
        "theorem_complex_id": str(contract.complex_id),
        "level": contract.level.value,
        "residual_norm": 0.0 if evaluation.residual is None else evaluation.residual.norm,
        "closure_status": evaluation.status.value,
        "exact_semantics": contract.exact_semantics,
    } for contract, evaluation in evaluations]
    metrics = save_csv(output / "qenn_contract_metrics.csv", rows)
    spatial = evaluations[-1][1].output
    figure_handle, axis = plt.subplots(figsize=(8.5, 3.8), constrained_layout=True)
    axis.plot(spatial.spatial_domain.detach().cpu(), spatial.local_operator.mean(dim=0).detach().cpu())
    axis.set(title="QENN spatial defect-field candidate", xlabel="normalized feature coordinate", ylabel="mean defect energy")
    figure = save_figure(figure_handle, output / "qenn_spatial_closure.png", dpi=160)
    plt.close(figure_handle)
    commit = git_commit(Path(__file__).resolve().parents[4])
    manifests = []
    for contract, evaluation in evaluations:
        residual = () if evaluation.residual is None else evaluation.residual.vector
        simulation = SimulationResult(
            ComplexId(str(contract.complex_id)), evaluation.status,
            {"module": "qenn", "fixture": "qenn-training-field-v1", "batch_size": 6, "feature_count": 16},
            seed, {"absolute": value.tolerance}, tuple(float(item) for item in residual),
            (metrics.name, figure.name), {"exact_semantics": contract.exact_semantics, "device": "cpu"},
        )
        manifests.append(write_artifact_manifest(
            output / f"{contract.complex_id}_manifest.json",
            build_manifest(
                simulation, appendix_filename=APPENDIX, appendix_source_sha256=APPENDIX_SHA256,
                repository_start_commit=START_COMMIT, repository_result_commit=commit,
                regeneration_command=f"python -m the_nothingness_effect.artificial_intelligence.qenn.simulation.run_contract_suite --output {output.as_posix()}",
            ),
        ))
    return {"metrics": metrics, "figure": figure, "manifests": manifests}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--seed", type=int, default=0)
    arguments = parser.parse_args()
    print(run_suite(arguments.output, seed=arguments.seed))
