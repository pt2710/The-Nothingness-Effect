"""Fail-closed gates for externally maintained authoritative appendix bindings."""

from __future__ import annotations

from collections import Counter
import csv
import json
from pathlib import Path

from the_nothingness_effect._runtime.theorem_complex_runtime.authority import (
    authoritative_bindings,
    bind_inventory_rows,
    bind_provenance_manifest,
    implementation_status_overrides,
    provenance_binding_report,
    source_binding_report,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import (
    all_contracts,
    dependency_downgrades,
    release_statuses,
)
from tools.export_effective_theorem_matrix import export, export_provenance

EXPECTED = {
    "appendix_canonical_self_negating_involution_flowpoint.tex": "5c44d82b34cd4c5d05d01253a62987f2f6099d582bf954a4cbdbc13b52b52206",
    "appendix_tne_mathematical_closure_architecture.tex": "3cd520d5b025f6f241c7eb09417528276f0c6904e07aa088057c7b57803bf011",
    "appendix_tne_foundational_closure_architecture.tex": "5e459eed3eca36d1342bc879fc8ac3962f3c801bfd1aab733f3db081a7ed0c69",
    "appendix_the_completeness_theorem.tex": "1a186b3350f16c284b3cb54f7dfb63d6729d98142e9fb8b53c6de4d9ce3d84f3",
}
FOUNDATIONAL = "appendix_tne_foundational_closure_architecture.tex"
BASE_IMPLEMENTED = 195
FOUNDATIONAL_BASE_IMPLEMENTED = 14
PROMOTED_DFI = {
    "dfi_uniqueness_of_decomposition_and_mapping_ambiguity",
    "dfi_flowpoint_consistency_and_interface_inconsistency",
    "dfi_simulation_consistency_and_simulation_breakdown",
}
EXPECTED_PROMOTION_PATH_COUNTS = {
    "the_nothingness_effect/artificial_intelligence/qenn/source_contracts.py": 8,
    "the_nothingness_effect/artificial_intelligence/pgqenn/source_contracts.py": 6,
    "the_nothingness_effect/artificial_intelligence/soinets/source_contracts.py": 14,
    "the_nothingness_effect/fluctuation_and_elastic_dynamics/dynamic_fluctuation_index/extended_contracts.py": 3,
    "the_nothingness_effect/foundational_architecture/symmetry/canonical_contracts.py": 5,
    "the_nothingness_effect/foundational_architecture/spatiality/canonical_contracts.py": 5,
    "the_nothingness_effect/foundational_architecture/countable_infinity/canonical_contracts.py": 6,
    "the_nothingness_effect/foundational_architecture/uncountable_infinity/canonical_contracts.py": 17,
    "the_nothingness_effect/foundational_architecture/observation_and_collapse/canonical_contracts.py": 16,
    "the_nothingness_effect/foundational_architecture/the_spectrum_of_infinities/canonical_contracts.py": 15,
    "the_nothingness_effect/foundational_architecture/the_spectrum_of_infinities/authoritative_dfi.py": 1,
}
EXPECTED_OVERRIDE_COUNT = sum(EXPECTED_PROMOTION_PATH_COUNTS.values())
EXPECTED_IMPLEMENTED = BASE_IMPLEMENTED + EXPECTED_OVERRIDE_COUNT
EXPECTED_PROXY = 351 - EXPECTED_IMPLEMENTED
EXPECTED_FOUNDATIONAL_IMPLEMENTED = FOUNDATIONAL_BASE_IMPLEMENTED + sum(
    count
    for path, count in EXPECTED_PROMOTION_PATH_COUNTS.items()
    if "/foundational_architecture/" in path
)


def _raw_matrix() -> list[dict[str, str]]:
    with Path("docs/data/theorem_complex_implementation_matrix.csv").open(
        newline="", encoding="utf-8-sig"
    ) as handle:
        return list(csv.DictReader(handle))


def test_authoritative_manifest_exposes_latest_external_bindings():
    assert authoritative_bindings() == EXPECTED


def test_every_managed_runtime_contract_uses_authoritative_digest():
    for contract in all_contracts():
        expected = EXPECTED.get(contract.appendix)
        if expected is not None:
            assert contract.appendix_source_sha256 == expected


def test_foundational_binding_promotes_only_reviewed_complexes():
    statuses = release_statuses()
    rows = [row for row in _raw_matrix() if row["appendix_file"] == FOUNDATIONAL]
    foundational_contracts = [
        contract for contract in all_contracts() if contract.appendix == FOUNDATIONAL
    ]
    assert len(rows) == 79
    assert len(foundational_contracts) == EXPECTED_FOUNDATIONAL_IMPLEMENTED
    assert (
        sum(statuses[row["complex_id"]] == "implemented" for row in rows)
        == EXPECTED_FOUNDATIONAL_IMPLEMENTED
    )
    assert (
        sum(statuses[row["complex_id"]] == "proxy" for row in rows)
        == 79 - EXPECTED_FOUNDATIONAL_IMPLEMENTED
    )


def test_all_promotions_are_named_auditable_and_dependency_closed():
    overrides = implementation_status_overrides()
    effective = bind_inventory_rows(_raw_matrix())
    effective_by_id = {row["complex_id"]: row for row in effective}
    statuses = release_statuses()

    assert len(overrides) == EXPECTED_OVERRIDE_COUNT
    assert (
        Counter(record["evidence_path"] for record in overrides.values())
        == EXPECTED_PROMOTION_PATH_COUNTS
    )
    for identifier, override in overrides.items():
        row = effective_by_id[identifier]
        assert row["recorded_implementation_status"] == "proxy"
        assert row["implementation_status"] == "implemented"
        assert row["implementation_status_binding"] == "manifest_override"
        assert row["implementation_status_override_reason"] == override["reason"]
        assert row["implementation_status_evidence_path"] == override["evidence_path"]
        assert Path(row["implementation_status_evidence_path"]).is_file()
        assert statuses[identifier] == "implemented"

    assert PROMOTED_DFI.issubset(overrides)
    assert (
        sum(row["implementation_status"] == "implemented" for row in effective)
        == EXPECTED_IMPLEMENTED
    )
    assert (
        sum(status == "implemented" for status in statuses.values())
        == EXPECTED_IMPLEMENTED
    )
    assert sum(status == "proxy" for status in statuses.values()) == EXPECTED_PROXY
    assert len(dependency_downgrades()) == 0
    assert statuses["flowpoint_certified_dfi_validation_functional"] == "implemented"
    assert statuses["spatially_localized_dfi_consistency_closure"] == "implemented"


def test_effective_matrix_has_no_authoritative_source_mismatch():
    report = source_binding_report()
    assert report["total_rows"] == 351
    assert report["managed_appendices"] == 4
    assert report["managed_rows"] == 108
    assert report["effective_source_sha_mismatches"] == 0
    assert report["implementation_status_overrides"] == EXPECTED_OVERRIDE_COUNT
    assert len(report["implementation_status_changes"]) == EXPECTED_OVERRIDE_COUNT
    assert not report["effective_mismatches"]


def test_binding_preserves_recorded_digest_for_audit():
    rows = [
        {
            "complex_id": "fixture",
            "appendix_file": "appendix_the_completeness_theorem.tex",
            "appendix_source_sha256": "0" * 64,
            "implementation_status": "proxy",
        }
    ]
    bound = bind_inventory_rows(rows, status_overrides={})
    assert bound[0]["recorded_appendix_source_sha256"] == "0" * 64
    assert (
        bound[0]["appendix_source_sha256"]
        == EXPECTED["appendix_the_completeness_theorem.tex"]
    )
    assert bound[0]["source_binding_status"] == "manifest_override"
    assert bound[0]["recorded_implementation_status"] == "proxy"
    assert bound[0]["implementation_status"] == "proxy"
    assert bound[0]["implementation_status_binding"] == "unchanged"


def test_effective_matrix_export_is_machine_readable(tmp_path: Path):
    output = tmp_path / "effective.csv"
    report_output = tmp_path / "effective.json"
    report = export(output, report_output)
    with output.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    stored_report = json.loads(report_output.read_text(encoding="utf-8"))
    assert len(rows) == 351
    assert report["effective_source_sha_mismatches"] == 0
    assert report["implementation_status_overrides"] == EXPECTED_OVERRIDE_COUNT
    assert stored_report["effective_matrix_output"] == output.as_posix()
    assert (
        sum(row["implementation_status"] == "implemented" for row in rows)
        == EXPECTED_IMPLEMENTED
    )
    assert all(
        row["appendix_source_sha256"] == EXPECTED[row["appendix_file"]]
        for row in rows
        if row["appendix_file"] in EXPECTED
    )


def test_effective_provenance_uses_same_authoritative_bindings(tmp_path: Path):
    output = tmp_path / "effective-provenance.json"
    report_output = tmp_path / "effective-provenance-report.json"
    report = export_provenance(output, report_output)
    payload = json.loads(output.read_text(encoding="utf-8"))
    stored_report = json.loads(report_output.read_text(encoding="utf-8"))
    assert report["effective_source_sha_mismatches"] == 0
    assert stored_report["effective_provenance_output"] == output.as_posix()
    assert payload["manifests"]
    assert len({item["theorem_complex_id"] for item in payload["manifests"]}) == len(
        payload["manifests"]
    )
    assert all(
        item["appendix_source_sha256"] == EXPECTED[item["appendix_filename"]]
        for item in payload["manifests"]
        if item["appendix_filename"] in EXPECTED
    )


def test_provenance_binding_preserves_recorded_digest():
    raw = {
        "manifests": [
            {
                "theorem_complex_id": "fixture",
                "appendix_filename": "appendix_the_completeness_theorem.tex",
                "appendix_source_sha256": "0" * 64,
            }
        ]
    }
    effective = bind_provenance_manifest(raw)
    report = provenance_binding_report()
    item = effective["manifests"][0]
    assert item["recorded_appendix_source_sha256"] == "0" * 64
    assert (
        item["appendix_source_sha256"]
        == EXPECTED["appendix_the_completeness_theorem.tex"]
    )
    assert item["source_binding_status"] == "manifest_override"
    assert report["effective_source_sha_mismatches"] == 0
