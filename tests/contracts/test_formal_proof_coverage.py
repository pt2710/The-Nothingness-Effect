from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from tools.build_formal_proof_coverage import build, classify


def _manifest(identifier: str, metadata: dict | None = None) -> dict:
    return {
        "theorem_complex_id": identifier,
        "closure_status": "closed",
        "approximation_metadata": metadata or {},
    }


def test_tests_and_exact_semantics_are_not_formal_proofs(tmp_path: Path):
    record = classify(
        _manifest("alpha", {"exact_semantics": True, "typed_sample": True}),
        tmp_path,
    )
    assert record["formal_proof_status"] == "not_formally_proved"
    assert "certificate" in record["formal_proof_reason"]


def test_complete_kernel_certificate_is_verified(tmp_path: Path):
    certificate = tmp_path / "proofs" / "alpha.cert"
    certificate.parent.mkdir()
    certificate.write_bytes(b"kernel checked proof certificate\n")
    digest = hashlib.sha256(certificate.read_bytes()).hexdigest()
    metadata = {
        "formal_proof_verified": True,
        "formal_proof_backend": "example-assistant",
        "formal_proof_kernel": "example-kernel-v1",
        "formal_proof_certificate_path": "proofs/alpha.cert",
        "formal_proof_certificate_sha256": digest,
        "formal_proof_assumptions_sha256": "a" * 64,
    }
    record = classify(_manifest("alpha", metadata), tmp_path)
    assert record["formal_proof_status"] == "verified"


def test_incomplete_proof_claim_fails_audit(tmp_path: Path):
    matrix = tmp_path / "matrix.csv"
    with matrix.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["complex_id", "appendix_file", "level", "implementation_path"])
        writer.writeheader()
        writer.writerow({"complex_id": "alpha", "appendix_file": "a.tex", "level": "A", "implementation_path": "alpha.py"})
    provenance = tmp_path / "provenance.json"
    provenance.write_text(json.dumps({"manifests": [_manifest("alpha", {"formal_proof_verified": True})]}), encoding="utf-8")
    with pytest.raises(RuntimeError, match="formal proof coverage audit failed"):
        build(matrix, provenance, tmp_path / "out.csv", tmp_path / "out.json", tmp_path)


def test_unclaimed_inventory_is_fully_classified(tmp_path: Path):
    matrix = tmp_path / "matrix.csv"
    with matrix.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["complex_id", "appendix_file", "level", "implementation_path"])
        writer.writeheader()
        writer.writerow({"complex_id": "alpha", "appendix_file": "a.tex", "level": "A", "implementation_path": "alpha.py"})
    provenance = tmp_path / "provenance.json"
    provenance.write_text(json.dumps({"manifests": [_manifest("alpha")]}), encoding="utf-8")
    report = build(matrix, provenance, tmp_path / "out.csv", tmp_path / "out.json", tmp_path)
    assert report["rows"] == 1
    assert report["verified_formal_proofs"] == 0
    assert report["counts"] == {"not_formally_proved": 1}
