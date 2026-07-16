"""Fail-closed binding to externally maintained authoritative appendix sources.

The authoritative LaTeX files are intentionally not tracked in this repository.
Their externally computed SHA-256 digests and explicitly reviewed implementation
promotions are recorded in ``docs/data/authoritative_appendix_sources.json``.
Runtime contracts, inventory rows, and artifact provenance are bound to that
manifest so stale source digests or unaudited status changes cannot silently
survive in an otherwise green release.
"""

from __future__ import annotations

from copy import deepcopy
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
    return (
        repository_root()
        / "docs"
        / "data"
        / "authoritative_appendix_sources.json"
    )


def default_implementation_matrix() -> Path:
    return (
        repository_root()
        / "docs"
        / "data"
        / "theorem_complex_implementation_matrix.csv"
    )


def default_artifact_provenance() -> Path:
    effective = (
        repository_root()
        / "reports"
        / "effective_artifact_provenance_manifest.json"
    )
    if effective.is_file():
        return effective
    return (
        repository_root()
        / "docs"
        / "data"
        / "artifact_provenance_manifest.json"
    )


def load_authority_manifest(
    path: str | Path | None = None,
) -> dict[str, object]:
    manifest_path = (
        Path(path) if path is not None else default_authority_manifest()
    )
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.1":
        raise RuntimeError(
            "authoritative appendix manifest must use schema version 1.1"
        )
    appendices = payload.get("appendices")
    if not isinstance(appendices, dict) or not appendices:
        raise RuntimeError(
            "authoritative appendix manifest must contain appendix bindings"
        )
    for appendix, record in appendices.items():
        if not isinstance(appendix, str) or not isinstance(record, dict):
            raise RuntimeError("invalid authoritative appendix binding record")
        digest = record.get("sha256")
        if not isinstance(digest, str) or not _SHA256_PATTERN.fullmatch(digest):
            raise RuntimeError(f"invalid SHA-256 binding for {appendix}")
        if not str(record.get("status", "")).startswith(
            ("verified", "recertified")
        ):
            raise RuntimeError(
                f"appendix binding is not recertified: {appendix}"
            )

    overrides = payload.get("implementation_status_overrides", {})
    if not isinstance(overrides, dict):
        raise RuntimeError(
            "implementation_status_overrides must be an object"
        )
    for identifier, record in overrides.items():
        if not isinstance(identifier, str) or not identifier:
            raise RuntimeError("implementation override ID must be nonempty")
        if not isinstance(record, dict):
            raise RuntimeError(
                f"invalid implementation override for {identifier}"
            )
        if record.get("status") != "implemented":
            raise RuntimeError(
                "authority manifest may only promote reviewed contracts to implemented"
            )
        reason = record.get("reason")
        evidence_path = record.get("evidence_path")
        if not isinstance(reason, str) or not reason.strip():
            raise RuntimeError(
                f"implementation override lacks reason: {identifier}"
            )
        if not isinstance(evidence_path, str) or not evidence_path.endswith(
            ".py"
        ):
            raise RuntimeError(
                f"implementation override lacks Python evidence path: {identifier}"
            )
    return payload


def authoritative_bindings(
    path: str | Path | None = None,
) -> dict[str, str]:
    payload = load_authority_manifest(path)
    appendices = payload["appendices"]
    assert isinstance(appendices, dict)
    return {
        str(appendix): str(record["sha256"])
        for appendix, record in appendices.items()
        if isinstance(record, dict)
    }


