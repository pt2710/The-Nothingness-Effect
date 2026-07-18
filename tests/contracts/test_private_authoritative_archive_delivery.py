from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tools.private_authoritative_archive_delivery import (
    DeliveryError,
    decrypt_archive_bytes,
    derive_key_from_passphrase,
    encode_key,
    encrypt_archive_bytes,
    generate_key,
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_private_archive_round_trip_preserves_exact_bytes():
    archive = b"PK\x03\x04synthetic-authoritative-archive-bytes"
    expected = _sha(archive)
    key = generate_key()
    envelope = encrypt_archive_bytes(archive, key, expected)
    assert envelope != archive
    assert decrypt_archive_bytes(envelope, key, expected) == archive
    assert len(encode_key(key)) == 44


def test_passphrase_derivation_is_deterministic_and_archive_bound():
    passphrase = "p" * 64
    first_sha = _sha(b"archive-one")
    second_sha = _sha(b"archive-two")
    assert derive_key_from_passphrase(passphrase, first_sha) == derive_key_from_passphrase(
        passphrase, first_sha
    )
    assert derive_key_from_passphrase(passphrase, first_sha) != derive_key_from_passphrase(
        passphrase, second_sha
    )


def test_private_archive_passphrase_round_trip_preserves_exact_bytes():
    archive = b"PK\x03\x04passphrase-authoritative-archive"
    expected = _sha(archive)
    key = derive_key_from_passphrase("high-entropy-passphrase-" * 3, expected)
    envelope = encrypt_archive_bytes(archive, key, expected)
    assert decrypt_archive_bytes(envelope, key, expected) == archive


def test_private_archive_rejects_short_passphrase():
    with pytest.raises(DeliveryError, match="at least"):
        derive_key_from_passphrase("too-short", "0" * 64)


def test_private_archive_rejects_wrong_key():
    archive = b"PK\x03\x04authority"
    expected = _sha(archive)
    envelope = encrypt_archive_bytes(archive, generate_key(), expected)
    with pytest.raises(DeliveryError, match="authentication failed"):
        decrypt_archive_bytes(envelope, generate_key(), expected)


def test_private_archive_rejects_tampered_ciphertext():
    archive = b"PK\x03\x04authority"
    expected = _sha(archive)
    key = generate_key()
    envelope = bytearray(encrypt_archive_bytes(archive, key, expected))
    envelope[-1] ^= 1
    with pytest.raises(DeliveryError, match="authentication failed"):
        decrypt_archive_bytes(bytes(envelope), key, expected)


def test_private_archive_rejects_wrong_expected_archive_hash():
    archive = b"PK\x03\x04authority"
    with pytest.raises(DeliveryError, match="mismatch before encryption"):
        encrypt_archive_bytes(archive, generate_key(), "0" * 64)


def test_ci_materializes_private_envelope_and_never_uploads_plaintext():
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "TNE_AUTHORITATIVE_ARCHIVE_PASSPHRASE" in workflow
    assert "TNE_AUTHORITATIVE_ARCHIVE_KEY" in workflow
    assert "private_authority/TNE_Authoritative_Appendices.zip.enc" in workflow
    assert "private_authoritative_archive_delivery.py decrypt" in workflow
    assert "--passphrase-env TNE_AUTHORITATIVE_ARCHIVE_PASSPHRASE" in workflow
    assert "verify_authoritative_archive.py" in workflow
    assert "shred -u" in workflow
    assert "status=$?" in workflow
    assert 'exit "${status}"' in workflow
    artifact_block = workflow.split("name: authoritative-archive-byte-evidence", 1)[1]
    artifact_block = artifact_block.split("name: Enforce authoritative archive byte gate", 1)[0]
    assert "TNE_Authoritative_Appendices.zip" not in artifact_block
    assert ".tex" not in artifact_block
