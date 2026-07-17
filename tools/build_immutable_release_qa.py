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
    artifact_coverage = _load(arguments.artifact_coverage)
    closure_obligations = _load(arguments.closure_obligations)
    robustness = _load(arguments.multimodal_robustness)

    blockers: list[str] = []
    if not _SHA_RE.fullmatch(arguments.result_commit):
        blockers.append("invalid_result_commit")
    if arguments.ci_conclusion != "success":
        blockers.append("theorem_complex_ci_not_successful")

    final_qa_commit = str(final_qa.get("repository_result_commit", ""))
    provenance_commit = str(provenance.get("repository_result_commit", ""))
    if final_qa_commit != arguments.result_commit:
        blockers.append("repository_final_qa_commit_mismatch")
    if provenance_commit != arguments.result_commit:
        blockers.append("artifact_provenance_commit_mismatch")

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

    artifact_total = int(artifact_coverage.get("theorem_complexes", 0))
    complete_artifacts = int(
        artifact_coverage.get("complete_core_artifact_bundles", 0)
    )
    if not bool(artifact_coverage.get("passed")):
        blockers.append("theorem_artifact_coverage_failed")
    if artifact_total != total or complete_artifacts != total:
        blockers.append("theorem_artifact_coverage_incomplete")
    if int(status.get("artifact_core_bundle_gaps", 0)) != 0:
        blockers.append("release_status_reports_artifact_gaps")

    open_count = int(status.get("open_and_numerical_candidate_preserved", 0))
    ledger_count = int(
        closure_obligations.get("open_or_numerical_candidate_count", -1)
    )
    if not bool(closure_obligations.get("all_open_states_represented")):
        blockers.append("closure_obligation_ledger_incomplete")
    if ledger_count != open_count:
        blockers.append("closure_obligation_count_mismatch")

    robustness_seeds = robustness.get("seeds", [])
    robustness_scenarios = set(str(item) for item in robustness.get("scenarios", []))
    required_scenarios = {"clean", "remove_color", "remove_sound", "remove_vision"}
    if not isinstance(robustness_seeds, list) or len(set(robustness_seeds)) < 3:
        blockers.append("multimodal_multiseed_coverage_incomplete")
    if not required_scenarios <= robustness_scenarios:
        blockers.append("multimodal_modality_removal_coverage_incomplete")
    if not bool(robustness.get("all_metrics_finite")):
        blockers.append("multimodal_robustness_nonfinite")
    if "synthetic" not in str(robustness.get("claim_boundary", "")):
        blockers.append("multimodal_robustness_claim_boundary_missing")

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
        arguments.artifact_coverage,
        arguments.closure_obligations,
        arguments.multimodal_robustness,
        arguments.archive_manifest,
        arguments.recertification_manifest,
    )
    payload = {
        "schema_version": "1.3",
        "repository": "pt2710/The-Nothingness-Effect",
        "branch": arguments.branch,
        "result_commit": arguments.result_commit,
        "repository_final_qa_commit": final_qa_commit,
        "artifact_provenance_commit": provenance_commit,
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
            "open_and_numerical_candidate_preserved": open_count,
            "artifact_core_bundle_gaps": status.get("artifact_core_bundle_gaps"),
        },
        "theorem_artifact_coverage": {
            "theorem_complexes": artifact_total,
            "complete_core_artifact_bundles": complete_artifacts,
            "diagnostic_bundles_enriched": artifact_coverage.get(
                "diagnostic_bundles_enriched"
            ),
            "passed": artifact_coverage.get("passed"),
        },
        "closure_obligation_ledger": {
            "open_or_numerical_candidate_count": ledger_count,
            "counts": closure_obligations.get("counts", {}),
            "all_open_states_represented": closure_obligations.get(
                "all_open_states_represented"
            ),
        },
        "multimodal_robustness": {
            "seeds": robustness_seeds,
            "epochs": robustness.get("epochs"),
            "scenarios": sorted(robustness_scenarios),
            "records": robustness.get("records"),
            "all_metrics_finite": robustness.get("all_metrics_finite"),
            "claim_boundary": robustness.get("claim_boundary"),
        },
        "effective_matrix_summary": matrix_summary,
        "provenance_manifest_count": provenance_count,
        "input_records": [_file_record(path) for path in inputs],
        "release_blockers": sorted(set(blockers)),
        "immutable_release_qa_passed": not blockers,
        "claim_boundary": (
            "Runtime implementation, byte-exact source binding, closure status, "
            "artifact completeness and validation status remain independent release "
            "dimensions. OPEN and NUMERICAL_CANDIDATE are preserved and are not "
            "promoted by this QA. Synthetic robustness is not empirical validation."
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
    parser.add_argument("--artifact-coverage", type=Path, required=True)
    parser.add_argument("--closure-obligations", type=Path, required=True)
    parser.add_argument("--multimodal-robustness", type=Path, required=True)
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
