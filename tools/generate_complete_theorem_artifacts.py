"""Generate aggregate provenance plus complete theorem diagnostic bundles.

Existing domain-specific suite artifacts are preserved. Contracts whose generated
files do not yet include machine-readable traces and an informative static plot are
evaluated with deterministic typed samples. If an already executed A-level suite has
no reusable typed input, its recorded residual/status manifest is replayed into the
diagnostic bundle rather than inventing a domain input. Optional 3-D and
five-coordinate projections are labelled as diagnostics, never physical geometry.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

import numpy as np

from tools.generate_artifact_provenance import (
    _sample_inputs,
    generate as generate_provenance,
)
from tools.theorem_diagnostic_artifacts import materialize_contract_diagnostics
from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import (
    active_contracts,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    ContractEvaluation,
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import (
    AdditiveDerivationInput,
    SpatialClosureInput,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance_authority import (
    provenance_binding_report,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    ClosureStatus,
    ComplexLevel,
    ResidualResult,
)


def _safe(identifier: str) -> str:
    return identifier.replace("::", "__").replace(":", "_")


def _has_suffix(files: list[str], suffix: str) -> bool:
    return any(str(item).lower().endswith(suffix) for item in files)


def _replay_manifest_evaluation(
    identifier: str,
    manifest: dict[str, object],
) -> tuple[dict[str, object], ContractEvaluation]:
    raw_status = str(manifest.get("closure_status", "open"))
    try:
        status = ClosureStatus(raw_status)
    except ValueError:
        status = ClosureStatus.OPEN
    raw_residual = manifest.get("residual_vector", [])
    residual_values = (
        tuple(float(item) for item in raw_residual)
        if isinstance(raw_residual, list)
        else ()
    )
    if not residual_values:
        residual_values = (0.0,)
    tolerances = manifest.get("numeric_tolerances", {})
    tolerance = 0.0
    if isinstance(tolerances, dict) and tolerances:
        tolerance = max(float(item) for item in tolerances.values())
    approximation = manifest.get("approximation_metadata", {})
    exact = (
        bool(approximation.get("exact_semantics", False))
        if isinstance(approximation, dict)
        else False
    )
    passed = status in {ClosureStatus.SATISFIED, ClosureStatus.CLOSED}
    residual = ResidualResult(
        f"{identifier}:suite_manifest_replay",
        residual_values,
        max(tolerance, 0.0),
        passed,
        ClosureStatus.SATISFIED if passed else status,
        {"source": "executed_domain_suite_manifest"},
    )
    value = {
        "parameters": manifest.get("parameters", {}),
        "seed": manifest.get("seed", 0),
        "source": "executed_domain_suite_manifest",
    }
    evaluation = ContractEvaluation(
        identifier,
        np.asarray(residual_values, dtype=float),
        status,
        None,
        residual,
        exact,
        "diagnostic replay of an already executed domain-specific suite manifest",
    )
    return value, evaluation


def _write_provenance_binding(
    aggregate_path: Path,
    binding_path: Path,
) -> dict[str, object]:
    report = provenance_binding_report(aggregate_path)
    total = int(report.get("total_manifests", 0))
    effective_mismatches = int(report.get("effective_source_sha_mismatches", 0))
    if total != 351 or effective_mismatches:
        raise RuntimeError(
            "fresh provenance binding is not release-clean: "
            f"manifests={total} mismatches={effective_mismatches}"
        )
    report["effective_provenance_output"] = aggregate_path.as_posix()
    binding_path.parent.mkdir(parents=True, exist_ok=True)
    binding_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def generate_complete(
    output_root: Path,
    aggregate_path: Path,
    coverage_path: Path,
    binding_path: Path | None = None,
) -> dict[str, object]:
    payload = generate_provenance(output_root, aggregate_path)
    manifests = payload.get("manifests")
    if not isinstance(manifests, list):
        raise RuntimeError("aggregate provenance has no manifest list")

    catalog = {str(contract.complex_id): contract for contract in active_contracts()}
    samples = _sample_inputs()
    enriched = 0
    replayed = 0
    records: list[dict[str, object]] = []

    for manifest in manifests:
        if not isinstance(manifest, dict):
            raise RuntimeError("invalid theorem provenance manifest")
        identifier = str(manifest["theorem_complex_id"])
        files = [str(item) for item in manifest.get("generated_files", [])]
        needs_bundle = not (
            _has_suffix(files, ".npz")
            and _has_suffix(files, ".csv")
            and _has_suffix(files, ".json")
            and _has_suffix(files, ".png")
        )
        if needs_bundle:
            contract = catalog[identifier]
            replay = False
            if identifier in samples:
                value = samples[identifier]
                evaluation = evaluate_contract(contract, value)
            elif contract.level is ComplexLevel.B:
                value = AdditiveDerivationInput(
                    {
                        str(source_id): np.full((6, 4), float(index + 1))
                        for index, source_id in enumerate(contract.source_ids)
                    }
                )
                evaluation = evaluate_contract(contract, value)
            elif contract.level is ComplexLevel.C:
                value = SpatialClosureInput(
                    {
                        str(source_id): np.full((6, 4), float(index + 1))
                        for index, source_id in enumerate(contract.source_ids)
                    }
                )
                evaluation = evaluate_contract(contract, value)
            else:
                value, evaluation = _replay_manifest_evaluation(identifier, manifest)
                replay = True
            removals = (
                []
                if replay
                else [check(value) for check in contract.source_removal_checks]
            )
            destination = output_root / "theorem_diagnostics" / _safe(identifier)
            generated = materialize_contract_diagnostics(
                destination,
                contract,
                value,
                evaluation,
                removals,
            )
            relative = [
                (destination / name).relative_to(output_root).as_posix()
                for name in generated
            ]
            files = sorted(set(files + relative))
            manifest["generated_files"] = files
            approximation = manifest.setdefault("approximation_metadata", {})
            if isinstance(approximation, dict):
                approximation["complete_diagnostic_bundle"] = True
                approximation["diagnostic_projection_claim_boundary"] = (
                    "not physical geometry or empirical validation"
                )
                approximation["diagnostic_source"] = (
                    "executed_domain_suite_manifest"
                    if replay
                    else "typed_contract_evaluation"
                )
            enriched += 1
            replayed += int(replay)

        records.append(
            {
                "theorem_complex_id": identifier,
                "has_json": _has_suffix(files, ".json"),
                "has_csv": _has_suffix(files, ".csv"),
                "has_npz": _has_suffix(files, ".npz"),
                "has_png": _has_suffix(files, ".png"),
                "has_gif": _has_suffix(files, ".gif"),
                "complete_core_bundle": all(
                    (
                        _has_suffix(files, ".json"),
                        _has_suffix(files, ".csv"),
                        _has_suffix(files, ".npz"),
                        _has_suffix(files, ".png"),
                    )
                ),
                "generated_file_count": len(files),
            }
        )

    incomplete = [
        record["theorem_complex_id"]
        for record in records
        if not bool(record["complete_core_bundle"])
    ]
    summary = payload.setdefault("summary", {})
    if not isinstance(summary, dict):
        raise RuntimeError("aggregate provenance summary is invalid")
    summary["complete_core_artifact_bundles"] = len(records) - len(incomplete)
    summary["incomplete_core_artifact_bundles"] = len(incomplete)
    summary["diagnostic_bundles_enriched"] = enriched
    summary["suite_manifest_replays"] = replayed
    summary["generated_npz_traces"] = sum(
        1 for record in records if bool(record["has_npz"])
    )
    summary["generated_2d_or_static_plots"] = sum(
        1 for record in records if bool(record["has_png"])
    )

    aggregate_path.parent.mkdir(parents=True, exist_ok=True)
    aggregate_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    effective_binding_path = (
        binding_path
        if binding_path is not None
        else aggregate_path.with_name("effective_artifact_provenance_binding.json")
    )
    binding_report = _write_provenance_binding(
        aggregate_path,
        effective_binding_path,
    )

    report = {
        "schema_version": "1.1",
        "theorem_complexes": len(records),
        "complete_core_artifact_bundles": len(records) - len(incomplete),
        "incomplete_core_artifact_bundles": len(incomplete),
        "incomplete_ids": incomplete,
        "diagnostic_bundles_enriched": enriched,
        "suite_manifest_replays": replayed,
        "provenance_binding_path": effective_binding_path.as_posix(),
        "provenance_binding_mismatches": binding_report.get(
            "effective_source_sha_mismatches",
            0,
        ),
        "requirements": ["json", "csv", "npz", "png"],
        "claim_boundary": (
            "diagnostic 3-D and five-coordinate projections are not physical geometry, "
            "formal proof, or empirical validation"
        ),
        "records": records,
        "passed": not incomplete,
    }
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if incomplete:
        raise RuntimeError(f"incomplete theorem artifact bundles: {incomplete[:5]}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--aggregate",
        type=Path,
        default=Path("reports/effective_artifact_provenance_manifest.json"),
    )
    parser.add_argument(
        "--coverage",
        type=Path,
        default=Path("reports/theorem_artifact_coverage.json"),
    )
    parser.add_argument("--binding", type=Path)
    arguments = parser.parse_args()
    report = generate_complete(
        arguments.output_root.resolve(),
        arguments.aggregate.resolve(),
        arguments.coverage.resolve(),
        arguments.binding.resolve() if arguments.binding is not None else None,
    )
    print(
        "theorem_artifact_coverage=passed "
        f"rows={report['theorem_complexes']} "
        f"enriched={report['diagnostic_bundles_enriched']} "
        f"replayed={report['suite_manifest_replays']} "
        f"provenance_mismatches={report['provenance_binding_mismatches']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
