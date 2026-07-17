# Private authoritative archive delivery

The authoritative appendix sources remain external to the public repository. CI receives the exact ZIP bytes through an authenticated encrypted envelope:

1. The exact authoritative ZIP is verified locally against `docs/data/authoritative_archive_manifest.json`.
2. The ZIP bytes are encrypted with AES-256-GCM.
3. Only `private_authority/TNE_Authoritative_Appendices.zip.enc` is tracked.
4. The 256-bit key is stored as the GitHub Actions secret `TNE_AUTHORITATIVE_ARCHIVE_KEY`.
5. Actions decrypts into `$RUNNER_TEMP`, verifies archive SHA-256, ZIP CRC, all ten member hashes, canonical input order, and all inventory labels, then removes the plaintext temporary file.
6. Neither the plaintext ZIP nor extracted `.tex` files are uploaded as artifacts.

The encrypted envelope is not itself an authoritative source. Release authority remains the decrypted byte stream with SHA-256:

```text
38901b612b0f868cf66e2bab95e4600378b46bab80dee5a6d55180ccca59ea11
```

The URL-based delivery variable remains an explicit fallback only. A release passes only after the byte verifier validates the decrypted or privately fetched stream.
