"""Fail-closed enforcement for private authoritative archive evidence.

The verifier produces byte-level ZIP/member evidence.  The workflow augments
that evidence with the tracked ciphertext-envelope SHA-256 and with proof that
the decrypted ZIP was securely removed from runner temporary storage.  This
module accepts the gate only when every independent condition is present and
true.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


EXPECTED_MEMBER_COUNT = 10
EXPECTED_MATRIX_ROWS = 351


class ArchiveGateError(RuntimeError):
    """Raised when archive evidence cannot be parsed or enforced."""


def load_evidence(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ArchiveGateError(f"archive evidence not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ArchiveGateError(f"archive evidence is not valid JSON: {path}") from error
    if not isinstance(payload, dict):
        raise ArchiveGateError("archive evidence root must be a JSON object")
    return payload


def _empty_sequence(value: object) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and len(value) == 0


def validation_errors(
    evidence: Mapping[str, Any],
    *,
    plaintext_path: Path | None = None,
) -> list[str]:
    failures: list[str] = []

    expected_archive = evidence.get("expected_archive_sha256")
    actual_archive = evidence.get("actual_archive_sha256")
    if not isinstance(expected_archive, str) or len(expected_archive) != 64:
        failures.append("expected_archive_sha256_missing_or_invalid")
    if not isinstance(actual_archive, str) or len(actual_archive) != 64:
        failures.append("actual_archive_sha256_missing_or_invalid")
    if expected_archive != actual_archive:
        failures.append("archive_sha256_mismatch")
    if evidence.get("archive_sha256_match") is not True:
        failures.append("archive_sha256_match_not_true")

    expected_envelope = evidence.get("expected_envelope_sha256")
    actual_envelope = evidence.get("actual_envelope_sha256")
    if not isinstance(expected_envelope, str) or len(expected_envelope) != 64:
        failures.append("expected_envelope_sha256_missing_or_invalid")
    if not isinstance(actual_envelope, str) or len(actual_envelope) != 64:
        failures.append("actual_envelope_sha256_missing_or_invalid")
    if expected_envelope != actual_envelope:
        failures.append("envelope_sha256_mismatch")
    if evidence.get("envelope_sha256_match") is not True:
        failures.append("envelope_sha256_match_not_true")

    if evidence.get("expected_member_count") != EXPECTED_MEMBER_COUNT:
        failures.append("expected_member_count_not_10")
    if evidence.get("actual_member_count") != EXPECTED_MEMBER_COUNT:
        failures.append("actual_member_count_not_10")
    if evidence.get("member_set_exact") is not True:
        failures.append("member_set_not_exact")
    if evidence.get("zip_crc_passed") is not True:
        failures.append("zip_crc_not_verified")
    if evidence.get("canonical_input_order_passed") is not True:
        failures.append("canonical_input_order_not_verified")
    if evidence.get("matrix_rows") != EXPECTED_MATRIX_ROWS:
        failures.append("matrix_row_count_not_351")

    for key in (
        "member_hash_mismatches",
        "missing_equation_labels",
        "missing_first_labels",
        "errors",
    ):
        if not _empty_sequence(evidence.get(key)):
            failures.append(f"{key}_not_empty")

    cleanup_method = evidence.get("plaintext_cleanup_method")
    if evidence.get("plaintext_cleanup_attempted") is not True:
        failures.append("plaintext_cleanup_not_attempted")
    if cleanup_method != "shred-u":
        failures.append("plaintext_cleanup_method_not_shred_u")
    if evidence.get("plaintext_cleanup_passed") is not True:
        failures.append("plaintext_cleanup_not_verified")
    if plaintext_path is not None and plaintext_path.exists():
        failures.append("plaintext_archive_still_exists")

    if evidence.get("passed") is not True:
        failures.append("aggregate_evidence_not_passed")

    return failures


def enforce(
    evidence_path: Path,
    *,
    plaintext_path: Path | None = None,
) -> dict[str, Any]:
    evidence = load_evidence(evidence_path)
    failures = validation_errors(evidence, plaintext_path=plaintext_path)
    if failures:
        raise ArchiveGateError(
            "authoritative archive gate failed: " + ", ".join(sorted(set(failures)))
        )
    return evidence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--plaintext-path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        evidence = enforce(args.evidence, plaintext_path=args.plaintext_path)
    except ArchiveGateError as error:
        print(str(error))
        return 1
    print(
        json.dumps(
            {
                "passed": True,
                "actual_envelope_sha256": evidence["actual_envelope_sha256"],
                "actual_archive_sha256": evidence["actual_archive_sha256"],
                "actual_member_count": evidence["actual_member_count"],
                "plaintext_cleanup_method": evidence["plaintext_cleanup_method"],
                "plaintext_cleanup_passed": evidence["plaintext_cleanup_passed"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
