"""Generate SOInet residual artifacts and provenance manifests."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import torch

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure
from the_nothingness_effect.artificial_intelligence.soinets.contracts import APPENDIX, APPENDIX_SHA256, SOInetContractInput, contracts
from the_nothingness_effect._runtime.theorem_complex_runtime import ComplexId, SimulationResult
from the_nothingness_effect._runtime.theorem_complex_runtime.artifacts import write_artifact_manifest
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import build_manifest, git_commit


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def fixture(seed: int = 0) -> SOInetContractInput:
    generator = torch.Generator().manual_seed(seed)
    position = torch.linspace(0.2, 1.4, 18)
    features = torch.stack((position, position.square(), torch.sin(position), torch.cos(position)), dim=-1)
    modalities = torch.stack([features * (1.0 + 0.1 * index) for index in range(3)])
    modalities = modalities + 0.01 * torch.randn(modalities.shape, generator=generator)
    return SOInetContractInput(modalities)


def run_suite(output_dir: str | Path, *, seed: int = 0):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    value = fixture(seed)
    evaluations = [(contract, evaluate_contract(contract, value)) for contract in contracts()]
    rows = [{
        "theorem_complex_id": str(contract.complex_id), "level": contract.level.value,
        "residual_norm": 0.0 if evaluation.residual is None else evaluation.residual.norm,
        "closure_status": evaluation.status.value, "exact_semantics": contract.exact_semantics,
    } for contract, evaluation in evaluations]
    metrics = save_csv(output / "soinets_contract_metrics.csv", rows)
    spatial = evaluations[-1][1].output
    figure_handle, axis = plt.subplots(figsize=(8.5, 3.8), constrained_layout=True)
    for index, modality in enumerate(spatial.local_operator.mean(dim=-1)):
        axis.plot(spatial.spatial_domain.detach().cpu(), modality.detach().cpu(), label=f"modality {index}")
    axis.set(title="SOInet modality-spatial defect field", xlabel="normalized spatial coordinate", ylabel="mean defect energy")
    axis.legend()
    figure = save_figure(figure_handle, output / "soinets_spatial_closure.png", dpi=160)
    plt.close(figure_handle)
    commit = git_commit(Path(__file__).resolve().parents[4])
    manifests = []
    for contract, evaluation in evaluations:
        residual = () if evaluation.residual is None else evaluation.residual.vector
        simulation = SimulationResult(
            ComplexId(str(contract.complex_id)), evaluation.status,
            {"module": "soinets", "fixture": "modality-field-v1", "modality_count": value.modalities.shape[0], "spatial_samples": value.modalities.shape[1]},
            seed, {"absolute": value.tolerance}, tuple(float(item) for item in residual),
            (metrics.name, figure.name), {"exact_semantics": contract.exact_semantics, "device": "cpu"},
        )
        manifests.append(write_artifact_manifest(
            output / f"{contract.complex_id}_manifest.json",
            build_manifest(
                simulation, appendix_filename=APPENDIX, appendix_source_sha256=APPENDIX_SHA256,
                repository_start_commit=START_COMMIT, repository_result_commit=commit,
                regeneration_command=f"python -m the_nothingness_effect.artificial_intelligence.soinets.simulation.run_contract_suite --output {output.as_posix()}",
            ),
        ))
    return {"metrics": metrics, "figure": figure, "manifests": manifests}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "artifacts")
    parser.add_argument("--seed", type=int, default=0)
    arguments = parser.parse_args()
    print(run_suite(arguments.output, seed=arguments.seed))
