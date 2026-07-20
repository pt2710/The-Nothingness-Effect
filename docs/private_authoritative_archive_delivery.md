# Private authoritative archive delivery

The authoritative appendix sources remain external to the public repository. CI receives the exact ZIP bytes through an authenticated encrypted envelope:

1. The exact authoritative ZIP is verified locally against `docs/data/authoritative_archive_manifest.json`.
2. The ZIP bytes are encrypted with AES-256-GCM.
3. Only `private_authority/TNE_Authoritative_Appendices.zip.enc` is tracked.
4. The existing high-entropy passphrase is stored as the GitHub Actions secret `TNE_AUTHORITATIVE_ARCHIVE_PASSPHRASE`.
5. The AES-256 key is derived with PBKDF2-HMAC-SHA256 using 600,000 iterations and a domain-separated salt bound to the authoritative archive SHA-256. The legacy direct-key secret `TNE_AUTHORITATIVE_ARCHIVE_KEY` remains supported as a fallback.
6. Actions decrypts into `$RUNNER_TEMP`, verifies archive SHA-256, ZIP CRC, all ten member hashes, canonical input order, and all inventory labels, then removes the plaintext temporary file.
7. Neither the plaintext ZIP nor extracted `.tex` files are uploaded as artifacts.

The encrypted envelope is not itself an authoritative source. Release authority remains the decrypted byte stream with SHA-256:

```text
38901b612b0f868cf66e2bab95e4600378b46bab80dee5a6d55180ccca59ea11
```

The tracked envelope has SHA-256:

```text
a0b431936bd1a411a5255baa179665450857995060944692ecf5934ee6de04b2
```

The URL-based delivery variable remains an explicit fallback only. A release passes only after the byte verifier validates the decrypted or privately fetched stream.
