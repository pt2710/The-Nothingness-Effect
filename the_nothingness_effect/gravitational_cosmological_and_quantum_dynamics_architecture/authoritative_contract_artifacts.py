"""Compact deterministic artifacts for active authoritative physical chains."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure
from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ComplexContract,
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
from the_nothingness_effect._runtime.theorem_complex_runtime.source_samples import (
    sample_inputs,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_artifacts import (
    START_COMMIT,
    fixture,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import (
    APPENDIX,
    APPENDIX_SHA256,
    CANONICAL_MODULE_IMPORTS,
    SPECS,
)


def _sample_count(value: object) -> int:
    for name in (
        "source",
        "coordinate",
        "coordinates",
        "radius",
        "trajectory",
        "data",
        "entropy",
    ):
        candidate = getattr(value, name, None)
        if candidate is not None:
            try:
                return len(candidate)
            except TypeError:
                continue
    return 1


def run_active_suite(
    module: str,
    contracts: Iterable[ComplexContract],
    output_dir: str | Path,
    *,
    seed: int = 0,
):
    spec = SPECS[module]
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    fallback = fixture()
    typed_samples = sample_inputs()
    active = tuple(contracts)
    evaluations = []
    for contract in active:
        value = typed_samples.get(str(contract.complex_id), fallback)
        evaluations.append((contract, value, evaluate_contract(contract, value)))

    records = [
        {
            "theorem_complex_id": str(contract.complex_id),
            "level": contract.level.value,
            "residual_norm": (
                0.0 if evaluation.residual is None else evaluation.residual.norm
            ),
            "closure_status": evaluation.status.value,
            "exact_semantics": contract.exact_semantics,
            "sample_type": type(value).__name__,
        }
        for contract, value, evaluation in evaluations
    ]
    metrics = save_csv(output / f"{module}_contract_metrics.csv", records)
    c_output = next(
        evaluation.output
        for contract, _value, evaluation in evaluations
        if str(contract.complex_id) == spec.c_id
    )
    figure_object, axis = plt.subplots(
        figsize=(8.5, 3.8),
        constrained_layout=True,
    )
    axis.plot(
        c_output.spatial_domain,
        c_output.local_operator,
        label="authoritative closure operator",
    )
    axis.set(
        title=f"{module} authoritative spatial closure",
        xlabel="spatial coordinate",
        ylabel="response",
    )
    axis.legend()
    figure = save_figure(
        figure_object,
        output / f"{module}_spatial_closure.png",
        dpi=160,
    )
    plt.close(figure_object)

    commit = git_commit(Path(__file__).resolve().parents[1])
    manifests = []
    for contract, value, evaluation in evaluations:
        residual = () if evaluation.residual is None else evaluation.residual.vector
        simulation = SimulationResult(
            ComplexId(str(contract.complex_id)),
            evaluation.status,
            {
                "module": module,
                "fixture": "contract-specific-authoritative-v3",
                "sample_type": type(value).__name__,
                "sample_count": _sample_count(value),
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
                        f"python -m {CANONICAL_MODULE_IMPORTS[module]}.simulation."
                        f"run_contract_suite --output {output.as_posix()}"
                    ),
                ),
            )
        )
    return {"metrics": metrics, "figure": figure, "manifests": manifests}
