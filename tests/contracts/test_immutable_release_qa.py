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
    artifact_passed: bool = True,
    ledger_complete: bool = True,
    open_count: int = 0,
    robustness_seeds: tuple[int, ...] = (0, 1, 2),
    convergence_records: int = 69,
    alignment_rows: int = 1,
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
                "closure_status": {"closed": 1},
                "validation_status": {"synthetic": 1},
                "artifact_status": {"complete_core_bundle": 1},
            },
            "open_and_numerical_candidate_preserved": open_count,
            "artifact_core_bundle_gaps": 0,
        },
    )
    matrix = _write(tmp_path / "matrix.json", {"summary": {"rows": 1}})
    provenance = _write(
        tmp_path / "provenance.json",
        {"repository_result_commit": evidence_commit, "manifests": [{"theorem_complex_id": "fixture"}]},
    )
    artifact_coverage = _write(
        tmp_path / "artifact_coverage.json",
        {
            "theorem_complexes": 1,
            "complete_core_artifact_bundles": 1 if artifact_passed else 0,
            "diagnostic_bundles_enriched": 1,
            "passed": artifact_passed,
        },
    )
    ledger_count = open_count if ledger_complete else open_count + 1
    closure_obligations = _write(
        tmp_path / "closure_obligations.json",
        {
            "open_or_numerical_candidate_count": ledger_count,
            "counts": {"open": ledger_count} if ledger_count else {},
            "all_open_states_represented": ledger_complete,
        },
    )
    formal_proof_coverage = _write(
        tmp_path / "formal_proof_coverage.json",
        {
            "rows": 1,
            "counts": {"not_formally_proved": 1},
            "all_rows_classified": True,
            "invalid_proof_claims": 0,
            "verified_formal_proofs": 0,
            "policy": "tests are not proof certificates",
        },
    )
    robustness = _write(
        tmp_path / "robustness.json",
        {
            "seeds": list(robustness_seeds),
            "epochs": 3,
            "scenarios": ["clean", "remove_color", "remove_sound", "remove_vision"],
            "records": len(robustness_seeds) * 4,
            "all_metrics_finite": True,
            "claim_boundary": "synthetic multi-seed robustness evidence",
        },
    )
    convergence = _write(
        tmp_path / "convergence.json",
        {
            "families": ["elastic_dubler", "locality_driven_gravity", "black_hole_dynamics", "elastic_pi_ripples"],
            "resolutions": [9, 17, 33],
            "records": convergence_records,
            "all_metrics_finite": True,
            "claim_boundary": "finite grid-refinement diagnostic; not continuum convergence proof",
        },
    )
    equation_alignment = _write(
        tmp_path / "equation_alignment.json",
        {
            "rows": alignment_rows,
            "complete_mappings": alignment_rows,
            "source_faithful_corrections": 23,
            "first_labels": alignment_rows,
            "equation_labels": max(2, alignment_rows),
            "errors": [],
            "passed": alignment_rows == 1,
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
        artifact_coverage=artifact_coverage,
        closure_obligations=closure_obligations,
        formal_proof_coverage=formal_proof_coverage,
        multimodal_robustness=robustness,
        source_faithful_convergence=convergence,
        equation_implementation_alignment=equation_alignment,
        archive_manifest=archive_manifest,
        recertification_manifest=recertification,
        result_commit=RESULT_COMMIT,
        branch="fixture",
        ci_conclusion="success",
        ci_run_id="1",
        output=tmp_path / "immutable.json",
        check=True,
    )


def test_immutable_release_qa_requires_complete_mathematical_closure(tmp_path: Path):
    payload = build(_arguments(tmp_path))
    assert payload["immutable_release_qa_passed"] is True
    assert payload["release_blockers"] == []
    assert payload["repository_final_qa_commit"] == RESULT_COMMIT
    assert payload["artifact_provenance_commit"] == RESULT_COMMIT
    assert payload["release_status_dimensions"]["open_and_numerical_candidate_preserved"] == 0
    assert payload["theorem_artifact_coverage"]["complete_core_artifact_bundles"] == 1
    assert payload["closure_obligation_ledger"]["all_open_states_represented"] is True
    assert payload["multimodal_robustness"]["seeds"] == [0, 1, 2]
    assert payload["source_faithful_convergence"]["records"] == 69
    assert payload["equation_implementation_alignment"]["complete_mappings"] == 1
    assert payload["formal_proof_coverage"]["verified_formal_proofs"] == 0


def test_immutable_release_qa_rejects_remaining_open_state(tmp_path: Path):
    payload = build(_arguments(tmp_path, open_count=1))
    assert payload["immutable_release_qa_passed"] is False
    assert "mathematical_closure_incomplete" in payload["release_blockers"]


def test_immutable_release_qa_fails_when_archive_bytes_are_unverified(tmp_path: Path):
    payload = build(_arguments(tmp_path, archive_passed=False))
    assert payload["immutable_release_qa_passed"] is False
    assert "authoritative_archive_byte_verification_failed" in payload["release_blockers"]
    assert "authoritative_archive_sha256_mismatch" in payload["release_blockers"]


def test_immutable_release_qa_rejects_evidence_from_another_commit(tmp_path: Path):
    payload = build(_arguments(tmp_path, evidence_commit="c" * 40))
    assert payload["immutable_release_qa_passed"] is False
    assert "repository_final_qa_commit_mismatch" in payload["release_blockers"]
    assert "artifact_provenance_commit_mismatch" in payload["release_blockers"]


def test_immutable_release_qa_rejects_incomplete_artifact_coverage(tmp_path: Path):
    payload = build(_arguments(tmp_path, artifact_passed=False))
    assert payload["immutable_release_qa_passed"] is False
    assert "theorem_artifact_coverage_failed" in payload["release_blockers"]
    assert "theorem_artifact_coverage_incomplete" in payload["release_blockers"]


def test_immutable_release_qa_rejects_missing_open_obligation(tmp_path: Path):
    payload = build(_arguments(tmp_path, ledger_complete=False))
    assert payload["immutable_release_qa_passed"] is False
    assert "closure_obligation_ledger_incomplete" in payload["release_blockers"]
    assert "closure_obligation_count_mismatch" in payload["release_blockers"]


def test_immutable_release_qa_requires_three_robustness_seeds(tmp_path: Path):
    payload = build(_arguments(tmp_path, robustness_seeds=(0, 1)))
    assert payload["immutable_release_qa_passed"] is False
    assert "multimodal_multiseed_coverage_incomplete" in payload["release_blockers"]


def test_immutable_release_qa_requires_all_69_convergence_records(tmp_path: Path):
    payload = build(_arguments(tmp_path, convergence_records=68))
    assert payload["immutable_release_qa_passed"] is False
    assert "source_faithful_convergence_record_mismatch" in payload["release_blockers"]


def test_immutable_release_qa_requires_complete_equation_alignment(tmp_path: Path):
    payload = build(_arguments(tmp_path, alignment_rows=0))
    assert payload["immutable_release_qa_passed"] is False
    assert "equation_implementation_row_mismatch" in payload["release_blockers"]
    assert "equation_implementation_mapping_incomplete" in payload["release_blockers"]
