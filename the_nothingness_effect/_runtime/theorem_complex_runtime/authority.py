"""Fail-closed binding to externally maintained authoritative appendix sources.

The authoritative LaTeX files are intentionally not tracked in this repository.
Their externally computed SHA-256 digests are recorded in
``docs/data/authoritative_appendix_sources.json``.  Runtime contracts and
inventory consumers are bound to that manifest so a stale source digest cannot
silently survive in an otherwise green release.
"""

from __future__ import annotations

import csv
from dataclasses import replace
import json
from pathlib import Path
import re
from typing import Iterable, Mapping

from .types import ComplexContract


_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_authority_manifest() -> Path:
    return repository_root() / "docs" / "data" / "authoritative_appendix_sources.json"


def default_implementation_matrix() -> Path:
    return repository_root() / "docs" / "data" / "theorem_complex_implementation_matrix.csv"


def load_authority_manifest(path: str | Path | None = None) -> dict[str, object]:
    manifest_path = Path(path) if path is not None else default_authority_manifest()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.1":
        raise RuntimeError("authoritative appendix manifest must use schema version 1.1")
    appendices = payload.get("appendices")
    if not isinstance(appendices, dict) or not appendices:
        raise RuntimeError("authoritative appendix manifest must contain appendix bindings")
    for appendix, record in appendices.items():
        if not isinstance(appendix, str) or not isinstance(record, dict):
            raise RuntimeError("invalid authoritative appendix binding record")
        digest = record.get("sha256")
        if not isinstance(digest, str) or not _SHA256_PATTERN.fullmatch(digest):
            raise RuntimeError(f"invalid SHA-256 binding for {appendix}")
        if not str(record.get("status", "")).startswith(("verified", "recertified")):
            raise RuntimeError(f"appendix binding is not recertified: {appendix}")
    return payload


def authoritative_bindings(path: str | Path | None = None) -> dict[str, str]:
    payload = load_authority_manifest(path)
    appendices = payload["appendices"]
    assert isinstance(appendices, dict)
    return {
        str(appendix): str(record["sha256"])
        for appendix, record in appendices.items()
        if isinstance(record, dict)
    }


def bind_contract(
    contract: ComplexContract,
    bindings: Mapping[str, str] | None = None,
) -> ComplexContract:
    active = authoritative_bindings() if bindings is None else dict(bindings)
    expected = active.get(contract.appendix)
    if expected is None or contract.appendix_source_sha256 == expected:
        return contract
    return replace(contract, appendix_source_sha256=expected)


def bind_contracts(
    contracts: Iterable[ComplexContract],
    bindings: Mapping[str, str] | None = None,
) -> tuple[ComplexContract, ...]:
    active = authoritative_bindings() if bindings is None else dict(bindings)
    return tuple(bind_contract(contract, active) for contract in contracts)


def bind_inventory_rows(
    rows: Iterable[Mapping[str, str]],
    bindings: Mapping[str, str] | None = None,
) -> list[dict[str, str]]:
    active = authoritative_bindings() if bindings is None else dict(bindings)
    result: list[dict[str, str]] = []
    for source in rows:
        row = dict(source)
        recorded = row.get("appendix_source_sha256", "")
        expected = active.get(row.get("appendix_file", ""))
        row["recorded_appendix_source_sha256"] = recorded
        if expected is None:
            row["source_binding_status"] = "unmanaged"
        elif recorded == expected:
            row["source_binding_status"] = "verified"
        else:
            row["source_binding_status"] = "manifest_override"
            row["appendix_source_sha256"] = expected
        result.append(row)
    return result


def source_binding_report(
    matrix_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
) -> dict[str, object]:
    path = Path(matrix_path) if matrix_path is not None else default_implementation_matrix()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        raw_rows = list(csv.DictReader(handle))
    bindings = authoritative_bindings(manifest_path)
    effective_rows = bind_inventory_rows(raw_rows, bindings)

    raw_mismatches: list[dict[str, str]] = []
    effective_mismatches: list[dict[str, str]] = []
    appendix_counts: dict[str, dict[str, int | str]] = {}
    for raw, effective in zip(raw_rows, effective_rows, strict=True):
        appendix = raw["appendix_file"]
        expected = bindings.get(appendix)
        if expected is None:
            continue
        summary = appendix_counts.setdefault(
            appendix,
            {
                "rows": 0,
                "raw_matches": 0,
                "overrides": 0,
                "effective_matches": 0,
                "authoritative_sha256": expected,
            },
        )
        summary["rows"] = int(summary["rows"]) + 1
        if raw.get("appendix_source_sha256") == expected:
            summary["raw_matches"] = int(summary["raw_matches"]) + 1
        else:
            summary["overrides"] = int(summary["overrides"]) + 1
            raw_mismatches.append(
                {
                    "complex_id": raw["complex_id"],
                    "appendix_file": appendix,
                    "recorded_sha256": raw.get("appendix_source_sha256", ""),
                    "authoritative_sha256": expected,
                }
            )
        if effective.get("appendix_source_sha256") == expected:
            summary["effective_matches"] = int(summary["effective_matches"]) + 1
        else:
            effective_mismatches.append(
                {
                    "complex_id": effective["complex_id"],
                    "appendix_file": appendix,
                    "effective_sha256": effective.get("appendix_source_sha256", ""),
                    "authoritative_sha256": expected,
                }
            )

    return {
        "schema_version": "1.0",
        "matrix_path": path.as_posix(),
        "total_rows": len(raw_rows),
        "managed_appendices": len(bindings),
        "managed_rows": sum(int(item["rows"]) for item in appendix_counts.values()),
        "raw_source_sha_mismatches": len(raw_mismatches),
        "effective_source_sha_mismatches": len(effective_mismatches),
        "source_binding_overrides": len(raw_mismatches),
        "raw_mismatches": raw_mismatches,
        "effective_mismatches": effective_mismatches,
        "appendices": dict(sorted(appendix_counts.items())),
    }
