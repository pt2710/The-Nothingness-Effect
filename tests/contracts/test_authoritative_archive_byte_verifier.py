from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import zipfile

from tools.verify_authoritative_archive import verify


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fixture(tmp_path: Path):
    order = b"\\input{appendix_source}\n\\input{appendix_commentary}\n"
    source = b"\\section{Source}\\label{first:source}\n\\begin{equation}x=x\\label{eq:source}\\end{equation}\n"
    commentary = b"commentary\n"
    members = {
        "TNE_APPENDIX_CANONICAL_INPUT_ORDER.tex": order,
        "appendix_source.tex": source,
        "appendix_commentary.tex": commentary,
    }
    archive = tmp_path / "authority.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for name, data in members.items():
            handle.writestr(name, data)

    manifest = {
        "archive_sha256": _sha(archive.read_bytes()),
        "canonical_input_order_file": "TNE_APPENDIX_CANONICAL_INPUT_ORDER.tex",
        "canonical_input_order": ["appendix_source.tex", "appendix_commentary.tex"],
        "members": {
            "TNE_APPENDIX_CANONICAL_INPUT_ORDER.tex": {
                "sha256": _sha(order),
                "role": "canonical_input_order",
            },
            "appendix_source.tex": {
                "sha256": _sha(source),
                "role": "theorem_runtime",
            },
            "appendix_commentary.tex": {
                "sha256": _sha(commentary),
                "role": "commentary_validation",
            },
        },
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    matrix_path = tmp_path / "matrix.csv"
    with matrix_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("complex_id", "appendix_file", "first_label", "equation_labels"),
        )
        writer.writeheader()
        writer.writerow(
            {
                "complex_id": "fixture",
                "appendix_file": "appendix_source.tex",
                "first_label": "first:source",
                "equation_labels": "eq:source",
            }
        )
    return archive, manifest_path, matrix_path


def test_verifier_reads_actual_zip_bytes_and_labels(tmp_path: Path):
    archive, manifest, matrix = _fixture(tmp_path)
    report = verify(archive, manifest_path=manifest, matrix_path=matrix)
    assert report["passed"] is True
    assert report["archive_sha256_match"] is True
    assert report["zip_crc_passed"] is True
    assert report["member_set_exact"] is True
    assert report["canonical_input_order_passed"] is True
    assert report["verified_first_labels"] == 1
    assert report["verified_equation_labels"] == 1


def test_verifier_fails_closed_when_archive_bytes_are_missing(tmp_path: Path):
    _, manifest, matrix = _fixture(tmp_path)
    report = verify(
        tmp_path / "missing.zip",
        manifest_path=manifest,
        matrix_path=matrix,
    )
    assert report["passed"] is False
    assert report["errors"] == ["authoritative_archive_bytes_unavailable"]


def test_verifier_rejects_tampered_archive_bytes(tmp_path: Path):
    archive, manifest, matrix = _fixture(tmp_path)
    with archive.open("ab") as handle:
        handle.write(b"tamper")
    report = verify(archive, manifest_path=manifest, matrix_path=matrix)
    assert report["passed"] is False
    assert report["archive_sha256_match"] is False
    assert "archive_sha256_mismatch" in report["errors"]
