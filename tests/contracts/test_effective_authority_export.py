from __future__ import annotations

import json
from pathlib import Path

from tools.export_effective_theorem_matrix import (
    _unresolved_provenance_mismatches,
    export,
    export_provenance,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.authority import (
    authoritative_bindings,
)


def test_effective_matrix_export_is_release_clean(tmp_path: Path):
    matrix_report = export(
        tmp_path / "effective_matrix.csv",
        tmp_path / "effective_matrix.json",
    )
    assert sum(
        int(record["rows"])
        for record in matrix_report["appendix_counts"].values()
    ) == 351
    assert matrix_report["source_binding_overrides"] == 0
    assert matrix_report["effective_source_mismatch_count"] == 0
    assert matrix_report["implementation_status_change_count"] == 156
    assert (tmp_path / "effective_matrix.csv").is_file()
    assert (tmp_path / "effective_matrix.json").is_file()


def test_explicit_fresh_provenance_export_is_release_clean(tmp_path: Path):
    appendix, digest = next(iter(authoritative_bindings().items()))
    source = tmp_path / "fresh_provenance.json"
    source.write_text(
        json.dumps(
            {
                "repository_result_commit": "b" * 40,
                "manifests": [
                    {
                        "theorem_complex_id": "fixture",
                        "appendix_filename": appendix,
                        "appendix_source_sha256": digest,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    provenance_report = export_provenance(
        tmp_path / "effective_provenance.json",
        tmp_path / "effective_provenance_binding.json",
        source,
    )
    assert provenance_report["total_manifests"] == 1
    assert provenance_report["source_binding_overrides"] == 0
    assert provenance_report["effective_source_sha_mismatches"] == 0
    assert _unresolved_provenance_mismatches(provenance_report) == []
    assert (tmp_path / "effective_provenance.json").is_file()
    assert (tmp_path / "effective_provenance_binding.json").is_file()
