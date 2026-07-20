from __future__ import annotations

import json
from pathlib import Path

from tools.export_effective_theorem_matrix import (
    _unresolved_provenance_mismatches,
    export_provenance,
)


COMPLETENESS_ID = "2_adic_criterion_of_theoremhood_and_typed_dual_infinity"
COMPLETENESS_APPENDIX = "appendix_the_completeness_theorem.tex"
RECORDED_SHA = "1a186b3350f16c284b3cb54f7dfb63d6729d98142e9fb8b53c6de4d9ce3d84f3"
AUTHORITATIVE_SHA = "d711e5c4260fb61bff1ef3e7ea3be14ef093370a9ff22607d2a54e74ba8b166b"


def _provenance(path: Path) -> Path:
    path.write_text(
        json.dumps(
            {
                "schema_version": "fixture",
                "manifests": [
                    {
                        "theorem_complex_id": COMPLETENESS_ID,
                        "appendix_filename": COMPLETENESS_APPENDIX,
                        "appendix_source_sha256": RECORDED_SHA,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_export_accepts_only_explicit_byte_verified_provenance_recertification(
    tmp_path: Path,
):
    report = export_provenance(
        tmp_path / "effective.json",
        tmp_path / "binding.json",
        _provenance(tmp_path / "raw.json"),
    )

    effective = json.loads((tmp_path / "effective.json").read_text(encoding="utf-8"))
    item = effective["manifests"][0]
    assert item["recorded_appendix_source_sha256"] == RECORDED_SHA
    assert item["recertified_appendix_source_sha256"] == AUTHORITATIVE_SHA
    assert item["source_binding_status"] == "recertified"
    assert item["source_exactness"] == "exact"

    assert report["raw_source_sha_mismatches"] == 1
    assert report["source_recertifications"] == 1
    assert report["effective_source_sha_mismatches"] == 0
    assert _unresolved_provenance_mismatches(report) == []


def test_unlisted_provenance_mismatch_remains_release_blocking():
    report = {
        "raw_mismatches": [
            {
                "theorem_complex_id": "not_in_recertification_ledger",
                "appendix_file": COMPLETENESS_APPENDIX,
                "authoritative_sha256": AUTHORITATIVE_SHA,
            }
        ]
    }

    assert _unresolved_provenance_mismatches(report) == [
        {
            "theorem_complex_id": "not_in_recertification_ledger",
            "appendix_file": COMPLETENESS_APPENDIX,
            "authoritative_sha256": AUTHORITATIVE_SHA,
        }
    ]
