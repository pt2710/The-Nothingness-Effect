"""Download exact CIFAR Python archives from hash-pinned mirrors.

The University of Toronto MD5 values remain the byte-identity authority. The
mirrors are transport fallbacks only; any byte drift fails closed before the
archives reach the evaluation pipeline.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
from typing import Any

from huggingface_hub import hf_hub_download


@dataclass(frozen=True)
class ArchiveSpec:
    name: str
    repo_id: str
    filename: str
    revision: str
    expected_md5: str
    expected_sha256: str
    official_url: str


SPECS = (
    ArchiveSpec(
        name="cifar-10",
        repo_id="xingslong/cifar-10-batches-py",
        filename="cifar-10-python.tar.gz",
        revision="main",
        expected_md5="c58f30108f718f92721af3b95e74349a",
        expected_sha256=(
            "6d958be074577803d12ecdefd02955f39262c83c16fe9348329d7fe0b5c001ce"
        ),
        official_url="https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz",
    ),
    ArchiveSpec(
        name="cifar-100",
        repo_id="nakroy/cifar100-python",
        filename="cifar-100-python.tar.gz",
        revision="201a32345d2c6b970e1a36c582930c83e09c96d2",
        expected_md5="eb9058c3a382ffc7106e4002c42a8d85",
        expected_sha256=(
            "85cd44d02ba6437773c5bbd22e183051d648de2e7d6b014e1ef29b855ba677a7"
        ),
        official_url="https://www.cs.toronto.edu/~kriz/cifar-100-python.tar.gz",
    ),
)


def _digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def download_verified_archives(output_dir: str | Path) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for spec in SPECS:
        cached = Path(
            hf_hub_download(
                repo_id=spec.repo_id,
                filename=spec.filename,
                repo_type="dataset",
                revision=spec.revision,
            )
        )
        if not cached.is_file() or cached.stat().st_size <= 0:
            raise RuntimeError(f"mirror returned no archive bytes: {spec.repo_id}")
        target = output / spec.filename
        temporary = target.with_suffix(target.suffix + ".partial")
        shutil.copyfile(cached, temporary)
        md5 = _digest(temporary, "md5")
        sha256 = _digest(temporary, "sha256")
        if md5 != spec.expected_md5:
            raise RuntimeError(
                f"official MD5 mismatch for {spec.name}: {md5} != {spec.expected_md5}"
            )
        if sha256 != spec.expected_sha256:
            raise RuntimeError(
                f"pinned SHA-256 mismatch for {spec.name}: "
                f"{sha256} != {spec.expected_sha256}"
            )
        temporary.replace(target)
        records.append(
            {
                "name": spec.name,
                "filename": spec.filename,
                "bytes": target.stat().st_size,
                "md5": md5,
                "sha256": sha256,
                "transport_repo_id": spec.repo_id,
                "transport_revision": spec.revision,
                "official_origin": spec.official_url,
                "authority": (
                    "University of Toronto archive identity, enforced by the "
                    "official MD5 and an independently pinned SHA-256"
                ),
            }
        )
    manifest = {
        "schema_version": "1.0",
        "verification_status": "passed",
        "archive_count": len(records),
        "archives": records,
        "transport_boundary": (
            "Hugging Face is used only as a high-availability byte transport; "
            "unmatched bytes are rejected before evaluation"
        ),
    }
    (output / "cifar_source_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = download_verified_archives(args.output)
    print(
        "cifar_archive_download=verified "
        f"archives={manifest['archive_count']} "
        + " ".join(
            f"{row['name']}={row['sha256']}" for row in manifest["archives"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
