"""CI guards for inventory, contract dependencies, provenance, and fail-closed laws."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess

from tools.consistency_catalog import implemented_contracts


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
    implemented = {row["complex_id"] for row in matrix if row["implementation_status"] == "implemented"}
    contracts = implemented_contracts()
    contract_ids = [str(contract.complex_id) for contract in contracts]
    if len(contract_ids) != len(set(contract_ids)) or set(contract_ids) != implemented:
        raise SystemExit("registered contract catalog does not exactly match implemented inventory")
    unresolved = sorted(
        (str(contract.complex_id), str(source_id))
        for contract in contracts
        for source_id in contract.source_ids
        if str(source_id) not in implemented
    )
    final_qa = json.loads(
        Path("docs/data/final_qa_manifest.json").read_text(encoding="utf-8")
    )
    documented_unresolved = sorted(
        (item["complex_id"], item["source_id"])
        for item in final_qa.get("unresolved_internal_dependencies", [])
    )
    if unresolved != documented_unresolved:
        raise SystemExit(
            "unresolved implementation dependencies differ from final QA manifest: "
            f"runtime={unresolved[:5]} documented={documented_unresolved[:5]}"
        )
    provenance = json.loads(Path("docs/data/artifact_provenance_manifest.json").read_text(encoding="utf-8"))
    manifested = [item["theorem_complex_id"] for item in provenance["manifests"]]
    if len(manifested) != len(set(manifested)) or set(manifested) != implemented:
        raise SystemExit("aggregate artifact provenance does not cover implemented inventory exactly once")
    if any(item.get("claim_boundary") != "finite computational support; not a formal proof substitute" for item in provenance["manifests"]):
        raise SystemExit("artifact manifest claim boundary missing or altered")
    canonical_paths = sorted({row["implementation_path"] for row in matrix if row["implementation_status"] == "implemented"})
    for relative in canonical_paths:
        path = Path(relative)
        if not path.is_file():
            raise SystemExit(f"implemented canonical path missing: {relative}")
        text = path.read_text(encoding="utf-8")
        if "nan_to_num" in text:
            raise SystemExit(f"NaN/Inf masking is forbidden in canonical source laws: {relative}")
        position = text.find("np.where(np.isfinite")
        if position >= 0 and "compatibility_mode" not in text[max(0, position - 1600):position]:
            raise SystemExit(f"non-finite neutralization found outside explicit compatibility mode: {relative}")
    tracked = subprocess.run(["git", "ls-files", "*.tex"], check=True, capture_output=True, text=True).stdout.splitlines()
    if tracked:
        raise SystemExit(f"tracked LaTeX files are forbidden: {tracked}")
    print(
        f"qa_guards=passed total=351 implemented={len(implemented)} duplicate_ids=0 "
        f"unresolved_dependencies={len(unresolved)} "
        f"provenance_manifests={len(manifested)} tracked_tex=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
