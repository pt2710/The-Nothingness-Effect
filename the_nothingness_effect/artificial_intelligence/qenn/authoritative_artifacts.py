"""Fresh artifacts for the authoritative QENN dual/product contracts."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import torch

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure
from the_nothingness_effect._runtime.theorem_complex_runtime import ComplexId, SimulationResult
from the_nothingness_effect._runtime.theorem_complex_runtime.artifacts import write_artifact_manifest
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import build_manifest, git_commit

from .authoritative_closure_contracts import A_IDS, APPENDIX, APPENDIX_SHA256, contracts
from .contracts import QENNContractInput


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def fixture(seed: int = 0) -> QENNContractInput:
    generator = torch.Generator().manual_seed(seed)
    axis = torch.linspace(0.0, 2.0 * torch.pi, 16)
    signal = torch.stack(
        (
            torch.sin(axis), torch.cos(axis), torch.sin(2.0 * axis),
            torch.cos(2.0 * axis), 0.5 * torch.sin(axis), 0.5 * torch.cos(axis),
        ),
        dim=-1,
    )
    signal = signal + 0.005 * torch.randn(signal.shape, generator=generator)
    return QENNContractInput(signal, tolerance=1e-6)


def run_suite(output_dir: str | Path, *, seed: int = 0):
    output = Path(output_dir); output.mkdir(parents=True, exist_ok=True)
    value = fixture(seed)
    evaluations = [(contract, evaluate_contract(contract, value)) for contract in contracts()]
    rows = []
    branch_rows = []
    for contract, evaluation in evaluations:
        residual = 0.0 if evaluation.residual is None else evaluation.residual.norm
        rows.append({
            "theorem_complex_id": str(contract.complex_id),
            "level": contract.level.value,
            "closure_status": evaluation.status.value,
            "residual_norm": residual,
            "exact_semantics": contract.exact_semantics,
        })
        if str(contract.complex_id) in A_IDS:
            branch_rows.append({
                "theorem_complex_id": str(contract.complex_id),
                "branch": evaluation.output.branch_name,
                "defect_norm": evaluation.output.defect_norm,
                "classification_residual": residual,
            })
    metrics = save_csv(output / "qenn_authoritative_metrics.csv", rows)
    branches = save_csv(output / "qenn_dual_branch_classification.csv", branch_rows)

    figure_handle, axis = plt.subplots(figsize=(10.5, 4.2), constrained_layout=True)
    positions = range(len(branch_rows))
    axis.bar(positions, [row["defect_norm"] for row in branch_rows])
    axis.axhline(value.tolerance, linestyle="--", linewidth=1.0, label="branch tolerance")
    axis.set(
        title="QENN positive/failure-dual classification",
        xlabel="authoritative A-complex index",
        ylabel="declared defect norm",
        xticks=list(positions),
        xticklabels=[str(index + 1) for index in positions],
    )
    axis.legend()
    figure = save_figure(figure_handle, output / "qenn_authoritative_branch_map.png", dpi=160)
    plt.close(figure_handle)

    commit = git_commit(Path(__file__).resolve().parents[3])
    manifests = []
    for contract, evaluation in evaluations:
        residual = () if evaluation.residual is None else evaluation.residual.vector
        simulation = SimulationResult(
            ComplexId(str(contract.complex_id)),
            evaluation.status,
            {
                "module": "qenn",
                "fixture": "authoritative-dual-product-v1",
                "sample_count": int(value.signal.shape[0]),
                "feature_count": int(value.signal.shape[1]),
            },
            seed,
            {"absolute": value.tolerance},
            tuple(float(item) for item in residual),
            (metrics.name, branches.name, figure.name),
            {
                "exact_semantics": contract.exact_semantics,
                "authority_bound": True,
                "formal_proof_verified": False,
                "evidence_class": "exact_finite_contract" if contract.exact_semantics else "numerical",
            },
        )
        manifests.append(
            write_artifact_manifest(
                output / f"{str(contract.complex_id).replace('::', '__')}_manifest.json",
                build_manifest(
                    simulation,
                    appendix_filename=APPENDIX,
                    appendix_source_sha256=APPENDIX_SHA256,
                    repository_start_commit=START_COMMIT,
                    repository_result_commit=commit,
                    regeneration_command=(
                        "python -m the_nothingness_effect.artificial_intelligence.qenn.simulation.run_contract_suite "
                        f"--output {output.as_posix()}"
                    ),
                ),
            )
        )
    return {"metrics": metrics, "branches": branches, "figure": figure, "manifests": manifests}
