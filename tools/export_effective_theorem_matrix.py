"""Export authority-bound theorem inventory and artifact provenance state."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from the_nothingness_effect._runtime.theorem_complex_runtime.authority import (
    bind_inventory_rows,
    bind_provenance_manifest,
    default_implementation_matrix,
    implementation_status_overrides,
    provenance_binding_report,
    source_binding_report,
)


RAW_PROVENANCE = REPOSITORY_ROOT / "docs" / "data" / "artifact_provenance_manifest.json"
CLAIM_BOUNDARY = "finite computational support; not a formal proof substitute"
START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def _effective_rows(matrix: Path | None = None) -> tuple[list[dict[str, str]], tuple[str, ...]]:
    source = matrix if matrix is not None else default_implementation_matrix()
    with source.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        raw_rows = list(reader)
        original_fields = tuple(reader.fieldnames or ())
    return bind_inventory_rows(raw_rows), original_fields


def export(
    output: Path,
    report_output: Path,
    matrix: Path | None = None,
) -> dict[str, object]:
    source = matrix if matrix is not None else default_implementation_matrix()
    rows, original_fields = _effective_rows(source)
    generated_fields = sorted(
        {field for row in rows for field in row} - set(original_fields)
    )
    fieldnames = original_fields + tuple(generated_fields)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    report = source_binding_report(source)
    report["effective_matrix_output"] = output.as_posix()
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _activation_provenance(
    identifier: str,
    override: dict[str, str],
    row: dict[str, str],
) -> dict[str, object]:
    encoded = json.dumps(
        {"complex_id": identifier, **override},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return {
        "appendix_filename": row["appendix_file"],
        "appendix_source_sha256": row["appendix_source_sha256"],
        "approximation_metadata": {
            "authority_status_override": True,
            "exact_semantics": False,
            "formal_proof_substitute": False,
        },
        "claim_boundary": CLAIM_BOUNDARY,
        "closure_status": "numerical_candidate",
        "generated_files": [],
        "evidence_files": [override["evidence_path"]],
        "numeric_tolerances": {"absolute": 1e-6},
        "parameter_hash": hashlib.sha256(encoded).hexdigest(),
        "parameters": {
            "fixture": "recertified-a-source-contract-v1",
            "status_override_reason": override["reason"],
        },
        "regeneration_command": "python -m pytest -q tests/contracts",
        "repository_result_commit": os.environ.get("GITHUB_SHA", "generated-at-runtime"),
        "repository_start_commit": START_COMMIT,
        "residual_vector": [],
        "seed": 0,
        "theorem_complex_id": identifier,
    }


def export_provenance(
    output: Path,
    report_output: Path,
    provenance: Path | None = None,
    matrix: Path | None = None,
) -> dict[str, object]:
    source = provenance if provenance is not None else RAW_PROVENANCE
    raw = json.loads(source.read_text(encoding="utf-8"))
    effective = bind_provenance_manifest(raw)
    manifests = effective.get("manifests")
    if not isinstance(manifests, list):
        raise RuntimeError("artifact provenance manifest must contain a manifest list")

    rows, _ = _effective_rows(matrix)
    by_id = {row["complex_id"]: row for row in rows}
    existing = {
        str(item.get("theorem_complex_id", ""))
        for item in manifests
        if isinstance(item, dict)
    }
    activations = implementation_status_overrides()
    added = 0
    for identifier, override in sorted(activations.items()):
        if identifier in existing:
            continue
        row = by_id.get(identifier)
        if row is None:
            raise RuntimeError(f"status override absent from theorem matrix: {identifier}")
        manifests.append(_activation_provenance(identifier, override, row))
        added += 1
    manifests.sort(key=lambda item: str(item.get("theorem_complex_id", "")))

    summary = effective.get("summary")
    if isinstance(summary, dict):
        summary["theorem_manifests"] = len(manifests)
        summary["authority_activation_manifests"] = added
    effective["authority_activation_provenance"] = {
        "added": added,
        "total_status_overrides": len(activations),
        "claim_boundary": CLAIM_BOUNDARY,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(effective, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report = provenance_binding_report(source)
    report["effective_provenance_output"] = output.as_posix()
    report["activation_manifests_added"] = added
    report["effective_total_manifests"] = len(manifests)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/effective_theorem_complex_implementation_matrix.csv"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("reports/effective_theorem_complex_implementation_matrix.json"),
    )
    parser.add_argument("--matrix", type=Path)
    parser.add_argument(
        "--provenance-output",
        type=Path,
        default=Path("reports/effective_artifact_provenance_manifest.json"),
    )
    parser.add_argument(
        "--provenance-report",
        type=Path,
        default=Path("reports/effective_artifact_provenance_binding.json"),
    )
    parser.add_argument("--provenance", type=Path)
    args = parser.parse_args()
    matrix_result = export(args.output, args.report, args.matrix)
    provenance_result = export_provenance(
        args.provenance_output,
        args.provenance_report,
        args.provenance,
        args.matrix,
    )
    print(
        "effective_authority_state_exported="
        f"matrix={args.output} rows={matrix_result['total_rows']} "
        f"status_overrides={matrix_result['implementation_status_overrides']} "
        f"matrix_source_overrides={matrix_result['source_binding_overrides']} "
        f"provenance={args.provenance_output} "
        f"provenance_added={provenance_result['activation_manifests_added']}"
    )
    if int(matrix_result["effective_source_sha_mismatches"]) or int(
        provenance_result["effective_source_sha_mismatches"]
    ):
        raise SystemExit(1)
