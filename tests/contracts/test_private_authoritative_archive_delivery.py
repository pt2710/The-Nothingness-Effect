from __future__ import annotations

import hashlib

import pytest

from tools.private_authoritative_archive_delivery import (
    DeliveryError,
    decrypt_archive_bytes,
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
