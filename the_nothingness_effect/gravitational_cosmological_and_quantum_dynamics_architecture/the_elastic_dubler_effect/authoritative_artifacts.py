"""Compact artifacts for the exact Elastic-Dubler core chain."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

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
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_artifacts import (
    START_COMMIT,
    fixture,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import (
    APPENDIX,
    APPENDIX_SHA256,
    SPECS,
    contracts_for,
)

from .potential_current_contract import contract as exact_c_contract


SPEC = SPECS["elastic_dubler_effect"]


def _core_contracts():
    return tuple(
        item for item in contracts_for(SPEC)
        if str(item.complex_id) != SPEC.c_id
    ) + (exact_c_contract(),)


def run_suite(output_dir: str | Path, *, seed: int = 0):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    value = fixture()
    contracts = _core_contracts()
    evaluations = [
        (contract, evaluate_contract(contract, value)) for contract in contracts
    ]
    records = [
        {
            "theorem_complex_id": str(contract.complex_id),
            "level": contract.level.value,
            "residual_norm": (
                0.0 if evaluation.residual is None else evaluation.residual.norm
            ),
            "closure_status": evaluation.status.value,
            "exact_semantics": contract.exact_semantics,
        }
        for contract, evaluation in evaluations
    ]
    metrics = save_csv(output / "elastic_dubler_effect_contract_metrics.csv", records)
    c_output = next(
        evaluation.output
        for contract, evaluation in evaluations
        if str(contract.complex_id) == SPEC.c_id
    )
    figure_object, axis = plt.subplots(
        figsize=(8.5, 3.8),
        constrained_layout=True,
    )
    axis.plot(c_output.spatial_domain, c_output.potential, label="potential")
    axis.plot(c_output.spatial_domain, c_output.local_operator, label="current")
    axis.set(
        title="Elastic-Dubler potential-current closure",
        xlabel="spatial coordinate",
        ylabel="response",
    )
    axis.legend()
    figure = save_figure(
        figure_object,
        output / "elastic_dubler_effect_spatial_closure.png",
        dpi=160,
    )
    plt.close(figure_object)

    commit = git_commit(Path(__file__).resolve().parents[2])
    manifests = []
    for contract, evaluation in evaluations:
        residual = () if evaluation.residual is None else evaluation.residual.vector
        simulation = SimulationResult(
            ComplexId(str(contract.complex_id)),
            evaluation.status,
            {
                "module": "elastic_dubler_effect",
                "fixture": "physical-field-v2",
                "sample_count": len(value.source),
            },
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
                    regeneration_command=(
                        "python -m the_nothingness_effect."
                        "gravitational_cosmological_and_quantum_dynamics_architecture."
                        "the_elastic_dubler_effect.simulation.run_contract_suite "
                        f"--output {output.as_posix()}"
                    ),
                ),
            )
        )
    return {"metrics": metrics, "figure": figure, "manifests": manifests}
