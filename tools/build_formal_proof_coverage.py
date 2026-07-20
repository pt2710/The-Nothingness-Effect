"""Build a fail-closed theorem-by-theorem formal machine-proof ledger."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_PROOF_FIELDS = (
    "formal_proof_backend",
    "formal_proof_kernel",
    "formal_proof_certificate_path",
    "formal_proof_certificate_sha256",
    "formal_proof_assumptions_sha256",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify(manifest: dict[str, Any], repository_root: Path) -> dict[str, str]:
    metadata = manifest.get("approximation_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    verified = metadata.get("formal_proof_verified") is True
    supplied = {name: str(metadata.get(name, "")).strip() for name in REQUIRED_PROOF_FIELDS}
    any_claim = verified or any(supplied.values())
    missing = [name for name, value in supplied.items() if not value]
    certificate = repository_root / supplied["formal_proof_certificate_path"] if supplied["formal_proof_certificate_path"] else None
    certificate_exists = certificate is not None and certificate.is_file()
    certificate_hash_matches = bool(
        certificate_exists
        and len(supplied["formal_proof_certificate_sha256"]) == 64
        and _sha256(certificate) == supplied["formal_proof_certificate_sha256"]
    )
    assumptions_hash_valid = len(supplied["formal_proof_assumptions_sha256"]) == 64
    complete = verified and not missing and certificate_hash_matches and assumptions_hash_valid
    if complete:
        status = "verified"
        reason = "kernel-checked certificate and assumptions hash verified"
    elif any_claim:
        status = "invalid_proof_claim"
        reason = "; ".join(
            [*(f"missing {name}" for name in missing),
             *( [] if certificate_exists else ["certificate file missing"] ),
             *( [] if certificate_hash_matches else ["certificate hash not verified"] ),
             *( [] if assumptions_hash_valid else ["assumptions hash invalid"] )]
        ) or "formal proof claim incomplete"
    else:
        status = "not_formally_proved"
        reason = "no proof-assistant kernel evidence or independently checkable certificate"
    return {
        "formal_proof_status": status,
        "formal_proof_reason": reason,
        **supplied,
    }


def build(matrix_path: Path, provenance_path: Path, csv_output: Path, json_output: Path, repository_root: Path) -> dict[str, Any]:
    with matrix_path.open(newline="", encoding="utf-8-sig") as handle:
        matrix = list(csv.DictReader(handle))
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    manifests = provenance.get("manifests")
    if not isinstance(manifests, list):
        raise RuntimeError("provenance manifest list is missing")
    by_id = {str(item.get("theorem_complex_id")): item for item in manifests if isinstance(item, dict)}
    records: list[dict[str, str]] = []
    for row in matrix:
        identifier = str(row["complex_id"])
        manifest = by_id.get(identifier)
        if manifest is None:
            raise RuntimeError(f"missing provenance manifest: {identifier}")
        records.append({
            "complex_id": identifier,
            "appendix_file": str(row.get("appendix_file", "")),
            "level": str(row.get("level", "")),
            "implementation_path": str(row.get("implementation_status_evidence_path") or row.get("implementation_path", "")),
            **classify(manifest, repository_root),
        })
    counts = dict(Counter(record["formal_proof_status"] for record in records))
    report = {
        "schema_version": "1.0",
        "rows": len(records),
        "counts": counts,
        "all_rows_classified": len(records) == len(matrix) == len(by_id),
        "invalid_proof_claims": counts.get("invalid_proof_claim", 0),
        "verified_formal_proofs": counts.get("verified", 0),
        "policy": "tests, exact_semantics, simulations, and small residuals are not formal proofs without kernel-checked certificate evidence",
        "records": records,
    }
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]) if records else ["complex_id"])
        writer.writeheader(); writer.writerows(records)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not report["all_rows_classified"] or report["invalid_proof_claims"]:
        raise RuntimeError("formal proof coverage audit failed")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=Path("reports/effective_theorem_complex_implementation_matrix.csv"))
    parser.add_argument("--provenance", type=Path, default=Path("reports/effective_artifact_provenance_manifest.json"))
    parser.add_argument("--csv-output", type=Path, default=Path("reports/formal_proof_coverage.csv"))
    parser.add_argument("--json-output", type=Path, default=Path("reports/formal_proof_coverage.json"))
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    args = parser.parse_args()
    report = build(args.matrix, args.provenance, args.csv_output, args.json_output, args.repository_root)
    print(f"formal_proof_coverage=passed rows={report['rows']} verified={report['verified_formal_proofs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
