"""Export the authority-bound theorem matrix and a source-binding audit report."""

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
    default_implementation_matrix,
    source_binding_report,
)


def export(
    output: Path,
    report_output: Path,
    matrix: Path | None = None,
) -> dict[str, object]:
    source = matrix if matrix is not None else default_implementation_matrix()
    with source.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        raw_rows = list(reader)
        original_fields = tuple(reader.fieldnames or ())
    rows = bind_inventory_rows(raw_rows)
    extra_fields = (
        "recorded_appendix_source_sha256",
        "source_binding_status",
    )
    fieldnames = original_fields + tuple(
        field for field in extra_fields if field not in original_fields
    )

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
    args = parser.parse_args()
    result = export(args.output, args.report, args.matrix)
    print(
        "effective_matrix_exported="
        f"{args.output} rows={result['total_rows']} "
        f"overrides={result['source_binding_overrides']} "
        f"effective_mismatches={result['effective_source_sha_mismatches']}"
    )
    if int(result["effective_source_sha_mismatches"]):
        raise SystemExit(1)
