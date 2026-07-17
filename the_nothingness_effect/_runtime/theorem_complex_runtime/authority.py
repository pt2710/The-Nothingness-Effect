"""Strict byte-backed authority binding and reviewed implementation promotions.

The authoritative source of truth is the immutable external ZIP snapshot declared
by ``docs/data/authoritative_archive_manifest.json``. Binding is observational:
source digests are compared and annotated, never overwritten.
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
_SUPPORTED_ARCHIVE_MANIFEST_SCHEMAS = {"2.0", "2.1"}


def default_archive_manifest() -> Path:
    return _impl.repository_root() / "docs" / "data" / "authoritative_archive_manifest.json"


def load_archive_manifest(path: str | Path | None = None) -> dict[str, object]:
    manifest_path = Path(path) if path is not None else default_archive_manifest()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    schema_version = str(payload.get("schema_version", ""))
    if schema_version not in _SUPPORTED_ARCHIVE_MANIFEST_SCHEMAS:
        raise RuntimeError(
            "authoritative archive manifest must use a supported schema version: "
            f"{sorted(_SUPPORTED_ARCHIVE_MANIFEST_SCHEMAS)}"
        )
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
    delivery = payload.get("archive_delivery")
    if schema_version == "2.1" and delivery not in {
        "private_authenticated_envelope",
        "external_ci_artifact_required",
    }:
        raise RuntimeError("schema 2.1 archive manifest has invalid delivery mode")
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
        if effective.get("implementation_status_binding") == "reviewed_override":
            changes.append(
                {
                    "complex_id": raw["complex_id"],
                    "from": raw.get("implementation_status", ""),
                    "to": effective.get("implementation_status", ""),
                    "reason": effective.get("implementation_status_override_reason", ""),
                    "evidence_path": effective.get("implementation_status_evidence_path", ""),
                }
            )
    return {
        "schema_version": "2.0",
        "authority_policy": "observational_no_sha_overwrite",
        "source_binding_overrides": 0,
        "bindings": bindings,
        "appendix_counts": counts,
        "raw_source_mismatches": raw_mismatches,
        "raw_source_mismatch_count": len(raw_mismatches),
        "historical_recertifications": recertifications,
        "historical_recertification_count": len(recertifications),
        "effective_source_mismatches": effective_mismatches,
        "effective_source_mismatch_count": len(effective_mismatches),
        "implementation_status_changes": changes,
        "implementation_status_change_count": len(changes),
    }
