"""Verify the authoritative TNE appendix ZIP from its actual bytes.

This verifier is intentionally independent of runtime SHA binding. It opens the
archive, validates the archive and member digests, exercises ZIP CRC checks,
checks canonical input order, and resolves every theorem-inventory label against
the extracted member bytes without writing authoritative ``.tex`` files to the
repository checkout.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
from typing import Any
import zipfile


DEFAULT_MANIFEST = Path("docs/data/authoritative_archive_manifest.json")
DEFAULT_MATRIX = Path("docs/data/theorem_complex_implementation_matrix.csv")
DEFAULT_OUTPUT = Path("reports/authoritative_archive_byte_verification.json")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def _matrix_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _input_order(text: str) -> list[str]:
    arguments = re.findall(r"\\(?:input|include)\s*\{([^}]+)\}", text)
    normalized: list[str] = []
    for argument in arguments:
        name = Path(argument.strip()).name
        normalized.append(name if name.endswith(".tex") else f"{name}.tex")
    return normalized


def verify(
    archive_path: Path,
    *,
    manifest_path: Path = DEFAULT_MANIFEST,
    matrix_path: Path = DEFAULT_MATRIX,
) -> dict[str, Any]:
    manifest = _read_json(manifest_path)
    expected_members = manifest.get("members")
    if not isinstance(expected_members, dict) or not expected_members:
        raise ValueError("authoritative archive manifest has no member map")

    result: dict[str, Any] = {
        "schema_version": "1.0",
        "archive_file": archive_path.name,
        "manifest_file": manifest_path.as_posix(),
        "matrix_file": matrix_path.as_posix(),
        "expected_archive_sha256": str(manifest.get("archive_sha256", "")),
        "actual_archive_sha256": None,
        "archive_sha256_match": False,
        "zip_crc_passed": False,
        "expected_member_count": len(expected_members),
        "actual_member_count": 0,
        "member_set_exact": False,
        "member_hash_mismatches": [],
        "canonical_input_order_passed": False,
        "canonical_input_order_observed": [],
        "matrix_rows": 0,
        "verified_first_labels": 0,
        "verified_equation_labels": 0,
        "missing_first_labels": [],
        "missing_equation_labels": [],
        "archive_roles_verified": {},
        "errors": [],
        "passed": False,
    }

    if not archive_path.is_file():
        result["errors"].append("authoritative_archive_bytes_unavailable")
        return result

    archive_bytes = archive_path.read_bytes()
    actual_archive_sha = _sha256(archive_bytes)
    result["actual_archive_sha256"] = actual_archive_sha
    result["archive_sha256_match"] = (
        actual_archive_sha == result["expected_archive_sha256"]
    )
    if not result["archive_sha256_match"]:
        result["errors"].append("archive_sha256_mismatch")

    try:
        with zipfile.ZipFile(archive_path) as archive:
            names = [item.filename for item in archive.infolist() if not item.is_dir()]
            result["actual_member_count"] = len(names)
            expected_names = set(expected_members)
            actual_names = set(names)
            result["member_set_exact"] = (
                len(names) == len(actual_names) and actual_names == expected_names
            )
            if not result["member_set_exact"]:
                result["errors"].append("archive_member_set_mismatch")
                result["missing_members"] = sorted(expected_names - actual_names)
                result["unexpected_members"] = sorted(actual_names - expected_names)
                result["duplicate_members"] = sorted(
                    name for name in actual_names if names.count(name) > 1
                )

            bad_crc_member = archive.testzip()
            result["zip_crc_passed"] = bad_crc_member is None
            if bad_crc_member is not None:
                result["errors"].append(f"zip_crc_failure:{bad_crc_member}")

            member_bytes: dict[str, bytes] = {}
            role_counts: dict[str, int] = {}
            for name, record in expected_members.items():
                role = str(record.get("role", "unclassified"))
                role_counts[role] = role_counts.get(role, 0) + 1
                if name not in actual_names:
                    continue
                data = archive.read(name)
                member_bytes[name] = data
                actual_sha = _sha256(data)
                expected_sha = str(record.get("sha256", ""))
                if actual_sha != expected_sha:
                    result["member_hash_mismatches"].append(
                        {
                            "member": name,
                            "expected_sha256": expected_sha,
                            "actual_sha256": actual_sha,
                        }
                    )
            result["archive_roles_verified"] = dict(sorted(role_counts.items()))
            if result["member_hash_mismatches"]:
                result["errors"].append("archive_member_sha256_mismatch")

            order_name = str(manifest.get("canonical_input_order_file", ""))
            expected_order = [str(item) for item in manifest.get("canonical_input_order", [])]
            if order_name in member_bytes:
                order_text = member_bytes[order_name].decode("utf-8-sig")
                observed = _input_order(order_text)
                if not observed:
                    positions = [
                        (order_text.find(Path(name).stem), name) for name in expected_order
                    ]
                    if all(position >= 0 for position, _ in positions):
                        observed = [name for _, name in sorted(positions)]
                result["canonical_input_order_observed"] = observed
                result["canonical_input_order_passed"] = observed == expected_order
            if not result["canonical_input_order_passed"]:
                result["errors"].append("canonical_input_order_mismatch")

            rows = _matrix_rows(matrix_path)
            result["matrix_rows"] = len(rows)
            for row in rows:
                appendix = row.get("appendix_file", "")
                data = member_bytes.get(appendix)
                if data is None:
                    result["missing_first_labels"].append(
                        {"complex_id": row.get("complex_id", ""), "label": "<member missing>"}
                    )
                    continue
                text = data.decode("utf-8-sig")
                first_label = row.get("first_label", "").strip()
                if first_label:
                    if f"\\label{{{first_label}}}" in text:
                        result["verified_first_labels"] += 1
                    else:
                        result["missing_first_labels"].append(
                            {"complex_id": row.get("complex_id", ""), "label": first_label}
                        )
                for label in filter(None, row.get("equation_labels", "").split(";")):
                    label = label.strip()
                    if f"\\label{{{label}}}" in text:
                        result["verified_equation_labels"] += 1
                    else:
                        result["missing_equation_labels"].append(
                            {"complex_id": row.get("complex_id", ""), "label": label}
                        )
            if result["missing_first_labels"]:
                result["errors"].append("missing_first_labels")
            if result["missing_equation_labels"]:
                result["errors"].append("missing_equation_labels")
    except (OSError, UnicodeError, zipfile.BadZipFile) as error:
        result["errors"].append(f"archive_read_failure:{type(error).__name__}:{error}")

    result["passed"] = not result["errors"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()

    payload = verify(
        arguments.archive,
        manifest_path=arguments.manifest,
        matrix_path=arguments.matrix,
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"authoritative_archive={arguments.archive} "
        f"archive_sha256={payload['actual_archive_sha256']} "
        f"passed={payload['passed']} errors={payload['errors']}"
    )
    return 1 if arguments.check and not payload["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
