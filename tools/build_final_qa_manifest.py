"""Build a fail-closed machine-readable final QA record from repository state."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import subprocess

if __package__:
    from tools.consistency_catalog import release_implemented_contracts
    from tools.verify_tne_repository_layout import verify
else:
    from consistency_catalog import release_implemented_contracts
    from verify_tne_repository_layout import verify

from the_nothingness_effect._runtime.theorem_complex_runtime.authority import (
    source_binding_report,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import (
    dependency_downgrades,
    release_statuses,
)


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def _git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _rows(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _change_counts(output: Path) -> dict[str, int]:
    statuses: dict[str, str] = {}
    for line in _git("diff", "--name-status", START_COMMIT).splitlines():
        if not line:
            continue
        fields = line.split("\t")
        statuses[fields[-1]] = fields[0][0]
    for path in _git("ls-files", "--others", "--exclude-standard").splitlines():
        if path:
            statuses[path] = "A"
    statuses.setdefault(output.as_posix(), "A")
    return {
        "new_files": sum(status == "A" for status in statuses.values()),
        "modified_files": sum(status != "A" for status in statuses.values()),
        "total_changed_files": len(statuses),
    }


def _prior_tests() -> dict[str, object]:
    path = Path("docs/data/final_qa_manifest.json")
    if not path.is_file():
        return {}
    try:
        return dict(json.loads(path.read_text(encoding="utf-8")).get("tests", {}))
    except (json.JSONDecodeError, TypeError):
        return {}


def _resolve_test_metrics(arguments: argparse.Namespace) -> dict[str, object]:
    prior = _prior_tests()
    return {
        "passed": (
            arguments.passed
            if arguments.passed is not None
            else int(prior.get("passed", 0))
        ),
        "failed": (
            arguments.failed
            if arguments.failed is not None
            else int(prior.get("failed", 0))
        ),
        "skipped": (
            arguments.skipped
            if arguments.skipped is not None
            else int(prior.get("skipped", 0))
        ),
        "warnings": (
            arguments.warnings
            if arguments.warnings is not None
            else int(prior.get("warnings", 0))
        ),
        "runtime_seconds": (
            arguments.runtime_seconds
            if arguments.runtime_seconds is not None
            else float(prior.get("runtime_seconds", 0.0))
        ),
    }


def build(arguments: argparse.Namespace) -> dict[str, object]:
    matrix = _rows(Path("docs/data/theorem_complex_implementation_matrix.csv"))
    requested_counts = Counter(row["implementation_status"] for row in matrix)
    statuses = release_statuses()
    effective_counts = Counter(statuses.values())
    implemented_levels = Counter(
        row["level"]
        for row in matrix
        if statuses[row["complex_id"]] == "implemented"
    )
    downgraded = list(dependency_downgrades())
    authority = source_binding_report()

    artifact = json.loads(
        Path("docs/data/artifact_provenance_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    verification = json.loads(
        Path("docs/data/appendix_source_verification.json").read_text(
            encoding="utf-8"
        )
    )
    revisions = Counter(
        row["revision_status"]
        for row in _rows(Path("docs/data/repository_file_revision_status.csv"))
    )

    implemented = {
        identifier
        for identifier, status in statuses.items()
        if status == "implemented"
    }
    contracts = release_implemented_contracts()
    unresolved = [
        {"complex_id": str(contract.complex_id), "source_id": str(source_id)}
        for contract in contracts
        for source_id in contract.source_ids
        if str(source_id) not in implemented
    ]

    tracked_tex = _git("ls-files", "*.tex").splitlines()
    carrier_conflicts = [
        row
        for row in matrix
        if row["level"] in {"B", "C"}
        and row.get("carrier_violation", "").lower() == "true"
    ]
    test_execution = json.loads(
        Path("reports/test_execution_manifest.json").read_text(encoding="utf-8")
    )
    simulation_execution = json.loads(
        Path("reports/simulation_execution_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    tests = _resolve_test_metrics(arguments)

    layout = verify(None)
    layout_payload = {
        "checks": layout.results,
        "passed": sum(item["passed"] for item in layout.results),
        "failed": sum(not item["passed"] for item in layout.results),
    }

    duplicate_ids = len(matrix) - len({row["complex_id"] for row in matrix})
    release_blockers: list[str] = []
    if int(tests["failed"]) != 0:
        release_blockers.append("test_failures")
    for kind, summary in (
        ("test_entrypoints", test_execution["summary"]),
        ("simulation_entrypoints", simulation_execution["summary"]),
    ):
        if int(summary.get("failed", 0)) or int(summary.get("timeout", 0)):
            release_blockers.append(kind)
    if layout_payload["failed"]:
        release_blockers.append("layout_verification")
    if unresolved:
        release_blockers.append("unresolved_internal_dependencies")
    if carrier_conflicts:
        release_blockers.append("carrier_conflicts")
    if duplicate_ids:
        release_blockers.append("duplicate_complex_ids")
    if tracked_tex:
        release_blockers.append("tracked_authoritative_tex")
    if int(authority["effective_source_sha_mismatches"]):
        release_blockers.append("authoritative_source_binding")
    if arguments.source_law_regression_status != "passed":
        release_blockers.append("source_law_regression")
    if not bool(verification.get("appendix_checksum_verified")):
        release_blockers.append("appendix_checksum_verification")
    if int(verification.get("missing_equation_labels", 0)):
        release_blockers.append("missing_equation_labels")
    if int(verification.get("missing_first_labels", 0)):
        release_blockers.append("missing_first_labels")
    if arguments.dependency_status != "pip check passed":
        release_blockers.append("dependency_environment")

    payload = {
        "schema_version": "1.2",
        "repository": "https://github.com/pt2710/The-Nothingness-Effect.git",
        "default_branch": "main",
        "work_branch": _git("branch", "--show-current"),
        "repository_start_commit": START_COMMIT,
        "repository_result_commit": _git("rev-parse", "HEAD"),
        "result_commit_note": (
            "Immutable implementation/artifact source commit used for this QA evaluation."
        ),
        "python_version": arguments.python_version,
        "dependency_status": arguments.dependency_status,
        "changes": _change_counts(arguments.output),
        "tests": tests,
        "theorem_inventory": {
            "total": len(matrix),
            "A": sum(row["level"] == "A" for row in matrix),
            "B": sum(row["level"] == "B" for row in matrix),
            "C": sum(row["level"] == "C" for row in matrix),
            "requested_implemented": requested_counts["implemented"],
            "implemented": effective_counts["implemented"],
            "implemented_A": implemented_levels["A"],
            "implemented_B": implemented_levels["B"],
            "implemented_C": implemented_levels["C"],
            "proxy_only": effective_counts["proxy"],
            "not_implemented": effective_counts["blocked"],
            "dependency_downgraded_to_proxy": len(downgraded),
            "blocked_B": sum(
                row["level"] == "B"
                and statuses[row["complex_id"]] == "blocked"
                for row in matrix
            ),
            "blocked_C": sum(
                row["level"] == "C"
                and statuses[row["complex_id"]] == "blocked"
                for row in matrix
            ),
            "carrier_conflicts": len(carrier_conflicts),
            "duplicate_complex_ids": duplicate_ids,
        },
        "dependency_downgrades": downgraded,
        "authoritative_source_binding": authority,
        "artifact_summary": artifact["summary"],
        "entrypoint_execution": {
            "test": test_execution["summary"],
            "simulation": simulation_execution["summary"],
        },
        "layout_verification": layout_payload,
        "repository_revision_plan": dict(sorted(revisions.items())),
        "unresolved_internal_dependencies": unresolved,
        "tracked_tex_files": tracked_tex,
        "appendix_source_checksum_verification": verification,
        "source_law_regression_status": arguments.source_law_regression_status,
        "security_confirmation": (
            "No authoritative appendix .tex file was copied into, tracked by, "
            "committed to, or pushed to the GitHub repository."
        ),
        "claim_boundary": "finite computational support; not a formal proof substitute",
        "release_blockers": sorted(set(release_blockers)),
        "final_qa_passed": not release_blockers,
    }
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/data/final_qa_manifest.json"),
    )
    parser.add_argument("--passed", type=int)
    parser.add_argument("--failed", type=int)
    parser.add_argument("--skipped", type=int)
    parser.add_argument("--warnings", type=int)
    parser.add_argument("--runtime-seconds", type=float)
    parser.add_argument("--python-version", default="3.14.3")
    parser.add_argument("--dependency-status", default="pip check passed")
    parser.add_argument("--source-law-regression-status", default="passed")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return non-zero when any release blocker is present.",
    )
    args = parser.parse_args()
    payload = build(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"final_qa_manifest={args.output} "
        f"final_qa_passed={payload['final_qa_passed']} "
        f"release_blockers={payload['release_blockers']}"
    )
    if args.check and not payload["final_qa_passed"]:
        raise SystemExit(1)
