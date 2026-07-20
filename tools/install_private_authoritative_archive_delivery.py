"""Install the exact authoritative ZIP as a private encrypted GitHub Actions delivery.

Requirements:
- Python 3.11+
- cryptography
- GitHub CLI (gh), authenticated with repository write and Actions-secret access
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import subprocess
import tempfile

from tools.private_authoritative_archive_delivery import (
    encode_key,
    encrypt_archive_bytes,
    generate_key,
    sha256_bytes,
)

EXPECTED_SHA256 = "38901b612b0f868cf66e2bab95e4600378b46bab80dee5a6d55180ccca59ea11"
DEFAULT_REPO = "pt2710/The-Nothingness-Effect"
DEFAULT_BRANCH = "codex/tne-authoritative-source-recertification"
DEFAULT_PATH = "private_authority/TNE_Authoritative_Appendices.zip.enc"


def run(command: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, input=input_text, text=True, check=True, capture_output=True)


def current_blob_sha(repo: str, path: str, branch: str) -> str | None:
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/contents/{path}?ref={branch}", "--jq", ".sha"],
        text=True,
        capture_output=True,
    )
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None


def install(archive: Path, repo: str, branch: str, path: str, trigger: bool) -> None:
    archive_bytes = archive.read_bytes()
    actual = sha256_bytes(archive_bytes)
    if actual != EXPECTED_SHA256:
        raise SystemExit(f"archive SHA-256 mismatch: expected {EXPECTED_SHA256}, got {actual}")

    key = generate_key()
    encrypted = encrypt_archive_bytes(archive_bytes, key, EXPECTED_SHA256)
    encoded_key = encode_key(key)

    run(
        ["gh", "secret", "set", "TNE_AUTHORITATIVE_ARCHIVE_KEY", "--repo", repo],
        input_text=encoded_key,
    )

    payload: dict[str, str] = {
        "message": "Install encrypted private authoritative archive delivery",
        "branch": branch,
        "content": base64.b64encode(encrypted).decode("ascii"),
    }
    existing_sha = current_blob_sha(repo, path, branch)
    if existing_sha:
        payload["sha"] = existing_sha

    with tempfile.TemporaryDirectory() as directory:
        request = Path(directory) / "request.json"
        request.write_text(json.dumps(payload), encoding="utf-8")
        run(
            [
                "gh",
                "api",
                "--method",
                "PUT",
                f"repos/{repo}/contents/{path}",
                "--input",
                str(request),
            ]
        )

    print(f"installed encrypted payload: {repo}@{branch}:{path}")
    print(f"plaintext archive SHA-256: {actual}")
    print(f"encrypted envelope SHA-256: {sha256_bytes(encrypted)}")

    if trigger:
        run(["gh", "workflow", "run", "ci.yml", "--repo", repo, "--ref", branch])
        print("triggered theorem-complex-ci workflow")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--path", default=DEFAULT_PATH)
    parser.add_argument("--trigger", action="store_true")
    arguments = parser.parse_args()
    if not arguments.archive.is_file():
        raise SystemExit(f"archive not found: {arguments.archive}")
    install(arguments.archive, arguments.repo, arguments.branch, arguments.path, arguments.trigger)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
