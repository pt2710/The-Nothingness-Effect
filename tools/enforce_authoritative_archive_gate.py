"""Fail-closed enforcement of private authoritative archive evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

EXPECTED_MEMBER_COUNT = 10
EXPECTED_MATRIX_ROWS = 351


class ArchiveGateError(RuntimeError):
    pass


def _object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ArchiveGateError(f"{label} not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ArchiveGateError(f"{label} is not valid JSON: {path}") from error
    if not isinstance(value, dict):
        raise ArchiveGateError(f"{label} root must be a JSON object")
    return value


def load_evidence(path: Path) -> dict[str, Any]:
    return _object(path, "archive evidence")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except FileNotFoundError as error:
        raise ArchiveGateError(f"encrypted envelope not found: {path}") from error
    return digest.hexdigest()


def _empty(value: object) -> bool:
    return (
        isinstance(value, Sequence)
        and not isinstance(value, (str, bytes))
        and len(value) == 0
    )


def enrich_runtime_evidence(
    evidence: Mapping[str, Any],
    *,
    repository_root: Path = Path("."),
    plaintext_path: Path | None = None,
) -> dict[str, Any]:
    result = dict(evidence)
    manifest = _object(
        repository_root / "docs/data/authoritative_archive_manifest.json",
        "authority manifest",
    )
    relative = manifest.get("encrypted_envelope_path")
    expected = manifest.get("encrypted_envelope_sha256")
    if not isinstance(relative, str) or not relative:
        raise ArchiveGateError("authority manifest lacks encrypted_envelope_path")
    if not isinstance(expected, str) or len(expected) != 64:
        raise ArchiveGateError("authority manifest lacks encrypted_envelope_sha256")
    actual = _sha256(repository_root / relative)
    workflow = (
        repository_root / ".github/workflows/ci.yml"
    ).read_text(encoding="utf-8")
    target = plaintext_path or Path(
        os.environ.get("RUNNER_TEMP", ".")
    ) / "TNE_Authoritative_Appendices.zip"
    shred_declared = 'shred -u "${archive}"' in workflow
    cleanup_passed = not target.exists()
    result.update(
        {
            "expected_envelope_sha256": expected,
            "actual_envelope_sha256": actual,
            "envelope_sha256_match": actual == expected,
            "plaintext_cleanup_attempted": bool(result.get("passed")) and shred_declared,
            "plaintext_cleanup_method": "shred-u" if shred_declared else "undeclared",
            "plaintext_cleanup_passed": cleanup_passed,
            "plaintext_cleanup_path": str(target),
        }
    )
    result["passed"] = bool(result.get("passed")) and all(
        (
            result["envelope_sha256_match"],
            result["plaintext_cleanup_attempted"],
            result["plaintext_cleanup_passed"],
        )
    )
    return result


def validation_errors(
    evidence: Mapping[str, Any],
    *,
    plaintext_path: Path | None = None,
) -> list[str]:
    failures: list[str] = []
    expected_archive = evidence.get("expected_archive_sha256")
    actual_archive = evidence.get("actual_archive_sha256")
    expected_envelope = evidence.get("expected_envelope_sha256")
    actual_envelope = evidence.get("actual_envelope_sha256")
    checks = {
        "archive_sha256_mismatch": expected_archive != actual_archive,
        "archive_sha256_match_not_true": evidence.get("archive_sha256_match") is not True,
        "envelope_sha256_mismatch": expected_envelope != actual_envelope,
        "envelope_sha256_match_not_true": evidence.get("envelope_sha256_match") is not True,
        "expected_member_count_not_10": evidence.get("expected_member_count") != 10,
        "actual_member_count_not_10": evidence.get("actual_member_count") != 10,
        "member_set_not_exact": evidence.get("member_set_exact") is not True,
        "zip_crc_not_verified": evidence.get("zip_crc_passed") is not True,
        "canonical_input_order_not_verified": evidence.get("canonical_input_order_passed") is not True,
        "matrix_row_count_not_351": evidence.get("matrix_rows") != 351,
        "plaintext_cleanup_not_attempted": evidence.get("plaintext_cleanup_attempted") is not True,
        "plaintext_cleanup_method_not_shred_u": evidence.get("plaintext_cleanup_method") != "shred-u",
        "plaintext_cleanup_not_verified": evidence.get("plaintext_cleanup_passed") is not True,
        "aggregate_evidence_not_passed": evidence.get("passed") is not True,
    }
    failures.extend(name for name, failed in checks.items() if failed)
    if not isinstance(expected_archive, str) or len(expected_archive) != 64:
        failures.append("expected_archive_sha256_missing_or_invalid")
    if not isinstance(actual_archive, str) or len(actual_archive) != 64:
        failures.append("actual_archive_sha256_missing_or_invalid")
    if not isinstance(expected_envelope, str) or len(expected_envelope) != 64:
        failures.append("expected_envelope_sha256_missing_or_invalid")
    if not isinstance(actual_envelope, str) or len(actual_envelope) != 64:
        failures.append("actual_envelope_sha256_missing_or_invalid")
    for key in (
        "member_hash_mismatches",
        "missing_equation_labels",
        "missing_first_labels",
        "errors",
    ):
        if not _empty(evidence.get(key)):
            failures.append(f"{key}_not_empty")
    if plaintext_path is not None and plaintext_path.exists():
        failures.append("plaintext_archive_still_exists")
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
            "authoritative archive gate failed: "
            + ", ".join(sorted(set(failures)))
        )
    return evidence


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--plaintext-path", type=Path)
    args = parser.parse_args(argv)
    target = args.plaintext_path or Path(
        os.environ.get("RUNNER_TEMP", ".")
    ) / "TNE_Authoritative_Appendices.zip"
    try:
        evidence = enrich_runtime_evidence(
            load_evidence(args.evidence),
            plaintext_path=target,
        )
        args.evidence.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        failures = validation_errors(evidence, plaintext_path=target)
        if failures:
            raise ArchiveGateError(
                "authoritative archive gate failed: "
                + ", ".join(sorted(set(failures)))
            )
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
