"""Compact deterministic artifacts for configured physical theorem chains."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from tne_runtime.artifacts.io import save_csv, save_figure
from equations.gravitational_cosmological_quantum_dynamics.contract_runtime import (
    APPENDIX,
    APPENDIX_SHA256,
    FieldLawInput,
    SPECS,
    contracts_for,
)
from tne_runtime.theorem_complex_runtime import ComplexId, SimulationResult
from tne_runtime.theorem_complex_runtime.artifacts import write_artifact_manifest
from tne_runtime.theorem_complex_runtime.contracts import evaluate_contract
from tne_runtime.theorem_complex_runtime.provenance import build_manifest, git_commit


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def fixture() -> FieldLawInput:
    coordinates = np.linspace(0.0, 2.0 * np.pi, 64)
    source = 1.5 + 0.3 * np.sin(coordinates) + 0.2 * np.cos(2.0 * coordinates)
    return FieldLawInput(coordinates, source, scale=2.5, frequency=1.25)


def run_suite(module: str, output_dir: str | Path, *, seed: int = 0):
    spec = SPECS[module]
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    value = fixture()
    evaluations = [(contract, evaluate_contract(contract, value)) for contract in contracts_for(spec)]
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
    metrics = save_csv(output / f"{module}_contract_metrics.csv", records)
    c_output = evaluations[-1][1].output
    fig, ax = plt.subplots(figsize=(8.5, 3.8), constrained_layout=True)
    ax.plot(c_output.spatial_domain, c_output.local_operator, label="local closure operator")
    ax.set(title=f"{module} spatial theorem candidate", xlabel="spatial coordinate", ylabel="response")
    ax.legend()
    figure = save_figure(fig, output / f"{module}_spatial_closure.png", dpi=160)
    plt.close(fig)
    commit = git_commit(Path(__file__).resolve().parents[1])
    manifests = []
    for contract, evaluation in evaluations:
        residual = () if evaluation.residual is None else evaluation.residual.vector
        simulation = SimulationResult(
            ComplexId(str(contract.complex_id)),
            evaluation.status,
            {"module": module, "fixture": "physical-field-v1", "sample_count": len(value.source)},
            seed,
            {"absolute": 1e-10},
            tuple(float(item) for item in residual),
            (metrics.name, figure.name),
            {"exact_semantics": contract.exact_semantics},
        )
        manifests.append(
            write_artifact_manifest(
                output / f"{str(contract.complex_id).replace(':', '_')}_manifest.json",
                build_manifest(
                    simulation,
                    appendix_filename=APPENDIX,
                    appendix_source_sha256=APPENDIX_SHA256,
                    repository_start_commit=START_COMMIT,
                    repository_result_commit=commit,
                    regeneration_command=f"python -m equations.{module}.simulation.run_contract_suite --output {output.as_posix()}",
                ),
            )
        )
    return {"metrics": metrics, "figure": figure, "manifests": manifests}
