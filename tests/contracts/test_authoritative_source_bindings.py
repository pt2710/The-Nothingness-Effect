"""Fail-closed gates for externally maintained authoritative appendix bindings."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from the_nothingness_effect._runtime.theorem_complex_runtime.authority import (
    authoritative_bindings,
    bind_inventory_rows,
    bind_provenance_manifest,
    provenance_binding_report,
    source_binding_report,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import all_contracts
from tools.export_effective_theorem_matrix import export, export_provenance


EXPECTED = {
    "appendix_canonical_self_negating_involution_flowpoint.tex": (
        "5c44d82b34cd4c5d05d01253a62987f2f6099d582bf954a4cbdbc13b52b52206"
    ),
    "appendix_tne_mathematical_closure_architecture.tex": (
        "3cd520d5b025f6f241c7eb09417528276f0c6904e07aa088057c7b57803bf011"
    ),
    "appendix_tne_foundational_closure_architecture.tex": (
        "5e459eed3eca36d1342bc879fc8ac3962f3c801bfd1aab733f3db081a7ed0c69"
    ),
    "appendix_the_completeness_theorem.tex": (
        "1a186b3350f16c284b3cb54f7dfb63d6729d98142e9fb8b53c6de4d9ce3d84f3"
    ),
}


def test_authoritative_manifest_exposes_latest_external_bindings():
    assert authoritative_bindings() == EXPECTED


def test_every_managed_runtime_contract_uses_authoritative_digest():
    for contract in all_contracts():
        expected = EXPECTED.get(contract.appendix)
        if expected is not None:
            assert contract.appendix_source_sha256 == expected


def test_effective_matrix_has_no_authoritative_source_mismatch():
    report = source_binding_report()

    assert report["total_rows"] == 351
    assert report["managed_appendices"] == 4
    assert report["managed_rows"] == 108
    assert report["effective_source_sha_mismatches"] == 0
    assert not report["effective_mismatches"]


def test_binding_preserves_recorded_digest_for_audit():
    rows = [
        {
            "complex_id": "fixture",
            "appendix_file": "appendix_the_completeness_theorem.tex",
            "appendix_source_sha256": "0" * 64,
        }
    ]

    bound = bind_inventory_rows(rows)

    assert bound[0]["recorded_appendix_source_sha256"] == "0" * 64
    assert bound[0]["appendix_source_sha256"] == EXPECTED[
        "appendix_the_completeness_theorem.tex"
    ]
    assert bound[0]["source_binding_status"] == "manifest_override"


def test_effective_matrix_export_is_machine_readable(tmp_path: Path):
    output = tmp_path / "effective.csv"
    report_output = tmp_path / "effective.json"

    report = export(output, report_output)

    with output.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    stored_report = json.loads(report_output.read_text(encoding="utf-8"))
    assert len(rows) == 351
    assert report["effective_source_sha_mismatches"] == 0
    assert stored_report["effective_matrix_output"] == output.as_posix()
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
    assert item["appendix_source_sha256"] == EXPECTED[
        "appendix_the_completeness_theorem.tex"
    ]
    assert item["source_binding_status"] == "manifest_override"
    assert report["effective_source_sha_mismatches"] == 0
