"""Fail-closed verification of authoritative appendix source bindings."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import all_contracts

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/data/theorem_complex_implementation_matrix.csv"
BINDINGS = ROOT / "docs/data/authoritative_appendix_source_bindings.json"
STALE_DIGESTS = {
    "3f428e24ed9518655f94145dcd8667f979aa03c74f75695d8273da273e2538d0",
    "2679b61a1d98100ed3a13669c16c299cd9b09807bc3847d383d559c9251189ea",
    "d711e5c4260fb61bff1ef3e7ea3be14ef093370a9ff22607d2a54e74ba8b166b",
}
EXPECTED_COMPLETENESS_SOURCES = {
    "typed_admissibility_instrument": (
        "2_adic_criterion_of_theoremhood_and_typed_dual_infinity",
        "non_manifestability_of_the_anti_circle_and_observation_collapse",
    ),
    "sheaf_of_closure_certificates": (
        "typed_admissibility_instrument",
        "idempotent_splitting_and_oscillation_obstruction",
        "protected_commuting_closure_transport",
    ),
    "terminal_quotient_of_closure_certificates": (
        "typed_admissibility_instrument",
        "idempotent_splitting_and_oscillation_obstruction",
        "protected_commuting_closure_transport",
        "noether_constant_to_local_transgression",
    ),
}


def main() -> int:
    with MATRIX.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    bindings = json.loads(BINDINGS.read_text(encoding="utf-8"))["appendices"]
    expected = {name: record["sha256"] for name, record in bindings.items()}

    matrix_by_id = {row["complex_id"]: row for row in rows}
    failures: list[str] = []
    for row in rows:
        appendix = row["appendix_file"]
        if appendix not in expected:
            failures.append(f"unbound appendix: {appendix}")
        elif row["appendix_source_sha256"] != expected[appendix]:
            failures.append(
                f"matrix digest mismatch: {row['complex_id']} "
                f"{row['appendix_source_sha256']} != {expected[appendix]}"
            )

    for contract in all_contracts():
        identifier = str(contract.complex_id)
        row = matrix_by_id.get(identifier)
        if row is None:
            failures.append(f"contract absent from matrix: {identifier}")
            continue
        if contract.appendix_source_sha256 != row["appendix_source_sha256"]:
            failures.append(
                f"contract digest mismatch: {identifier} "
                f"{contract.appendix_source_sha256} != {row['appendix_source_sha256']}"
            )

    for identifier, source_ids in EXPECTED_COMPLETENESS_SOURCES.items():
        actual = tuple(
            item for item in matrix_by_id[identifier]["source_complex_ids"].split(";") if item
        )
        if actual != source_ids:
            failures.append(
                f"completeness source graph mismatch: {identifier}: {actual} != {source_ids}"
            )

    for path in sorted((ROOT / "the_nothingness_effect").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for digest in STALE_DIGESTS:
            if digest in text:
                failures.append(
                    f"stale digest remains in {path.relative_to(ROOT)}: {digest}"
                )

    if failures:
        raise SystemExit(
            "authoritative source binding verification failed:\n- "
            + "\n- ".join(failures[:30])
        )
    print(
        "authoritative_source_bindings=passed "
        f"appendices={len(expected)} contracts={len(all_contracts())} rows={len(rows)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