def implementation_status_overrides(
    path: str | Path | None = None,
) -> dict[str, dict[str, str]]:
    payload = load_authority_manifest(path)
    raw = payload.get("implementation_status_overrides", {})
    assert isinstance(raw, dict)
    return {
        str(identifier): {
            "status": str(record["status"]),
            "reason": str(record["reason"]),
            "evidence_path": str(record["evidence_path"]),
        }
        for identifier, record in raw.items()
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
    status_overrides: Mapping[str, Mapping[str, str]] | None = None,
) -> list[dict[str, str]]:
    active = authoritative_bindings() if bindings is None else dict(bindings)
    promotions = (
        implementation_status_overrides()
        if status_overrides is None
        else {
            str(identifier): dict(record)
            for identifier, record in status_overrides.items()
        }
    )
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for source in rows:
        row = dict(source)
        identifier = row.get("complex_id", "")
        seen.add(identifier)
        recorded_digest = row.get("appendix_source_sha256", "")
        expected = active.get(row.get("appendix_file", ""))
        row["recorded_appendix_source_sha256"] = recorded_digest
        if expected is None:
            row["source_binding_status"] = "unmanaged"
        elif recorded_digest == expected:
            row["source_binding_status"] = "verified"
        else:
            row["source_binding_status"] = "manifest_override"
            row["appendix_source_sha256"] = expected

        recorded_status = row.get("implementation_status", "")
        row["recorded_implementation_status"] = recorded_status
        override = promotions.get(identifier)
        if override is None:
            row["implementation_status_binding"] = "unchanged"
            row["implementation_status_override_reason"] = ""
            row["implementation_status_evidence_path"] = ""
        else:
            evidence_path = str(override["evidence_path"])
            if not (repository_root() / evidence_path).is_file():
                raise RuntimeError(
                    f"implementation override evidence path missing: {evidence_path}"
                )
            row["implementation_status"] = str(override["status"])
            row["implementation_status_binding"] = "manifest_override"
            row["implementation_status_override_reason"] = str(
                override["reason"]
            )
            row["implementation_status_evidence_path"] = evidence_path
        result.append(row)

    missing = sorted(set(promotions) - seen)
    if missing:
        raise RuntimeError(
            f"implementation overrides reference unknown matrix IDs: {missing[:5]}"
        )
    return result


def bind_provenance_manifest(
    payload: Mapping[str, object],
    bindings: Mapping[str, str] | None = None,
) -> dict[str, object]:
    active = authoritative_bindings() if bindings is None else dict(bindings)
    result = deepcopy(dict(payload))
    manifests = result.get("manifests")
    if not isinstance(manifests, list):
        raise RuntimeError(
            "artifact provenance manifest must contain a manifest list"
        )
    for item in manifests:
        if not isinstance(item, dict):
            raise RuntimeError("artifact provenance entries must be objects")
        appendix = str(item.get("appendix_filename", ""))
        recorded = str(item.get("appendix_source_sha256", ""))
        expected = active.get(appendix)
        item["recorded_appendix_source_sha256"] = recorded
        if expected is None:
            item["source_binding_status"] = "unmanaged"
        elif recorded == expected:
            item["source_binding_status"] = "verified"
        else:
            item["source_binding_status"] = "manifest_override"
            item["appendix_source_sha256"] = expected
    return result


