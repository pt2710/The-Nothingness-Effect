"""Activate the 31 typed A-level dependency sources and synchronize inventories."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import shutil

from the_nothingness_effect._runtime.theorem_complex_runtime.dependency_sources import (
    FAMILY_IDS,
    SPEC_BY_ID,
    source_ids,
)

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/data/theorem_complex_implementation_matrix.csv"
REPORT_MATRIX = ROOT / "reports/theorem_complex_implementation_matrix.csv"
SOURCE_REGISTRY = ROOT / "docs/data/source_law_registry.json"
REPORT_SOURCE_REGISTRY = ROOT / "reports/source_law_registry.json"
MASTER_MANIFEST = ROOT / "reports/theorem_complex_manifest.json"
TEST_PATH = "tests/contracts/test_dependency_source_contracts.py"
SIMULATION_PATH = "tools/generate_artifact_provenance.py"
ARTIFACT_PATH = "docs/data/artifact_provenance_manifest.json"
IMPLEMENTATIONS = {
    "qenn": "the_nothingness_effect/artificial_intelligence/qenn/dependency_sources.py",
    "pgqenn": "the_nothingness_effect/artificial_intelligence/pgqenn/dependency_sources.py",
    "soinets": "the_nothingness_effect/artificial_intelligence/soinets/dependency_sources.py",
    "dfi": "the_nothingness_effect/fluctuation_and_elastic_dynamics/dynamic_fluctuation_index/dependency_sources.py",
}
TARGETS = set(source_ids())
STATUS_REASON = (
    "current authoritative A-level source law implemented as a typed finite operator "
    "with a separate algebraic invariant residual and explicit failure-dual field"
)
DECISION_NOTE = (
    "Activated in phase 2 to close the upstream dependency graph; finite computational "
    "evidence is not promoted to a formal proof or physical existence claim."
)


def _family(identifier: str) -> str:
    for family, identifiers in FAMILY_IDS.items():
        if identifier in identifiers:
            return family
    raise KeyError(identifier)


def _read_matrix(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or ())


def _write_matrix(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _update_manifest(value: dict[str, object], implementation_path: str) -> None:
    value["status"] = "implemented"
    value["status_reason"] = STATUS_REASON
    value["implementation_modules"] = [implementation_path]
    value["test_modules"] = sorted(set([*value.get("test_modules", []), TEST_PATH]))
    value["simulation_modules"] = [SIMULATION_PATH]
    value["artifact_manifests"] = [ARTIFACT_PATH]
    value["known_limitations"] = [
        "finite computational witness only",
        "failure-dual magnitude is diagnostic and not a formal theorem proof",
    ]
    falsification = dict(value.get("falsification", {}))
    falsification["execution_status"] = "implemented"
    falsification["obligations"] = [
        "domain/codomain guards",
        "theorem-law invariant",
        "failure-dual counterexample",
        "finite/NaN checks",
    ]
    value["falsification"] = falsification
    value["required_tests"] = falsification["obligations"]
    value["required_artifacts"] = [
        "JSON artifact manifest",
        "CSV source metrics",
        "failure-dual diagnostic trace",
    ]
    value["mathematical_contract"] = {
        "closure_predicate": None,
        "codomain": {
            "type": "DependencySourceResult",
            "description": "response field, invariant residual, diagnostic, and failure-dual field",
        },
        "domain": {
            "type": "DependencySourceInput",
            "description": "finite primary and auxiliary rank-two witness fields",
        },
        "exact_semantics": True,
        "invariant": "algebraic reconstruction residual <= tolerance",
        "operator": "source_operator",
        "parameter_constraints": [
            "finite common-shape fields",
            "non-negative tolerance",
            "strictly positive failure_scale",
        ],
        "residual": "invariant_residual",
        "simulation_runner": SIMULATION_PATH,
        "source_removal_check_count": 0,
    }


def activate_matrix() -> dict[str, dict[str, str]]:
    rows, fieldnames = _read_matrix(MATRIX)
    by_id = {row["complex_id"]: row for row in rows}
    missing = TARGETS - by_id.keys()
    if missing:
        raise RuntimeError(f"phase-2 source IDs absent from matrix: {sorted(missing)}")
    for identifier in TARGETS:
        row = by_id[identifier]
        implementation = IMPLEMENTATIONS[_family(identifier)]
        row.update(
            {
                "implementation_status": "implemented",
                "implementation_path": implementation,
                "test_path": TEST_PATH,
                "simulation_path": SIMULATION_PATH,
                "visualization_path": ARTIFACT_PATH,
                "required_tests": "domain/codomain guards; theorem-law invariant; failure-dual counterexample; finite/NaN checks",
                "required_artifacts": "JSON artifact manifest + CSV source metrics + failure-dual diagnostic trace",
                "artifact_status": "generator_smoke_tested",
                "decision_note": DECISION_NOTE,
                "dependency_status": "authoritative_cross_reference",
                "status_reason": STATUS_REASON,
                "carrier_violation": "false",
            }
        )
    _write_matrix(MATRIX, rows, fieldnames)
    shutil.copyfile(MATRIX, REPORT_MATRIX)
    return by_id


def activate_individual_manifests(matrix_by_id: dict[str, dict[str, str]]) -> None:
    for identifier in TARGETS:
        row = matrix_by_id[identifier]
        path = ROOT / row["theorem_complex_path"] / "manifest.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("complex_id") != identifier:
            raise RuntimeError(f"manifest ID mismatch at {path}: {value.get('complex_id')} != {identifier}")
        _update_manifest(value, IMPLEMENTATIONS[_family(identifier)])
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def activate_master_manifest() -> None:
    value = json.loads(MASTER_MANIFEST.read_text(encoding="utf-8"))
    complexes = value.get("complexes", [])
    by_id = {item["complex_id"]: item for item in complexes}
    missing = TARGETS - by_id.keys()
    if missing:
        raise RuntimeError(f"phase-2 source IDs absent from master manifest: {sorted(missing)}")
    for identifier in TARGETS:
        _update_manifest(by_id[identifier], IMPLEMENTATIONS[_family(identifier)])
    if "implementation_status_counts" in value:
        implemented = sum(item.get("status") == "implemented" for item in complexes)
        value["implementation_status_counts"] = {
            "implemented": implemented,
            "proxy": len(complexes) - implemented,
        }
    MASTER_MANIFEST.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def activate_source_registry() -> None:
    value = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    laws = value["source_laws"]
    by_id = {item["complex_id"]: item for item in laws}
    missing = TARGETS - by_id.keys()
    if missing:
        raise RuntimeError(f"phase-2 source IDs absent from source registry: {sorted(missing)}")
    for identifier in TARGETS:
        item = by_id[identifier]
        item["implementation_status"] = "implemented"
        item["status_reason"] = STATUS_REASON
    implemented = sum(item["implementation_status"] == "implemented" for item in laws)
    value["inventory_summary"]["implementation_status_counts"] = {
        "implemented": implemented,
        "proxy": len(laws) - implemented,
    }
    SOURCE_REGISTRY.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    shutil.copyfile(SOURCE_REGISTRY, REPORT_SOURCE_REGISTRY)


def verify_activation() -> None:
    rows, _ = _read_matrix(MATRIX)
    active = {row["complex_id"] for row in rows if row["implementation_status"] == "implemented"}
    missing = TARGETS - active
    if missing:
        raise RuntimeError(f"phase-2 activation incomplete: {sorted(missing)}")
    if len(TARGETS) != 31 or len(SPEC_BY_ID) != 31:
        raise RuntimeError(f"phase-2 source count changed: targets={len(TARGETS)} specs={len(SPEC_BY_ID)}")


def main() -> None:
    matrix = activate_matrix()
    activate_individual_manifests(matrix)
    activate_master_manifest()
    activate_source_registry()
    verify_activation()
    print(
        "dependency_sources_phase2=activated "
        f"sources={len(TARGETS)} expected_requested_implemented=226 expected_dependency_downgrades=0"
    )


if __name__ == "__main__":
    main()
