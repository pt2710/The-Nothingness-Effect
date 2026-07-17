"""Strict byte-backed authority binding and reviewed implementation promotions.

The authoritative source of truth is the committed immutable ZIP snapshot
declared by ``docs/data/authoritative_archive_manifest.json``.  Binding is
observational: source digests are compared and annotated, never overwritten.
"""

from __future__ import annotations

from copy import deepcopy
import csv
import json
from pathlib import Path
from typing import Iterable, Mapping

from . import _authority_impl as _impl
from ._authority_impl import *  # noqa: F401,F403
from .types import ComplexContract


_BASE_IMPLEMENTATION_STATUS_OVERRIDES = _impl.implementation_status_overrides


def default_archive_manifest() -> Path:
    return _impl.repository_root() / "docs" / "data" / "authoritative_archive_manifest.json"


def load_archive_manifest(path: str | Path | None = None) -> dict[str, object]:
    manifest_path = Path(path) if path is not None else default_archive_manifest()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "2.0":
        raise RuntimeError("authoritative archive manifest must use schema version 2.0")
    members = payload.get("members")
    if not isinstance(members, dict) or not members:
        raise RuntimeError("authoritative archive manifest has no members")
    archive_sha = payload.get("archive_sha256")
    if not isinstance(archive_sha, str) or len(archive_sha) != 64:
        raise RuntimeError("authoritative archive SHA-256 is invalid")
    for filename, record in members.items():
        if not isinstance(filename, str) or not isinstance(record, dict):
            raise RuntimeError("invalid authoritative archive member")
        digest = record.get("sha256")
        role = record.get("role")
        if not isinstance(digest, str) or len(digest) != 64:
            raise RuntimeError(f"invalid member SHA-256: {filename}")
        if role not in {
            "theorem_runtime",
            "commentary_validation",
            "research_relations",
            "canonical_input_order",
        }:
            raise RuntimeError(f"invalid archive role: {filename}")
    return payload


def authoritative_bindings(
    path: str | Path | None = None,
) -> dict[str, str]:
    payload = load_archive_manifest(path)
    members = payload["members"]
    assert isinstance(members, dict)
    return {
        str(filename): str(record["sha256"])
        for filename, record in members.items()
        if isinstance(record, dict) and record.get("role") == "theorem_runtime"
    }


def default_override_directory() -> Path:
    return _impl.repository_root() / "docs" / "data" / "authority_overrides"


def default_recertification_manifest() -> Path:
    return (
        _impl.repository_root()
        / "docs"
        / "data"
        / "source_recertification"
        / "authoritative_recertification_101.json"
    )


def recertified_source_bindings() -> dict[str, dict[str, str]]:
    path = default_recertification_manifest()
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "2.0":
        raise RuntimeError("source recertification manifest must use schema 2.0")
    appendices = payload.get("appendices")
    if not isinstance(appendices, dict):
        raise RuntimeError("source recertification manifest lacks appendices")
    result: dict[str, dict[str, str]] = {}
    for appendix, record in appendices.items():
        if not isinstance(record, dict):
            raise RuntimeError("invalid source recertification appendix record")
        identifiers = record.get("complex_ids")
        if not isinstance(identifiers, list):
            raise RuntimeError("recertification appendix lacks complex IDs")
        for identifier in identifiers:
            identifier = str(identifier)
            if not identifier or identifier in result:
                raise RuntimeError("duplicate or empty recertification ID")
            result[identifier] = {
                "appendix_file": str(appendix),
                "authoritative_appendix_sha256": str(
                    record["authoritative_appendix_sha256"]
                ),
                "recertification_status": str(record["recertification_status"]),
            }
    if len(result) != int(payload.get("total_complexes", -1)):
        raise RuntimeError("source recertification cardinality mismatch")
    return result


