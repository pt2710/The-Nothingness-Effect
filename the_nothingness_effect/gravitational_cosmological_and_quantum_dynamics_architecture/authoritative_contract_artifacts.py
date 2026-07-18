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
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_black_hole import (
    sample_inputs as black_hole_samples,
)
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_elastic_dubler import (
    sample_inputs as elastic_dubler_samples,
)
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_elastic_pi_ripples import (
    sample_inputs as elastic_pi_ripple_samples,
)
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_locality_gravity import (
    sample_inputs as locality_gravity_samples,
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


def _physical_samples() -> dict[str, object]:
    """Return only physical typed samples that have no optional AI backend."""

    samples: dict[str, object] = {}
    for factory in (
        elastic_dubler_samples,
        locality_gravity_samples,
        black_hole_samples,
        elastic_pi_ripple_samples,
    ):
        samples.update(factory())
    return samples


def _sample_for_contract(
    contract: ComplexContract,
    typed_samples: dict[str, object],
    fallback: object,
) -> object:
    direct = typed_samples.get(str(contract.complex_id))
    accepted = contract.domain.python_types
    if direct is not None and (not accepted or isinstance(direct, accepted)):
        return direct
    if not accepted or isinstance(fallback, accepted):
        return fallback
    for sample in typed_samples.values():
        if isinstance(sample, accepted):
            return sample
    return fallback


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
    typed_samples = _physical_samples()
    active = tuple(contracts)
    evaluations = []
    for contract in active:
        value = _sample_for_contract(contract, typed_samples, fallback)
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
                "fixture": "contract-specific-authoritative-v5",
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