def source_binding_report(
    matrix_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
) -> dict[str, object]:
    path = (
        Path(matrix_path)
        if matrix_path is not None
        else default_implementation_matrix()
    )
    with path.open(newline="", encoding="utf-8-sig") as handle:
        raw_rows = list(csv.DictReader(handle))
    bindings = authoritative_bindings(manifest_path)
    promotions = implementation_status_overrides(manifest_path)
    effective_rows = bind_inventory_rows(raw_rows, bindings, promotions)

    raw_mismatches: list[dict[str, str]] = []
    effective_mismatches: list[dict[str, str]] = []
    status_changes: list[dict[str, str]] = []
    appendix_counts: dict[str, dict[str, int | str]] = {}
    for raw, effective in zip(raw_rows, effective_rows, strict=True):
        appendix = raw["appendix_file"]
        expected = bindings.get(appendix)
        if expected is not None:
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
                        "recorded_sha256": raw.get(
                            "appendix_source_sha256",
                            "",
                        ),
                        "authoritative_sha256": expected,
                    }
                )
            if effective.get("appendix_source_sha256") == expected:
                summary["effective_matches"] = int(
                    summary["effective_matches"]
                ) + 1
            else:
                effective_mismatches.append(
                    {
                        "complex_id": effective["complex_id"],
                        "appendix_file": appendix,
                        "effective_sha256": effective.get(
                            "appendix_source_sha256",
                            "",
                        ),
                        "authoritative_sha256": expected,
                    }
                )
        if (
            raw.get("implementation_status")
            != effective.get("implementation_status")
        ):
            status_changes.append(
                {
                    "complex_id": raw["complex_id"],
                    "recorded_status": raw.get("implementation_status", ""),
                    "effective_status": effective.get(
                        "implementation_status",
                        "",
                    ),
                    "reason": effective.get(
                        "implementation_status_override_reason",
                        "",
                    ),
                    "evidence_path": effective.get(
                        "implementation_status_evidence_path",
                        "",
                    ),
                }
            )

    return {
        "schema_version": "1.1",
        "matrix_path": path.as_posix(),
        "total_rows": len(raw_rows),
        "managed_appendices": len(bindings),
        "managed_rows": sum(
            int(item["rows"]) for item in appendix_counts.values()
        ),
        "raw_source_sha_mismatches": len(raw_mismatches),
        "effective_source_sha_mismatches": len(effective_mismatches),
        "source_binding_overrides": len(raw_mismatches),
        "implementation_status_overrides": len(status_changes),
        "implementation_status_changes": status_changes,
        "raw_mismatches": raw_mismatches,
        "effective_mismatches": effective_mismatches,
        "appendices": dict(sorted(appendix_counts.items())),
    }


def provenance_binding_report(
    provenance_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
) -> dict[str, object]:
    path = (
        Path(provenance_path)
        if provenance_path is not None
        else default_artifact_provenance()
    )
    raw_payload = json.loads(path.read_text(encoding="utf-8"))
    bindings = authoritative_bindings(manifest_path)
    effective_payload = bind_provenance_manifest(raw_payload, bindings)
    raw_items = raw_payload.get("manifests")
    effective_items = effective_payload.get("manifests")
    if not isinstance(raw_items, list) or not isinstance(
        effective_items,
        list,
    ):
        raise RuntimeError(
            "artifact provenance manifest must contain a manifest list"
        )

    raw_mismatches: list[dict[str, str]] = []
    effective_mismatches: list[dict[str, str]] = []
    for raw, effective in zip(raw_items, effective_items, strict=True):
        assert isinstance(raw, dict) and isinstance(effective, dict)
        appendix = str(raw.get("appendix_filename", ""))
        expected = bindings.get(appendix)
        if expected is None:
            continue
        if raw.get("appendix_source_sha256") != expected:
            raw_mismatches.append(
                {
                    "theorem_complex_id": str(
                        raw.get("theorem_complex_id", "")
                    ),
                    "appendix_filename": appendix,
                    "recorded_sha256": str(
                        raw.get("appendix_source_sha256", "")
                    ),
                    "authoritative_sha256": expected,
                }
            )
        if effective.get("appendix_source_sha256") != expected:
            effective_mismatches.append(
                {
                    "theorem_complex_id": str(
                        effective.get("theorem_complex_id", "")
                    ),
                    "appendix_filename": appendix,
                    "effective_sha256": str(
                        effective.get("appendix_source_sha256", "")
                    ),
                    "authoritative_sha256": expected,
                }
            )

    return {
        "schema_version": "1.0",
        "provenance_path": path.as_posix(),
        "total_manifests": len(raw_items),
        "raw_source_sha_mismatches": len(raw_mismatches),
        "effective_source_sha_mismatches": len(effective_mismatches),
        "source_binding_overrides": len(raw_mismatches),
        "raw_mismatches": raw_mismatches,
        "effective_mismatches": effective_mismatches,
    }
