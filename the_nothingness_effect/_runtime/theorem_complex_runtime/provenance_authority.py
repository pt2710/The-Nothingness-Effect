"""Observational, recertification-aware authority binding for provenance records.

Producer manifests retain the digest recorded at generation time.  Historical
source drift is never hidden by overwriting that digest; an explicit
recertification record may instead establish byte-backed exactness through the
separate ``recertified_appendix_source_sha256`` field.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Mapping

from . import _authority_impl as _impl
from .authority import (
    authoritative_bindings,
    recertified_source_bindings,
)


def bind_provenance_manifest(
    payload: Mapping[str, object],
    bindings: Mapping[str, str] | None = None,
) -> dict[str, object]:
    active = authoritative_bindings() if bindings is None else dict(bindings)
    recertified = recertified_source_bindings()
    result = deepcopy(dict(payload))
    manifests = result.get("manifests")
    if not isinstance(manifests, list):
        raise RuntimeError("artifact provenance manifest must contain a manifest list")

    for item in manifests:
        if not isinstance(item, dict):
            raise RuntimeError("artifact provenance entries must be objects")
        identifier = str(item.get("theorem_complex_id", ""))
        appendix = str(item.get("appendix_filename", ""))
        recorded = str(item.get("appendix_source_sha256", ""))
        expected = active.get(appendix)
        record = recertified.get(identifier)

        item["recorded_appendix_source_sha256"] = recorded
        item.pop("recertified_appendix_source_sha256", None)
        if expected is None:
            item["source_binding_status"] = "unmanaged"
            item["source_exactness"] = "unverified"
        elif recorded == expected:
            item["source_binding_status"] = "verified"
            item["source_exactness"] = "exact"
        elif (
            record is not None
            and record["appendix_file"] == appendix
            and record["authoritative_appendix_sha256"] == expected
            and record["recertification_status"] == "byte_verified_label_reaudited"
        ):
            item["source_binding_status"] = "recertified"
            item["source_exactness"] = "exact"
            item["recertified_appendix_source_sha256"] = expected
        else:
            item["source_binding_status"] = "mismatch"
            item["source_exactness"] = "stale"
    return result


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
    if not isinstance(items, list):
        raise RuntimeError("artifact provenance manifest must contain a manifest list")

    raw_mismatches = [
        {
            "theorem_complex_id": str(item.get("theorem_complex_id", "")),
            "appendix_file": str(item.get("appendix_filename", "")),
            "recorded_sha256": str(item.get("recorded_appendix_source_sha256", "")),
            "authoritative_sha256": bindings.get(
                str(item.get("appendix_filename", "")), ""
            ),
        }
        for item in items
        if str(item.get("appendix_filename", "")) in bindings
        and str(item.get("recorded_appendix_source_sha256", ""))
        != bindings[str(item.get("appendix_filename", ""))]
    ]
    recertifications = [
        {
            "theorem_complex_id": str(item.get("theorem_complex_id", "")),
            "appendix_file": str(item.get("appendix_filename", "")),
            "recorded_sha256": str(item.get("recorded_appendix_source_sha256", "")),
            "authoritative_sha256": str(
                item.get("recertified_appendix_source_sha256", "")
            ),
        }
        for item in items
        if item.get("source_binding_status") == "recertified"
    ]
    effective_mismatches = [
        {
            "theorem_complex_id": str(item.get("theorem_complex_id", "")),
            "appendix_file": str(item.get("appendix_filename", "")),
            "recorded_sha256": str(item.get("recorded_appendix_source_sha256", "")),
            "authoritative_sha256": bindings.get(
                str(item.get("appendix_filename", "")), ""
            ),
        }
        for item in items
        if item.get("source_binding_status") == "mismatch"
    ]
    return {
        "schema_version": "2.1",
        "provenance_path": path.as_posix(),
        "total_manifests": len(items),
        "managed_appendices": len(bindings),
        "raw_source_sha_mismatches": len(raw_mismatches),
        "source_recertifications": len(recertifications),
        "effective_source_sha_mismatches": len(effective_mismatches),
        "source_binding_overrides": 0,
        "raw_mismatches": raw_mismatches,
        "recertifications": recertifications,
        "effective_mismatches": effective_mismatches,
    }
