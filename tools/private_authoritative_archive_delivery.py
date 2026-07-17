"""Encrypt or decrypt the authoritative TNE appendix ZIP without publishing plaintext.

The envelope uses AES-256-GCM. The exact authoritative ZIP bytes are encrypted
locally, and only the authenticated ciphertext is tracked. The 256-bit key is
stored in a GitHub Actions secret and is never written to the repository.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import os
from pathlib import Path
import secrets
import sys

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"TNEAUTH1"
NONCE_BYTES = 12
KEY_BYTES = 32
AAD_PREFIX = b"TNE authoritative appendix archive\x00"


class DeliveryError(RuntimeError):
    """Raised when a private archive envelope is invalid or cannot be opened."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def generate_key() -> bytes:
    return secrets.token_bytes(KEY_BYTES)


def encode_key(key: bytes) -> str:
    if len(key) != KEY_BYTES:
        raise DeliveryError(f"expected {KEY_BYTES} key bytes, got {len(key)}")
    return base64.urlsafe_b64encode(key).decode("ascii")


def decode_key(value: str) -> bytes:
    try:
        key = base64.urlsafe_b64decode(value.encode("ascii"))
    except (ValueError, UnicodeError) as error:
        raise DeliveryError("archive key is not valid URL-safe base64") from error
    if len(key) != KEY_BYTES:
        raise DeliveryError(f"archive key must decode to {KEY_BYTES} bytes")
    return key


def associated_data(expected_sha256: str) -> bytes:
    normalized = expected_sha256.strip().lower()
    if len(normalized) != 64 or any(ch not in "0123456789abcdef" for ch in normalized):
        raise DeliveryError("expected archive SHA-256 must be 64 lowercase hex characters")
    return AAD_PREFIX + normalized.encode("ascii")


def encrypt_archive_bytes(archive_bytes: bytes, key: bytes, expected_sha256: str) -> bytes:
    actual = sha256_bytes(archive_bytes)
    if actual != expected_sha256.lower():
        raise DeliveryError(
            f"authoritative archive SHA-256 mismatch before encryption: expected {expected_sha256}, got {actual}"
        )
    nonce = secrets.token_bytes(NONCE_BYTES)
    ciphertext = AESGCM(key).encrypt(nonce, archive_bytes, associated_data(expected_sha256))
    return MAGIC + nonce + ciphertext


def decrypt_archive_bytes(envelope: bytes, key: bytes, expected_sha256: str) -> bytes:
    minimum = len(MAGIC) + NONCE_BYTES + 16
    if len(envelope) < minimum or not envelope.startswith(MAGIC):
        raise DeliveryError("invalid authoritative archive envelope header")
    nonce_start = len(MAGIC)
    nonce_end = nonce_start + NONCE_BYTES
    nonce = envelope[nonce_start:nonce_end]
    ciphertext = envelope[nonce_end:]
    try:
        archive_bytes = AESGCM(key).decrypt(
            nonce,
            ciphertext,
            associated_data(expected_sha256),
        )
    except InvalidTag as error:
        raise DeliveryError("authoritative archive envelope authentication failed") from error
    actual = sha256_bytes(archive_bytes)
    if actual != expected_sha256.lower():
        raise DeliveryError(
            f"decrypted authoritative archive SHA-256 mismatch: expected {expected_sha256}, got {actual}"
        )
    return archive_bytes


def _secure_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(data)


def encrypt_file(archive: Path, output: Path, key: bytes, expected_sha256: str) -> None:
    if not archive.is_file():
        raise DeliveryError(f"authoritative archive does not exist: {archive}")
    _secure_write(output, encrypt_archive_bytes(archive.read_bytes(), key, expected_sha256))


def decrypt_file(encrypted: Path, output: Path, key: bytes, expected_sha256: str) -> None:
    if not encrypted.is_file():
        raise DeliveryError(f"encrypted authoritative archive does not exist: {encrypted}")
    _secure_write(output, decrypt_archive_bytes(encrypted.read_bytes(), key, expected_sha256))


def _command_encrypt(arguments: argparse.Namespace) -> int:
    key = generate_key() if arguments.key is None else decode_key(arguments.key)
    encrypt_file(arguments.archive, arguments.output, key, arguments.expected_sha256)
    encoded = encode_key(key)
    if arguments.key_output:
        _secure_write(arguments.key_output, (encoded + "\n").encode("ascii"))
    else:
        print(encoded)
    print(
        f"encrypted_archive={arguments.output} encrypted_sha256={sha256_bytes(arguments.output.read_bytes())}",
        file=sys.stderr,
    )
    return 0


def _command_decrypt(arguments: argparse.Namespace) -> int:
    value = arguments.key
    if value is None and arguments.key_env:
        value = os.environ.get(arguments.key_env)
    if not value:
        raise DeliveryError("authoritative archive decryption key is unavailable")
    decrypt_file(
        arguments.encrypted,
        arguments.output,
        decode_key(value),
        arguments.expected_sha256,
    )
    print(
        f"decrypted_archive={arguments.output} archive_sha256={sha256_bytes(arguments.output.read_bytes())}",
        file=sys.stderr,
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    encrypt_parser = subparsers.add_parser("encrypt")
    encrypt_parser.add_argument("--archive", type=Path, required=True)
    encrypt_parser.add_argument("--output", type=Path, required=True)
    encrypt_parser.add_argument("--expected-sha256", required=True)
    encrypt_parser.add_argument("--key")
    encrypt_parser.add_argument("--key-output", type=Path)
    encrypt_parser.set_defaults(handler=_command_encrypt)

    decrypt_parser = subparsers.add_parser("decrypt")
    decrypt_parser.add_argument("--encrypted", type=Path, required=True)
    decrypt_parser.add_argument("--output", type=Path, required=True)
    decrypt_parser.add_argument("--expected-sha256", required=True)
    decrypt_parser.add_argument("--key")
    decrypt_parser.add_argument("--key-env", default="TNE_AUTHORITATIVE_ARCHIVE_KEY")
    decrypt_parser.set_defaults(handler=_command_decrypt)

    arguments = parser.parse_args()
    try:
        return int(arguments.handler(arguments))
    except DeliveryError as error:
        print(f"private authoritative archive delivery failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
