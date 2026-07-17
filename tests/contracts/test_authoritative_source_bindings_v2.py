from __future__ import annotations

import csv
import json
from pathlib import Path

from the_nothingness_effect._runtime.theorem_complex_runtime.authority import authoritative_bindings, bind_inventory_rows, implementation_status_overrides, source_binding_report
from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import all_contracts, dependency_downgrades, release_statuses

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_MANIFEST = ROOT / "docs/data/authoritative_archive_manifest.json"
MATRIX = ROOT / "docs/data/theorem_complex_implementation_matrix.csv"
RECERTIFICATION = ROOT / "docs/data/source_recertification/authoritative_recertification_101.json"


def _rows():
    with MATRIX.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def test_bindings_are_derived_from_archive_member_manifest():
    manifest = json.loads(ARCHIVE_MANIFEST.read_text(encoding="utf-8"))
    expected = {filename: record["sha256"] for filename, record in manifest["members"].items() if record["role"] == "theorem_runtime"}
    assert authoritative_bindings() == expected
    assert len(expected) == 7


def test_binding_is_observational_and_never_overwrites_bad_digest():
    rows = [{"complex_id":"fixture","appendix_file":"appendix_the_completeness_theorem.tex","appendix_source_sha256":"0" * 64,"implementation_status":"proxy"}]
    bound = bind_inventory_rows(rows, status_overrides={})
    assert bound[0]["appendix_source_sha256"] == "0" * 64
    assert bound[0]["recorded_appendix_source_sha256"] == "0" * 64
    assert bound[0]["source_binding_status"] == "mismatch"
    assert bound[0]["source_exactness"] == "stale"


def test_101_historical_drift_rows_are_explicitly_recertified():
    report = source_binding_report()
    assert report["total_rows"] == 351
    assert report["managed_appendices"] == 7
    assert report["managed_rows"] == 351
    assert report["raw_source_sha_mismatches"] == 101
    assert report["effective_source_sha_mismatches"] == 0
    assert report["source_binding_overrides"] == 0
    assert report["source_recertifications"] == 101

    payload = json.loads(RECERTIFICATION.read_text(encoding="utf-8"))
    assert payload["total_complexes"] == 101
    assert {filename: record["complex_count"] for filename, record in payload["appendices"].items()} == {
        "appendix_tne_mathematical_closure_architecture.tex": 7,
        "appendix_tne_foundational_closure_architecture.tex": 79,
        "appendix_the_completeness_theorem.tex": 15,
    }
    identifiers = [identifier for record in payload["appendices"].values() for identifier in record["complex_ids"]]
    assert len(identifiers) == len(set(identifiers)) == 101


def test_contract_catalog_is_source_exact_and_dependency_closed():
    bindings = authoritative_bindings()
    contracts = all_contracts()
    assert len(contracts) == 351
    assert all(contract.appendix_source_sha256 == bindings[contract.appendix] for contract in contracts)
    statuses = release_statuses()
    assert sum(status == "implemented" for status in statuses.values()) == 351
    assert dependency_downgrades() == ()


def test_promotions_remain_named_and_auditable():
    overrides = implementation_status_overrides()
    rows = bind_inventory_rows(_rows())
    assert len(overrides) == 156
    assert sum(row["implementation_status"] == "implemented" for row in rows) == 351
    assert all((ROOT / row["implementation_status_evidence_path"]).is_file() for row in rows if row["implementation_status_binding"] == "reviewed_override")
