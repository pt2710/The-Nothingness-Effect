"""Auditable activation overlay for newly recertified executable contracts."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping


CLAIM_BOUNDARY = "finite computational support; not a formal proof substitute"
START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_activation_manifest() -> Path:
    return repository_root() / "docs" / "data" / "implementation_activation_overrides.json"


def load_activation_records(path: str | Path | None = None) -> dict[str, dict[str, object]]:
    source = Path(path) if path is not None else default_activation_manifest()
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0":
        raise RuntimeError("implementation activation manifest must use schema version 1.0")
    groups = payload.get("groups")
    if not isinstance(groups, list) or not groups:
        raise RuntimeError("implementation activation manifest must contain groups")

    records: dict[str, dict[str, object]] = {}
    for group in groups:
        if not isinstance(group, dict):
            raise RuntimeError("implementation activation groups must be objects")
        identifiers = group.get("complex_ids")
        if not isinstance(identifiers, list) or not identifiers:
            raise RuntimeError("implementation activation group lacks complex IDs")
        for identifier in identifiers:
            if not isinstance(identifier, str) or not identifier:
                raise RuntimeError("implementation activation ID must be nonempty text")
            if identifier in records:
                raise RuntimeError(f"duplicate implementation activation: {identifier}")
            records[identifier] = {
                "complex_id": identifier,
                "effective_status": payload.get("effective_status", "implemented"),
                "activation_reason": payload.get("activation_reason", "recertified executable contract"),
                "exact_semantics": bool(payload.get("exact_semantics", False)),
                "claim_boundary": payload.get("claim_boundary", CLAIM_BOUNDARY),
                "module": group.get("module", ""),
                "implementation_path": group.get("implementation_path", ""),
                "test_path": group.get("test_path", ""),
                "simulation_path": group.get("simulation_path", ""),
            }
    if len(records) != 31:
        raise RuntimeError(f"expected 31 recertified A-source activations, found {len(records)}")
    return records


def apply_inventory_activations(
    rows: Iterable[Mapping[str, str]],
    records: Mapping[str, Mapping[str, object]] | None = None,
) -> list[dict[str, str]]:
    active = load_activation_records() if records is None else dict(records)
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for source in rows:
        row = dict(source)
        identifier = row.get("complex_id", "")
        activation = active.get(identifier)
        row["recorded_implementation_status"] = row.get("implementation_status", "")
        row["recorded_implementation_path"] = row.get("implementation_path", "")
        row["recorded_test_path"] = row.get("test_path", "")
        row["recorded_simulation_path"] = row.get("simulation_path", "")
        if activation is None:
            row["activation_status"] = "unchanged"
        else:
            seen.add(identifier)
            row["activation_status"] = "recertified_override"
            row["implementation_status"] = str(activation["effective_status"])
            row["baseline_status"] = "recertified_executable_source"
            row["implementation_path"] = str(activation["implementation_path"])
            row["test_path"] = str(activation["test_path"])
            row["simulation_path"] = str(activation["simulation_path"])
            row["dependency_status"] = "source contract implemented"
            row["status_reason"] = str(activation["activation_reason"])
            row["decision_note"] = str(activation["activation_reason"])
        result.append(row)
    missing = sorted(set(active) - seen)
    if missing:
        raise RuntimeError(f"activation IDs are absent from theorem inventory: {missing[:5]}")
    return result


def apply_provenance_activations(
    payload: Mapping[str, object],
    inventory_rows: Iterable[Mapping[str, str]],
    records: Mapping[str, Mapping[str, object]] | None = None,
) -> dict[str, object]:
    active = load_activation_records() if records is None else dict(records)
    rows = {str(row["complex_id"]): dict(row) for row in inventory_rows}
    result = deepcopy(dict(payload))
    manifests = result.get("manifests")
    if not isinstance(manifests, list):
        raise RuntimeError("artifact provenance manifest must contain a manifest list")
    existing = {
        str(item.get("theorem_complex_id", ""))
        for item in manifests
        if isinstance(item, dict)
    }
    for identifier, activation in sorted(active.items()):
        if identifier in existing:
            continue
        row = rows.get(identifier)
        if row is None:
            raise RuntimeError(f"activated provenance ID absent from matrix: {identifier}")
        encoded = json.dumps(activation, sort_keys=True, separators=(",", ":")).encode()
        manifests.append(
            {
                "appendix_filename": row["appendix_file"],
                "appendix_source_sha256": row["appendix_source_sha256"],
                "approximation_metadata": {
                    "activation_overlay": True,
                    "exact_semantics": bool(activation["exact_semantics"]),
                    "formal_proof_substitute": False,
                },
                "claim_boundary": activation["claim_boundary"],
                "closure_status": "numerical_candidate",
                "generated_files": [],
                "evidence_files": [
                    activation["implementation_path"],
                    activation["test_path"],
                    activation["simulation_path"],
                ],
                "numeric_tolerances": {"absolute": 1e-6},
                "parameter_hash": hashlib.sha256(encoded).hexdigest(),
                "parameters": {
                    "fixture": "recertified-a-source-contract-v1",
                    "module": activation["module"],
                },
                "regeneration_command": f"python -m pytest -q {activation['test_path']}",
                "repository_result_commit": "generated-at-runtime",
                "repository_start_commit": START_COMMIT,
                "residual_vector": [],
                "seed": 0,
                "theorem_complex_id": identifier,
            }
        )
    manifests.sort(key=lambda item: str(item.get("theorem_complex_id", "")))
    summary = result.get("summary")
    if isinstance(summary, dict):
        summary["theorem_manifests"] = len(manifests)
        summary["activation_overlay_manifests"] = len(active)
    result["activation_overlay"] = {
        "count": len(active),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    return result
