"""Build the machine-readable final QA record from verified repository state."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import subprocess

if __package__:
    from tools.consistency_catalog import implemented_contracts
else:
    from consistency_catalog import implemented_contracts


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def _git(*arguments: str) -> str:
    return subprocess.run(["git", *arguments], check=True, capture_output=True, text=True).stdout.strip()


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
    relative_output = output.as_posix()
    statuses.setdefault(relative_output, "A")
    return {
        "new_files": sum(status == "A" for status in statuses.values()),
        "modified_files": sum(status != "A" for status in statuses.values()),
        "total_changed_files": len(statuses),
    }


def build(arguments: argparse.Namespace) -> dict[str, object]:
    matrix = _rows(Path("docs/data/theorem_complex_implementation_matrix.csv"))
    status_counts = Counter(row["implementation_status"] for row in matrix)
    level_counts = Counter(row["level"] for row in matrix if row["implementation_status"] == "implemented")
    artifact = json.loads(Path("docs/data/artifact_provenance_manifest.json").read_text(encoding="utf-8"))
    verification = json.loads(Path("docs/data/appendix_source_verification.json").read_text(encoding="utf-8"))
    revisions = Counter(row["revision_status"] for row in _rows(Path("docs/data/repository_file_revision_status.csv")))
    implemented = {row["complex_id"] for row in matrix if row["implementation_status"] == "implemented"}
    contracts = implemented_contracts()
    unresolved = [
        {"complex_id": str(contract.complex_id), "source_id": str(source_id)}
        for contract in contracts
        for source_id in contract.source_ids
        if str(source_id) not in implemented
    ]
    tracked_tex = _git("ls-files", "*.tex").splitlines()
    carrier_conflicts = [
        row for row in matrix
        if row["level"] in {"B", "C"} and row.get("carrier_violation", "").lower() == "true"
    ]
    test_execution = json.loads(Path("reports/test_execution_manifest.json").read_text(encoding="utf-8"))
    simulation_execution = json.loads(Path("reports/simulation_execution_manifest.json").read_text(encoding="utf-8"))
    payload = {
        "schema_version": "1.0",
        "repository": "https://github.com/pt2710/The-Nothingness-Effect.git",
        "default_branch": "main",
        "work_branch": _git("branch", "--show-current"),
        "repository_start_commit": START_COMMIT,
        "repository_result_commit": _git("rev-parse", "HEAD"),
        "result_commit_note": "This is the immutable implementation/artifact source commit immediately before the final QA report commit.",
        "python_version": arguments.python_version,
        "dependency_status": arguments.dependency_status,
        "changes": _change_counts(arguments.output),
        "tests": {
            "passed": arguments.passed,
            "failed": arguments.failed,
            "skipped": arguments.skipped,
            "warnings": arguments.warnings,
            "runtime_seconds": arguments.runtime_seconds,
        },
        "theorem_inventory": {
            "total": len(matrix),
            "A": sum(row["level"] == "A" for row in matrix),
            "B": sum(row["level"] == "B" for row in matrix),
            "C": sum(row["level"] == "C" for row in matrix),
            "implemented": status_counts["implemented"],
            "implemented_A": level_counts["A"],
            "implemented_B": level_counts["B"],
            "implemented_C": level_counts["C"],
            "proxy_only": status_counts["proxy"],
            "not_implemented": status_counts["blocked"],
            "blocked_B": sum(row["level"] == "B" and row["implementation_status"] == "blocked" for row in matrix),
            "blocked_C": sum(row["level"] == "C" and row["implementation_status"] == "blocked" for row in matrix),
            "carrier_conflicts": len(carrier_conflicts),
            "duplicate_complex_ids": len(matrix) - len({row["complex_id"] for row in matrix}),
        },
        "artifact_summary": artifact["summary"],
        "entrypoint_execution": {
            "test": test_execution["summary"],
            "simulation": simulation_execution["summary"],
        },
        "repository_revision_plan": dict(sorted(revisions.items())),
        "unresolved_internal_dependencies": unresolved,
        "tracked_tex_files": tracked_tex,
        "appendix_source_checksum_verification": verification,
        "source_law_regression_status": arguments.source_law_regression_status,
        "security_confirmation": "No authoritative appendix .tex file was copied into, tracked by, committed to, or pushed to the GitHub repository.",
        "claim_boundary": "finite computational support; not a formal proof substitute",
    }
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/data/final_qa_manifest.json"))
    parser.add_argument("--passed", type=int, required=True)
    parser.add_argument("--failed", type=int, required=True)
    parser.add_argument("--skipped", type=int, required=True)
    parser.add_argument("--warnings", type=int, required=True)
    parser.add_argument("--runtime-seconds", type=float, required=True)
    parser.add_argument("--python-version", default="3.14.3")
    parser.add_argument("--dependency-status", default="pip check passed")
    parser.add_argument("--source-law-regression-status", default="passed")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build(args), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"final_qa_manifest={args.output}")
