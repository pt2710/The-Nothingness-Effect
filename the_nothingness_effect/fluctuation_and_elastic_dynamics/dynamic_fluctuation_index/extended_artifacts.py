"""Runtime-derived provenance for recertified DFI A05--A07 source laws."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from the_nothingness_effect._runtime.artifacts.io import save_csv
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

from .contracts import APPENDIX, APPENDIX_SHA256
from .dfi import normalized_dfi, require_finite_dfi
from .extended_contracts import (
    DFIDecompositionInput,
    DFIFlowpointInterfaceInput,
    DFISimulationInput,
)
from .source_contracts import contracts


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def run_suite(output_dir: str | Path, *, seed: int = 0):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    data = np.array(
        [
            [1.0, 2.0, 4.0],
            [2.0, 3.0, 5.0],
            [3.0, 5.0, 8.0],
            [5.0, 8.0, 13.0],
        ]
    )
    scale = 7.0
    expected = np.asarray(
        require_finite_dfi(
            normalized_dfi(data, spectrum_scale=scale)
        ).normalized_entropy,
        dtype=float,
    )
    swap = np.array(
        [
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    inputs = (
        DFIDecompositionInput(data, scale, (2, 0, 1)),
        DFIFlowpointInterfaceInput(data, scale, swap),
        DFISimulationInput(data, scale, expected),
    )
    evaluations = tuple(
        (contract, evaluate_contract(contract, value))
        for contract, value in zip(contracts(), inputs, strict=True)
    )
    metrics = save_csv(
        output / "dfi_extended_source_metrics.csv",
        [
            {
                "theorem_complex_id": str(contract.complex_id),
                "residual_norm": evaluation.residual.norm,
                "closure_status": evaluation.status.value,
                "source_registry": "extended_A",
            }
            for contract, evaluation in evaluations
        ],
    )
    commit = git_commit(Path(__file__).resolve().parents[4])
    manifests = []
    for contract, evaluation in evaluations:
        simulation = SimulationResult(
            ComplexId(str(contract.complex_id)),
            evaluation.status,
            {
                "module": "dfi",
                "fixture": "recertified-source-validation-v1",
                "source_registry": "extended_A",
            },
            seed,
            {"absolute": 1e-10},
            tuple(float(item) for item in evaluation.residual.vector),
            (metrics.name,),
            {
                "exact_semantics": contract.exact_semantics,
                "authority_bound": True,
            },
        )
        manifests.append(
            write_artifact_manifest(
                output / f"{contract.complex_id}_manifest.json",
                build_manifest(
                    simulation,
                    appendix_filename=APPENDIX,
                    appendix_source_sha256=APPENDIX_SHA256,
                    repository_start_commit=START_COMMIT,
                    repository_result_commit=commit,
                    regeneration_command=(
                        "python -m the_nothingness_effect.fluctuation_and_"
                        "elastic_dynamics.dynamic_fluctuation_index.simulation."
                        f"run_contract_suite --output {output.as_posix()}"
                    ),
                ),
            )
        )
    return {"metrics": metrics, "manifests": manifests}
