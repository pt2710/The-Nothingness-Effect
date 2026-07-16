"""Deterministic theorem artifacts for DFI, pDFI, Elastic-pi, and its norm."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure
from the_nothingness_effect._runtime.theorem_complex_runtime import ComplexId, SimulationResult
from the_nothingness_effect._runtime.theorem_complex_runtime.artifacts import write_artifact_manifest
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import build_manifest, git_commit


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"
APPENDIX = "appendix_tne_fluctuation_and_elastic_dynamics.tex"
APPENDIX_SHA256 = "e37d7583d56287f0cc48d819afadf06ab7f1d8cbccce1790c8b8f18f1b96f30b"


def _contracts_and_input(category: str) -> tuple[tuple[Any, ...], Any]:
    if category == "dfi":
        from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.contracts import (
            ApplicabilityInput,
            DFIInput,
            DFIRescalingInput,
            SpatialDFIInput,
            contracts,
        )

        data = np.array([[1.0, 2.0, 4.0], [2.0, 3.0, 5.0], [3.0, 5.0, 8.0], [5.0, 8.0, 13.0]])

        def input_for(identifier: str):
            if identifier in {"dfi_spectrum_normalized_existence_and_normalization_breakdown", "dfi_entropic_fluctuation_encoding_and_fluctuation_divergence"}:
                return DFIInput(data, 7.0)
            if identifier in {"dfi_invariance_under_soi_rescaling_and_spurious_scale_dependence", "scale_normalized_dfi_homogeneity_invariant"}:
                return DFIRescalingInput(data, 7.0, 19.0)
            if identifier in {
                "dfi_adaptive_applicability_and_contextual_instability",
                "entropic_applicability_response_operator",
            }:
                return ApplicabilityInput(data, 7.0, 0.01)
            return SpatialDFIInput(data, 7.0)

        return contracts(), input_for
    if category == "elastic_pi":
        from the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.contracts import ElasticPiInput, contracts

        value = ElasticPiInput(np.array([0.2, 0.7, 1.8, 3.4, 5.5]), 2.5, np.linspace(0.0, 1.0, 5))
        return contracts(), lambda _identifier: value
    if category == "pdfi":
        from the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.contracts import ParityDFIInput, contracts

        value = ParityDFIInput(np.array([7, 22, 11, 34, 17, 52]), 2.5, 100.0)
        return contracts(), lambda _identifier: value
    if category == "elastic_pi_norm":
        from the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi_norm.contracts import ElasticPiNormInput, contracts

        value = ElasticPiNormInput(np.array([1, 3, 8, 5, 12]), np.array([0.2, 0.7, 1.6, 2.1, 3.4]), 4.0, anchored=False)
        return contracts(), lambda _identifier: value
    raise ValueError(f"unknown fluctuation artifact category {category!r}")


def run_suite(category: str, output_dir: str | Path, *, seed: int = 0) -> dict[str, Path | list[Path]]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    np.random.default_rng(seed)  # seed is recorded even though these fixtures are deterministic
    contracts, input_for = _contracts_and_input(category)
    records: list[dict[str, Any]] = []
    evaluations = []
    for contract in contracts:
        evaluation = evaluate_contract(contract, input_for(str(contract.complex_id)))
        evaluations.append((contract, evaluation))
        records.append(
            {
                "theorem_complex_id": str(contract.complex_id),
                "level": contract.level.value,
                "residual_norm": 0.0 if evaluation.residual is None else evaluation.residual.norm,
                "closure_status": evaluation.status.value,
                "exact_semantics": contract.exact_semantics,
                "source_count": len(contract.source_ids),
            }
        )
    metrics_path = save_csv(output / f"{category}_contract_metrics.csv", records)
    fig, ax = plt.subplots(figsize=(9, 3.8), constrained_layout=True)
    ax.bar(np.arange(len(records)), [item["residual_norm"] for item in records])
    ax.set(title=f"{category} theorem residuals", xlabel="contract index", ylabel="residual norm")
    figure_path = save_figure(fig, output / f"{category}_contract_residuals.png", dpi=160)
    plt.close(fig)
    commit = git_commit(Path(__file__).resolve().parents[1])
    manifests: list[Path] = []
    for contract, evaluation in evaluations:
        residual = () if evaluation.residual is None else evaluation.residual.vector
        simulation = SimulationResult(
            ComplexId(str(contract.complex_id)),
            evaluation.status,
            {"category": category, "fixture": "deterministic-contract-v1"},
            seed,
            {"absolute": 1e-10},
            tuple(float(item) for item in residual),
            (metrics_path.name, figure_path.name),
            {"exact_semantics": contract.exact_semantics},
        )
        module_name = {
            "dfi": "the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index",
            "pdfi": "the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index",
            "elastic_pi": "the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi",
            "elastic_pi_norm": "the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi_norm",
        }[category]
        manifests.append(
            write_artifact_manifest(
                output / f"{contract.complex_id}_manifest.json",
                build_manifest(
                    simulation,
                    appendix_filename=APPENDIX,
                    appendix_source_sha256=APPENDIX_SHA256,
                    repository_start_commit=START_COMMIT,
                    repository_result_commit=commit,
                    regeneration_command=f"python -m {module_name}.simulation.run_contract_suite --output {output.as_posix()}",
                ),
            )
        )
    return {"metrics": metrics_path, "figure": figure_path, "manifests": manifests}
