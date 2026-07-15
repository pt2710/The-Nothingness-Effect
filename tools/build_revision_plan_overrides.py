"""Record a conservative row-by-row review of the audit file revision plan."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def _rows(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _alternatives(repository: Path, planned: Path) -> list[Path]:
    candidates: list[Path] = []
    parent = planned.parent
    if planned.name in {"a_level.py", "b_level.py", "c_level.py", "residuals.py"}:
        candidates.append(parent / "contracts.py")
    if planned.name == "run_suite.py":
        candidates.append(parent / "run_contract_suite.py")
    if "visualization" in planned.parts:
        candidates.append(parent.parent / "simulation" / "run_contract_suite.py")
    if len(planned.parts) >= 3 and planned.parts[0:2] == ("equations", "artificial_intelligence"):
        module = planned.parts[2]
        candidates.extend(
            (
                Path("tests/contracts") / f"test_{module}_contracts.py",
                Path("tests/artifacts") / f"test_{module}_artifacts.py",
                Path("tests/numerical") / f"test_{module}_model.py",
            )
        )
    documentation = {
        Path("docs/theorem_complex_traceability.md"): Path("docs/tne_theorem_complex_implementation_status.md"),
        Path("docs/revised_appendix_consistency.md"): Path("docs/tne_appendix_repository_consistency_report.md"),
    }
    if planned in documentation:
        candidates.append(documentation[planned])
    return [candidate for candidate in candidates if (repository / candidate).is_file()]


def build(repository: Path, plan: Path) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in _rows(plan):
        planned = Path(row["path"])
        if (repository / planned).exists():
            status = "reviewed_present"
            evidence = f"Exact planned path exists: {planned.as_posix()}"
        else:
            alternatives = _alternatives(repository, planned)
            if alternatives:
                status = "reviewed_partial_alternative"
                evidence = "Implemented subset or equivalent responsibility at: " + ";".join(item.as_posix() for item in alternatives)
            else:
                status = "reviewed_open"
                evidence = "No exact path or certified substitute; theorem rows remain proxy_only/not_implemented where applicable."
        result[row["path"]] = {
            "revision_status": status,
            "verification_evidence": evidence,
        }
    if len(result) != len(_rows(plan)):
        raise ValueError("revision-plan paths are not unique")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path("."))
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("docs/data/repository_revision_status_overrides.json"))
    arguments = parser.parse_args()
    payload = build(arguments.repository.resolve(), arguments.plan.resolve())
    arguments.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"reviewed_revision_plan_rows={len(payload)} output={arguments.output}")
