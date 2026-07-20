from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.enforce_authoritative_archive_gate import (
    ArchiveGateError,
    enforce,
    validation_errors,
)


ARCHIVE_SHA = "3" * 64
ENVELOPE_SHA = "a" * 64


def _passing_evidence() -> dict[str, object]:
    return {
        "schema_version": "1.1",
        "expected_archive_sha256": ARCHIVE_SHA,
        "actual_archive_sha256": ARCHIVE_SHA,
        "archive_sha256_match": True,
        "expected_envelope_sha256": ENVELOPE_SHA,
        "actual_envelope_sha256": ENVELOPE_SHA,
        "envelope_sha256_match": True,
        "expected_member_count": 10,
        "actual_member_count": 10,
        "member_set_exact": True,
        "zip_crc_passed": True,
        "canonical_input_order_passed": True,
        "matrix_rows": 351,
        "member_hash_mismatches": [],
        "missing_equation_labels": [],
        "missing_first_labels": [],
        "errors": [],
        "plaintext_cleanup_attempted": True,
        "plaintext_cleanup_method": "shred-u",
        "plaintext_cleanup_passed": True,
        "passed": True,
    }


def test_complete_archive_evidence_passes(tmp_path: Path):
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(_passing_evidence()), encoding="utf-8")
    plaintext_path = tmp_path / "deleted.zip"

    result = enforce(evidence_path, plaintext_path=plaintext_path)

    assert result["actual_member_count"] == 10
    assert result["plaintext_cleanup_method"] == "shred-u"


def test_envelope_hash_mismatch_fails_closed():
    evidence = _passing_evidence()
    evidence["actual_envelope_sha256"] = "b" * 64
    evidence["envelope_sha256_match"] = False

    failures = validation_errors(evidence)

    assert "envelope_sha256_mismatch" in failures
    assert "envelope_sha256_match_not_true" in failures


def test_member_or_crc_failure_is_rejected():
    evidence = _passing_evidence()
    evidence["actual_member_count"] = 9
    evidence["zip_crc_passed"] = False
    evidence["member_hash_mismatches"] = ["member.tex"]

    failures = validation_errors(evidence)

    assert "actual_member_count_not_10" in failures
    assert "zip_crc_not_verified" in failures
    assert "member_hash_mismatches_not_empty" in failures


def test_nonsecure_cleanup_method_is_rejected():
    evidence = _passing_evidence()
    evidence["plaintext_cleanup_method"] = "rm-f"

    assert "plaintext_cleanup_method_not_shred_u" in validation_errors(evidence)


def test_existing_plaintext_archive_is_rejected(tmp_path: Path):
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(_passing_evidence()), encoding="utf-8")
    plaintext_path = tmp_path / "authority.zip"
    plaintext_path.write_bytes(b"PK\x03\x04plaintext")

    with pytest.raises(ArchiveGateError, match="plaintext_archive_still_exists"):
        enforce(evidence_path, plaintext_path=plaintext_path)


def test_missing_or_invalid_evidence_fails_closed(tmp_path: Path):
    with pytest.raises(ArchiveGateError, match="not found"):
        enforce(tmp_path / "missing.json")

    invalid = tmp_path / "invalid.json"
    invalid.write_text("[]", encoding="utf-8")
    with pytest.raises(ArchiveGateError, match="JSON object"):
        enforce(invalid)
