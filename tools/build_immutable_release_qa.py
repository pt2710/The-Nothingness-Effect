"""Assemble an immutable, branch-head-bound TNE release-QA manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any


_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def _file_record(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.as_posix(),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def build(arguments: argparse.Namespace) -> dict[str, Any]:
    final_qa = _load(arguments.final_qa)
    archive_qa = _load(arguments.archive_qa)
    status = _load(arguments.status_dimensions)
    matrix = _load(arguments.matrix_report)
    provenance = _load(arguments.provenance)

    blockers: list[str] = []
    if not _SHA_RE.fullmatch(arguments.result_commit):
        blockers.append("invalid_result_commit")
    if arguments.ci_conclusion != "success":
        blockers.append("theorem_complex_ci_not_successful")
    if not bool(final_qa.get("final_qa_passed")):
        blockers.append("repository_final_qa_failed")
    blockers.extend(
        f"repository:{item}" for item in final_qa.get("release_blockers", [])
    )
    if not bool(archive_qa.get("passed")):
        blockers.append("authoritative_archive_byte_verification_failed")
    if archive_qa.get("actual_archive_sha256") != archive_qa.get(
        "expected_archive_sha256"
    ):
        blockers.append("authoritative_archive_sha256_mismatch")

    total = int(final_qa.get("theorem_inventory", {}).get("total", 0))
    dimensions = status.get("dimensions", {})
    if int(status.get("rows", 0)) != total:
        blockers.append("release_status_row_count_mismatch")
    if int(dimensions.get("runtime_status", {}).get("implemented", 0)) != total:
        blockers.append("runtime_implementation_incomplete")
    if any(
        count
        for name, count in dimensions.get("source_exactness", {}).items()
        if name != "exact"
    ):
        blockers.append("source_exactness_incomplete")

    matrix_summary = matrix.get("summary", matrix.get("counts", {}))
    provenance_manifests = provenance.get("manifests")
    provenance_count = (
        len(provenance_manifests) if isinstance(provenance_manifests, list) else 0
    )
    if provenance_count != total:
        blockers.append("provenance_cardinality_mismatch")

    inputs = (
        arguments.final_qa,
        arguments.archive_qa,
        arguments.status_dimensions,
        arguments.matrix_report,
        arguments.provenance,
        arguments.archive_manifest,
        arguments.recertification_manifest,
    )
    payload = {
        "schema_version": "1.0",
        "repository": "pt2710/The-Nothingness-Effect",
        "branch": arguments.branch,
        "result_commit": arguments.result_commit,
        "ci_conclusion": arguments.ci_conclusion,
        "ci_run_id": arguments.ci_run_id,
        "authority_archive_sha256": archive_qa.get("actual_archive_sha256"),
        "authority_archive_expected_sha256": archive_qa.get(
            "expected_archive_sha256"
        ),
        "archive_byte_verification": archive_qa,
        "repository_final_qa": final_qa,
        "release_status_dimensions": {
            "rows": status.get("rows"),
            "dimensions": dimensions,
            "open_and_numerical_candidate_preserved": status.get(
                "open_and_numerical_candidate_preserved"
            ),
        },
        "effective_matrix_summary": matrix_summary,
        "provenance_manifest_count": provenance_count,
        "input_records": [_file_record(path) for path in inputs],
        "release_blockers": sorted(set(blockers)),
        "immutable_release_qa_passed": not blockers,
        "claim_boundary": (
            "Runtime implementation, byte-exact source binding, closure status, "
            "and validation status remain independent release dimensions. OPEN "
            "and NUMERICAL_CANDIDATE are preserved and are not promoted by this QA."
        ),
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final-qa", type=Path, required=True)
    parser.add_argument("--archive-qa", type=Path, required=True)
    parser.add_argument("--status-dimensions", type=Path, required=True)
    parser.add_argument("--matrix-report", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument(
        "--archive-manifest",
        type=Path,
        default=Path("docs/data/authoritative_archive_manifest.json"),
    )
    parser.add_argument(
        "--recertification-manifest",
        type=Path,
        default=Path(
            "docs/data/source_recertification/authoritative_recertification_101.json"
        ),
    )
    parser.add_argument("--result-commit", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--ci-conclusion", required=True)
    parser.add_argument("--ci-run-id", default="")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()

    payload = build(arguments)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"immutable_release_qa={arguments.output} "
        f"result_commit={arguments.result_commit} "
        f"passed={payload['immutable_release_qa_passed']} "
        f"blockers={payload['release_blockers']}"
    )
    return 1 if arguments.check and not payload["immutable_release_qa_passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
