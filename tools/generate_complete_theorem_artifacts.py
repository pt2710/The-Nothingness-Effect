"""Generate aggregate provenance plus complete theorem diagnostic bundles.

Existing domain-specific suite artifacts are preserved.  Contracts whose generated
files do not yet include machine-readable traces and an informative static plot are
evaluated with the same deterministic typed samples used by provenance generation
and receive a compact JSON/CSV/NPZ/2-D diagnostic bundle.  Optional 3-D and
five-coordinate projections are labelled as diagnostics, never physical geometry.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

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
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import (
    AdditiveDerivationInput,
    SpatialClosureInput,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ComplexLevel


def _safe(identifier: str) -> str:
    return identifier.replace("::", "__").replace(":", "_")


def _has_suffix(files: list[str], suffix: str) -> bool:
    return any(str(item).lower().endswith(suffix) for item in files)


def generate_complete(
    output_root: Path,
    aggregate_path: Path,
    coverage_path: Path,
) -> dict[str, object]:
    payload = generate_provenance(output_root, aggregate_path)
    manifests = payload.get("manifests")
    if not isinstance(manifests, list):
        raise RuntimeError("aggregate provenance has no manifest list")

    catalog = {str(contract.complex_id): contract for contract in active_contracts()}
    samples = _sample_inputs()
    enriched = 0
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
            if identifier in samples:
                value = samples[identifier]
            elif contract.level is ComplexLevel.B:
                value = AdditiveDerivationInput(
                    {
                        str(source_id): np.full((6, 4), float(index + 1))
                        for index, source_id in enumerate(contract.source_ids)
                    }
                )
            elif contract.level is ComplexLevel.C:
                value = SpatialClosureInput(
                    {
                        str(source_id): np.full((6, 4), float(index + 1))
                        for index, source_id in enumerate(contract.source_ids)
                    }
                )
            else:
                raise RuntimeError(
                    f"A-level contract lacks deterministic typed sample: {identifier}"
                )
            evaluation = evaluate_contract(contract, value)
            removals = [check(value) for check in contract.source_removal_checks]
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
            enriched += 1

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
    report = {
        "schema_version": "1.0",
        "theorem_complexes": len(records),
        "complete_core_artifact_bundles": len(records) - len(incomplete),
        "incomplete_core_artifact_bundles": len(incomplete),
        "incomplete_ids": incomplete,
        "diagnostic_bundles_enriched": enriched,
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
    arguments = parser.parse_args()
    report = generate_complete(
        arguments.output_root.resolve(),
        arguments.aggregate.resolve(),
        arguments.coverage.resolve(),
    )
    print(
        "theorem_artifact_coverage=passed "
        f"rows={report['theorem_complexes']} "
        f"enriched={report['diagnostic_bundles_enriched']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
