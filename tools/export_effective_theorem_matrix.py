"""Export authority-bound theorem inventory and artifact provenance state."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from the_nothingness_effect._runtime.theorem_complex_runtime.authority import (
    bind_inventory_rows,
    bind_provenance_manifest,
    default_artifact_provenance,
    default_implementation_matrix,
    provenance_binding_report,
    recertified_source_bindings,
    source_binding_report,
)


def _effective_rows(
    matrix: Path | None = None,
) -> tuple[list[dict[str, str]], tuple[str, ...]]:
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


def export_provenance(
    output: Path,
    report_output: Path,
    provenance: Path | None = None,
) -> dict[str, object]:
    source = provenance if provenance is not None else default_artifact_provenance()
    raw = json.loads(source.read_text(encoding="utf-8"))
    effective = bind_provenance_manifest(raw)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(effective, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report = provenance_binding_report(source)
    report["effective_provenance_output"] = output.as_posix()
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _unresolved_provenance_mismatches(
    report: dict[str, object],
) -> list[dict[str, str]]:
    """Return mismatches not covered by the explicit 101-row recertification ledger."""

    recertified = recertified_source_bindings()
    raw = report.get("raw_mismatches", [])
    if not isinstance(raw, list):
        raise RuntimeError("provenance binding report has invalid raw_mismatches")
    unresolved: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            raise RuntimeError("provenance mismatch record must be an object")
        identifier = str(item.get("theorem_complex_id", ""))
        appendix = str(item.get("appendix_filename", ""))
        authoritative = str(item.get("authoritative_sha256", ""))
        record = recertified.get(identifier)
        if (
            record is not None
            and record["appendix_file"] == appendix
            and record["authoritative_appendix_sha256"] == authoritative
            and record["recertification_status"] == "byte_verified_label_reaudited"
        ):
            continue
        unresolved.append(
            {
                "theorem_complex_id": identifier,
                "appendix_filename": appendix,
                "authoritative_sha256": authoritative,
            }
        )
    return unresolved


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
    )
    unresolved_provenance = _unresolved_provenance_mismatches(provenance_result)
    provenance_result["explicitly_recertified_mismatches"] = int(
        provenance_result.get("effective_source_sha_mismatches", 0)
    ) - len(unresolved_provenance)
    provenance_result["unresolved_source_sha_mismatches"] = len(
        unresolved_provenance
    )
    Path(args.provenance_report).write_text(
        json.dumps(provenance_result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "effective_authority_state_exported="
        f"matrix={args.output} rows={matrix_result['total_rows']} "
        f"matrix_source_overrides={matrix_result['source_binding_overrides']} "
        f"matrix_status_overrides={matrix_result['implementation_status_overrides']} "
        f"provenance={args.provenance_output} "
        f"provenance_overrides={provenance_result['source_binding_overrides']} "
        f"provenance_explicit_recertifications="
        f"{provenance_result['explicitly_recertified_mismatches']} "
        f"provenance_unresolved="
        f"{provenance_result['unresolved_source_sha_mismatches']}"
    )
    if int(matrix_result["effective_source_sha_mismatches"]) or unresolved_provenance:
        raise SystemExit(1)
