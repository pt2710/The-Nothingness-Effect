"""CI guards for inventory, dependency closure, provenance, and fail-closed laws."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.consistency_catalog import release_implemented_contracts
from tools.verify_tne_repository_layout import verify
from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import (
    dependency_downgrades,
    release_statuses,
)


def _rows(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    matrix = _rows(Path("docs/data/theorem_complex_implementation_matrix.csv"))
    identifiers = [row["complex_id"] for row in matrix]
    if len(matrix) != 351 or len(set(identifiers)) != 351:
        raise SystemExit("inventory must contain 351 unique theorem-complex IDs")

    levels = {level: sum(row["level"] == level for row in matrix) for level in ("A", "B", "C")}
    if levels != {"A": 204, "B": 98, "C": 49}:
        raise SystemExit(f"invalid theorem inventory level counts: {levels}")

    requested_implemented = {
        row["complex_id"] for row in matrix if row["implementation_status"] == "implemented"
    }
    statuses = release_statuses()
    implemented = {
        identifier for identifier, status in statuses.items() if status == "implemented"
    }
    downgraded = dependency_downgrades()

    contracts = release_implemented_contracts()
    contract_ids = [str(contract.complex_id) for contract in contracts]
    if len(contract_ids) != len(set(contract_ids)) or set(contract_ids) != implemented:
        raise SystemExit("active contract catalog does not exactly match dependency-closed inventory")

    unresolved = sorted(
        (str(contract.complex_id), str(source_id))
        for contract in contracts
        for source_id in contract.source_ids
        if str(source_id) not in implemented
    )
    if unresolved:
        raise SystemExit(
            "dependency-closed implementation set still contains unresolved sources: "
            f"{unresolved[:5]}"
        )

    provenance = json.loads(
        Path("docs/data/artifact_provenance_manifest.json").read_text(encoding="utf-8")
    )
    manifested = [item["theorem_complex_id"] for item in provenance["manifests"]]
    if len(manifested) != len(set(manifested)):
        raise SystemExit("aggregate artifact provenance contains duplicate theorem-complex IDs")
    manifested_set = set(manifested)
    if not implemented.issubset(manifested_set):
        missing = sorted(implemented - manifested_set)
        raise SystemExit(f"active implementations lack artifact provenance: {missing[:5]}")
    if not manifested_set.issubset(requested_implemented):
        unknown = sorted(manifested_set - requested_implemented)
        raise SystemExit(f"artifact provenance contains non-requested implementation IDs: {unknown[:5]}")
    if any(
        item.get("claim_boundary")
        != "finite computational support; not a formal proof substitute"
        for item in provenance["manifests"]
    ):
        raise SystemExit("artifact manifest claim boundary missing or altered")

    canonical_paths = sorted(
        {
            row["implementation_path"]
            for row in matrix
            if statuses[row["complex_id"]] == "implemented"
        }
    )
    for relative in canonical_paths:
        path = Path(relative)
        if not path.is_file():
            raise SystemExit(f"implemented canonical path missing: {relative}")
        text = path.read_text(encoding="utf-8")
        if "nan_to_num" in text:
            raise SystemExit(f"NaN/Inf masking is forbidden in canonical source laws: {relative}")
        position = text.find("np.where(np.isfinite")
        if position >= 0 and "compatibility_mode" not in text[max(0, position - 1600):position]:
            raise SystemExit(
                f"non-finite neutralization found outside explicit compatibility mode: {relative}"
            )

    tracked = subprocess.run(
        ["git", "ls-files", "*.tex"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    if tracked:
        raise SystemExit(f"tracked LaTeX files are forbidden: {tracked}")

    layout = verify(None)
    layout_failures = [result for result in layout.results if not result["passed"]]
    if layout_failures:
        first = layout_failures[0]
        raise SystemExit(
            f"repository layout QA failed: {first['name']}: {first['failures'][:3]}"
        )

    print(
        f"qa_guards=passed total=351 requested_implemented={len(requested_implemented)} "
        f"release_implemented={len(implemented)} dependency_downgrades={len(downgraded)} "
        f"unresolved_dependencies=0 provenance_manifests={len(manifested)} "
        f"layout_checks={len(layout.results)} tracked_tex=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
