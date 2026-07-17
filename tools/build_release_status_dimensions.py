"""Build independent runtime/source/closure/validation/artifact status dimensions."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path

from the_nothingness_effect._runtime.theorem_complex_runtime.authority import bind_inventory_rows
from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import release_statuses


def build(
    matrix_path: Path,
    provenance_path: Path,
    csv_output: Path,
    json_output: Path,
    artifact_coverage_path: Path | None = None,
) -> dict[str, object]:
    with matrix_path.open(newline="", encoding="utf-8-sig") as handle:
        raw_rows = list(csv.DictReader(handle))
    rows = bind_inventory_rows(raw_rows)
    statuses = release_statuses(matrix_path)
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    manifests = provenance.get("manifests")
    if not isinstance(manifests, list):
        raise RuntimeError("provenance manifest list is missing")
    by_id = {
        str(item["theorem_complex_id"]): item
        for item in manifests
        if isinstance(item, dict)
    }

    artifact_records: dict[str, dict[str, object]] = {}
    if artifact_coverage_path is not None:
        coverage = json.loads(artifact_coverage_path.read_text(encoding="utf-8"))
        records = coverage.get("records")
        if not isinstance(records, list):
            raise RuntimeError("artifact coverage record list is missing")
        artifact_records = {
            str(item["theorem_complex_id"]): item
            for item in records
            if isinstance(item, dict)
        }

    records: list[dict[str, str]] = []
    for row in rows:
        identifier = row["complex_id"]
        manifest = by_id.get(identifier)
        closure = (
            str(manifest.get("closure_status", "untested"))
            if manifest is not None
            else "untested"
        )
        approximation = (
            manifest.get("approximation_metadata", {})
            if manifest is not None
            else {}
        )
        if isinstance(approximation, dict) and approximation.get("empirical_dataset"):
            validation = "empirical"
        elif manifest is not None:
            validation = "synthetic"
        else:
            validation = "untested"
        artifact_record = artifact_records.get(identifier)
        if artifact_record is None:
            artifact_status = "untested"
        elif bool(artifact_record.get("complete_core_bundle")):
            artifact_status = "complete_core_bundle"
        else:
            artifact_status = "incomplete"
        records.append(
            {
                "complex_id": identifier,
                "appendix_file": row["appendix_file"],
                "level": row["level"],
                "runtime_status": (
                    "implemented" if statuses[identifier] == "implemented" else "missing"
                ),
                "source_exactness": row["source_exactness"],
                "closure_status": closure,
                "validation_status": validation,
                "artifact_status": artifact_status,
                "implementation_path": (
                    row.get("implementation_status_evidence_path")
                    or row.get("implementation_path", "")
                ),
            }
        )

    csv_output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(records[0])
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)

    dimensions = {
        name: dict(Counter(record[name] for record in records))
        for name in (
            "runtime_status",
            "source_exactness",
            "closure_status",
            "validation_status",
            "artifact_status",
        )
    }
    report = {
        "schema_version": "1.1",
        "rows": len(records),
        "dimensions": dimensions,
        "open_and_numerical_candidate_preserved": (
            dimensions["closure_status"].get("open", 0)
            + dimensions["closure_status"].get("numerical_candidate", 0)
        ),
        "artifact_core_bundle_gaps": dimensions["artifact_status"].get("incomplete", 0),
        "records": records,
    }
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("reports/effective_theorem_complex_implementation_matrix.csv"),
    )
    parser.add_argument(
        "--provenance",
        type=Path,
        default=Path("reports/effective_artifact_provenance_manifest.json"),
    )
    parser.add_argument("--artifact-coverage", type=Path)
    parser.add_argument(
        "--csv-output",
        type=Path,
        default=Path("reports/release_status_dimensions.csv"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("reports/release_status_dimensions.json"),
    )
    args = parser.parse_args()
    report = build(
        args.matrix,
        args.provenance,
        args.csv_output,
        args.json_output,
        args.artifact_coverage,
    )
    print(
        f"release_status_dimensions=passed rows={report['rows']} "
        f"open_or_candidate={report['open_and_numerical_candidate_preserved']} "
        f"artifact_gaps={report['artifact_core_bundle_gaps']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
