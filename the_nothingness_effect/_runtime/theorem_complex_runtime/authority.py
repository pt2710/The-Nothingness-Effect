"""Fail-closed authority binding with modular reviewed promotion manifests.

The base implementation remains byte-identical in ``_authority_impl.py``.
Additional implementation promotions are loaded only from validated JSON files
under ``docs/data/authority_overrides`` and are merged fail-closed.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import _authority_impl as _impl
from ._authority_impl import *  # noqa: F401,F403


_BASE_IMPLEMENTATION_STATUS_OVERRIDES = _impl.implementation_status_overrides


def default_override_directory() -> Path:
    return _impl.repository_root() / "docs" / "data" / "authority_overrides"


def _load_override_file(path: Path) -> dict[str, dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0":
        raise RuntimeError(f"authority override manifest has invalid schema: {path}")
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
    return result


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
        additions = _load_override_file(manifest_path)
        overlap = sorted(set(result) & set(additions))
        if overlap:
            raise RuntimeError(
                f"duplicate authority overrides across manifests: {overlap[:5]}"
            )
        result.update(additions)
    return result


_impl.implementation_status_overrides = implementation_status_overrides
