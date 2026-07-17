from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.build_immutable_release_qa import build


RESULT_COMMIT = "b" * 40


def _write(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _arguments(
    tmp_path: Path,
    *,
    archive_passed: bool = True,
    evidence_commit: str = RESULT_COMMIT,
) -> argparse.Namespace:
    final_qa = _write(
        tmp_path / "final.json",
        {
            "final_qa_passed": True,
            "release_blockers": [],
            "theorem_inventory": {"total": 1},
            "repository_result_commit": evidence_commit,
        },
    )
    archive_qa = _write(
        tmp_path / "archive.json",
        {
            "passed": archive_passed,
            "actual_archive_sha256": "a" * 64 if archive_passed else None,
            "expected_archive_sha256": "a" * 64,
        },
    )
    status = _write(
        tmp_path / "status.json",
        {
            "rows": 1,
            "dimensions": {
                "runtime_status": {"implemented": 1},
                "source_exactness": {"exact": 1},
                "closure_status": {"open": 1},
                "validation_status": {"synthetic": 1},
            },
            "open_and_numerical_candidate_preserved": 1,
        },
    )
    matrix = _write(tmp_path / "matrix.json", {"summary": {"rows": 1}})
    provenance = _write(
        tmp_path / "provenance.json",
        {
            "repository_result_commit": evidence_commit,
            "manifests": [{"theorem_complex_id": "fixture"}],
        },
    )
    archive_manifest = _write(tmp_path / "archive_manifest.json", {"fixture": True})
    recertification = _write(tmp_path / "recertification.json", {"fixture": True})
    return argparse.Namespace(
        final_qa=final_qa,
        archive_qa=archive_qa,
        status_dimensions=status,
        matrix_report=matrix,
        provenance=provenance,
        archive_manifest=archive_manifest,
        recertification_manifest=recertification,
        result_commit=RESULT_COMMIT,
        branch="fixture",
        ci_conclusion="success",
        ci_run_id="1",
        output=tmp_path / "immutable.json",
        check=True,
    )


def test_immutable_release_qa_preserves_open_as_independent_dimension(tmp_path: Path):
    payload = build(_arguments(tmp_path))
    assert payload["immutable_release_qa_passed"] is True
    assert payload["release_blockers"] == []
    assert payload["repository_final_qa_commit"] == RESULT_COMMIT
    assert payload["artifact_provenance_commit"] == RESULT_COMMIT
    assert payload["release_status_dimensions"][
        "open_and_numerical_candidate_preserved"
    ] == 1


def test_immutable_release_qa_fails_when_archive_bytes_are_unverified(tmp_path: Path):
    payload = build(_arguments(tmp_path, archive_passed=False))
    assert payload["immutable_release_qa_passed"] is False
    assert "authoritative_archive_byte_verification_failed" in payload[
        "release_blockers"
    ]
    assert "authoritative_archive_sha256_mismatch" in payload["release_blockers"]


def test_immutable_release_qa_rejects_evidence_from_another_commit(tmp_path: Path):
    payload = build(_arguments(tmp_path, evidence_commit="c" * 40))
    assert payload["immutable_release_qa_passed"] is False
    assert "repository_final_qa_commit_mismatch" in payload["release_blockers"]
    assert "artifact_provenance_commit_mismatch" in payload["release_blockers"]