def _load_override_file(
    path: Path,
) -> tuple[str, dict[str, dict[str, str]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") not in {"1.0", "1.1"}:
        raise RuntimeError(f"authority override manifest has invalid schema: {path}")
    mode = str(payload.get("override_mode", "add"))
    if mode not in {"add", "replace"}:
        raise RuntimeError(f"invalid authority override mode: {path}")
    raw = payload.get("implementation_status_overrides")
    if not isinstance(raw, dict) or not raw:
        raise RuntimeError(f"authority override manifest is empty: {path}")
    result: dict[str, dict[str, str]] = {}
    for identifier, record in raw.items():
        if not isinstance(identifier, str) or not identifier:
            raise RuntimeError(f"invalid authority override identifier: {path}")
        if not isinstance(record, dict) or record.get("status") != "implemented":
            raise RuntimeError(f"invalid authority override record: {identifier}")
        reason = record.get("reason")
        evidence_path = record.get("evidence_path")
        if not isinstance(reason, str) or not reason.strip():
            raise RuntimeError(f"authority override lacks reason: {identifier}")
        if not isinstance(evidence_path, str) or not evidence_path.endswith(".py"):
            raise RuntimeError(
                f"authority override lacks Python evidence path: {identifier}"
            )
        result[identifier] = {
            "status": "implemented",
            "reason": reason,
            "evidence_path": evidence_path,
        }
    return mode, result


def implementation_status_overrides(
    path: str | Path | None = None,
) -> dict[str, dict[str, str]]:
    result = _BASE_IMPLEMENTATION_STATUS_OVERRIDES(path)
    if path is not None and Path(path) != _impl.default_authority_manifest():
        return result
    directory = default_override_directory()
    if not directory.is_dir():
        return result
    for manifest_path in sorted(directory.glob("*.json")):
        mode, additions = _load_override_file(manifest_path)
        overlap = sorted(set(result) & set(additions))
        if mode == "add" and overlap:
            raise RuntimeError(
                f"duplicate authority overrides across manifests: {overlap[:5]}"
            )
        if mode == "replace":
            missing = sorted(set(additions) - set(result))
            if missing:
                raise RuntimeError(
                    f"replacement authority overrides are unknown: {missing[:5]}"
                )
        result.update(additions)
    return result


def bind_contract(
    contract: ComplexContract,
    bindings: Mapping[str, str] | None = None,
) -> ComplexContract:
    """Return the contract unchanged; authority mismatches must remain visible."""
    return contract


def bind_contracts(
    contracts: Iterable[ComplexContract],
    bindings: Mapping[str, str] | None = None,
) -> tuple[ComplexContract, ...]:
    return tuple(contracts)


def bind_inventory_rows(
    rows: Iterable[Mapping[str, str]],
    bindings: Mapping[str, str] | None = None,
    status_overrides: Mapping[str, Mapping[str, str]] | None = None,
) -> list[dict[str, str]]:
    active = authoritative_bindings() if bindings is None else dict(bindings)
    promotions = (
        implementation_status_overrides()
        if status_overrides is None
        else {str(identifier): dict(record) for identifier, record in status_overrides.items()}
    )
    recertified = recertified_source_bindings()
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for source in rows:
        row = dict(source)
        identifier = row.get("complex_id", "")
        seen.add(identifier)
        recorded_digest = row.get("appendix_source_sha256", "")
        expected = active.get(row.get("appendix_file", ""))
        row["recorded_appendix_source_sha256"] = recorded_digest
        recertification = recertified.get(identifier)
        if expected is None:
            row["source_binding_status"] = "unmanaged"
            row["source_exactness"] = "unverified"
        elif recorded_digest == expected:
            row["source_binding_status"] = "verified"
            row["source_exactness"] = "exact"
        elif (
            recertification is not None
            and recertification["appendix_file"] == row.get("appendix_file", "")
            and recertification["authoritative_appendix_sha256"] == expected
            and recertification["recertification_status"]
            == "byte_verified_label_reaudited"
        ):
            row["source_binding_status"] = "recertified"
            row["source_exactness"] = "exact"
            row["recertified_appendix_source_sha256"] = expected
        else:
            row["source_binding_status"] = "mismatch"
            row["source_exactness"] = "stale"

        recorded_status = row.get("implementation_status", "")
        row["recorded_implementation_status"] = recorded_status
        override = promotions.get(identifier)
        if override is None:
            row["implementation_status_binding"] = "unchanged"
            row["implementation_status_override_reason"] = ""
            row["implementation_status_evidence_path"] = ""
        else:
            evidence_path = str(override["evidence_path"])
            if not (_impl.repository_root() / evidence_path).is_file():
                raise RuntimeError(
                    f"implementation override evidence path missing: {evidence_path}"
                )
            row["implementation_status"] = str(override["status"])
            row["implementation_status_binding"] = "reviewed_override"
            row["implementation_status_override_reason"] = str(override["reason"])
            row["implementation_status_evidence_path"] = evidence_path
        row["runtime_status"] = (
            "implemented" if row.get("implementation_status") == "implemented" else "missing"
        )
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
        raise RuntimeError("artifact provenance manifest must contain a manifest list")
    for item in manifests:
        if not isinstance(item, dict):
            raise RuntimeError("artifact provenance entries must be objects")
        appendix = str(item.get("appendix_filename", ""))
        recorded = str(item.get("appendix_source_sha256", ""))
        expected = active.get(appendix)
        item["recorded_appendix_source_sha256"] = recorded
        if expected is None:
            item["source_binding_status"] = "unmanaged"
            item["source_exactness"] = "unverified"
        elif recorded == expected:
            item["source_binding_status"] = "verified"
            item["source_exactness"] = "exact"
        else:
            item["source_binding_status"] = "mismatch"
            item["source_exactness"] = "stale"
    return result


def source_binding_report(
    matrix_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
) -> dict[str, object]:
    path = Path(matrix_path) if matrix_path is not None else _impl.default_implementation_matrix()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        raw_rows = list(csv.DictReader(handle))
    bindings = authoritative_bindings(manifest_path)
    effective_rows = bind_inventory_rows(raw_rows, bindings)
    raw_mismatches = []
    effective_mismatches = []
    recertifications = []
    changes = []
    counts: dict[str, dict[str, int | str]] = {}
    for raw, effective in zip(raw_rows, effective_rows, strict=True):
        appendix = raw["appendix_file"]
        expected = bindings.get(appendix)
        if expected is not None:
            summary = counts.setdefault(
                appendix,
                {
                    "rows": 0,
                    "raw_exact": 0,
                    "recertified": 0,
                    "mismatches": 0,
                    "authoritative_sha256": expected,
                },
            )
            summary["rows"] = int(summary["rows"]) + 1
            if raw.get("appendix_source_sha256") == expected:
                summary["raw_exact"] = int(summary["raw_exact"]) + 1
            else:
                raw_mismatches.append(
                    {
                        "complex_id": raw["complex_id"],
                        "appendix_file": appendix,
                        "recorded_sha256": raw.get("appendix_source_sha256", ""),
                        "authoritative_sha256": expected,
                    }
                )
            if effective["source_binding_status"] == "recertified":
                summary["recertified"] = int(summary["recertified"]) + 1
                recertifications.append(
                    {
                        "complex_id": raw["complex_id"],
                        "appendix_file": appendix,
                        "recorded_sha256": raw.get("appendix_source_sha256", ""),
                        "authoritative_sha256": expected,
                    }
                )
            elif effective["source_binding_status"] == "mismatch":
                summary["mismatches"] = int(summary["mismatches"]) + 1
                effective_mismatches.append(
                    {
                        "complex_id": raw["complex_id"],
                        "appendix_file": appendix,
                        "recorded_sha256": raw.get("appendix_source_sha256", ""),
                        "authoritative_sha256": expected,
                    }
                )
        if raw.get("implementation_status") != effective.get("implementation_status"):
            changes.append(
                {
                    "complex_id": raw["complex_id"],
                    "recorded_status": raw.get("implementation_status", ""),
                    "effective_status": effective.get("implementation_status", ""),
                    "reason": effective.get("implementation_status_override_reason", ""),
                    "evidence_path": effective.get("implementation_status_evidence_path", ""),
                }
            )
    return {
        "schema_version": "2.0",
        "matrix_path": path.as_posix(),
        "total_rows": len(raw_rows),
        "managed_appendices": len(bindings),
        "managed_rows": sum(int(item["rows"]) for item in counts.values()),
        "raw_source_sha_mismatches": len(raw_mismatches),
        "effective_source_sha_mismatches": len(effective_mismatches),
        "source_binding_overrides": 0,
        "source_recertifications": len(recertified_source_bindings()),
        "implementation_status_overrides": len(changes),
        "implementation_status_changes": changes,
        "raw_mismatches": raw_mismatches,
        "recertifications": recertifications,
        "effective_mismatches": effective_mismatches,
        "appendices": dict(sorted(counts.items())),
    }


def provenance_binding_report(
    provenance_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
) -> dict[str, object]:
    path = (
        Path(provenance_path)
        if provenance_path is not None
        else _impl.default_artifact_provenance()
    )
    raw = json.loads(path.read_text(encoding="utf-8"))
    bindings = authoritative_bindings(manifest_path)
    effective = bind_provenance_manifest(raw, bindings)
    items = effective.get("manifests")
    assert isinstance(items, list)
    mismatches = [
        {
            "theorem_complex_id": str(item.get("theorem_complex_id", "")),
            "appendix_file": str(item.get("appendix_filename", "")),
            "recorded_sha256": str(item.get("appendix_source_sha256", "")),
            "authoritative_sha256": bindings.get(str(item.get("appendix_filename", "")), ""),
        }
        for item in items
        if str(item.get("appendix_filename", "")) in bindings
        and str(item.get("appendix_source_sha256", ""))
        != bindings[str(item.get("appendix_filename", ""))]
    ]
    return {
        "schema_version": "2.0",
        "provenance_path": path.as_posix(),
        "total_manifests": len(items),
        "managed_appendices": len(bindings),
        "effective_source_sha_mismatches": len(mismatches),
        "raw_source_sha_mismatches": len(mismatches),
        "source_binding_overrides": 0,
        "effective_mismatches": mismatches,
        "raw_mismatches": mismatches,
    }


# Patch the preserved implementation module because its report functions resolve
# globals in that module at call time.
_impl.authoritative_bindings = authoritative_bindings
_impl.implementation_status_overrides = implementation_status_overrides
_impl.bind_contract = bind_contract
_impl.bind_contracts = bind_contracts
_impl.bind_inventory_rows = bind_inventory_rows
_impl.bind_provenance_manifest = bind_provenance_manifest
_impl.source_binding_report = source_binding_report
_impl.provenance_binding_report = provenance_binding_report
