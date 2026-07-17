from __future__ import annotations

from pathlib import Path

from tools.export_effective_theorem_matrix import (
    _unresolved_provenance_mismatches,
    export,
    export_provenance,
)


def test_effective_matrix_and_provenance_export_are_release_clean(tmp_path: Path):
    matrix_report = export(
        tmp_path / "effective_matrix.csv",
        tmp_path / "effective_matrix.json",
    )
    provenance_report = export_provenance(
        tmp_path / "effective_provenance.json",
        tmp_path / "effective_provenance_binding.json",
    )

    assert sum(
        int(record["rows"])
        for record in matrix_report["appendix_counts"].values()
    ) == 351
    assert matrix_report["source_binding_overrides"] == 0
    assert matrix_report["effective_source_mismatch_count"] == 0
    assert matrix_report["implementation_status_change_count"] == 156

    assert provenance_report["total_manifests"] == 351
    assert provenance_report["source_binding_overrides"] == 0
    assert provenance_report["effective_source_sha_mismatches"] == 0
    assert _unresolved_provenance_mismatches(provenance_report) == []

    assert (tmp_path / "effective_matrix.csv").is_file()
    assert (tmp_path / "effective_matrix.json").is_file()
    assert (tmp_path / "effective_provenance.json").is_file()
    assert (tmp_path / "effective_provenance_binding.json").is_file()
