"""Fail-closed byte and provenance verification for HF audio collections."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any


REQUIRED_CATEGORIES = {"speech", "music", "sound_effects"}
REQUIRED_PARTITIONS = {"permissive", "noncommercial", "unknown_or_mixed"}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def verify_collection(root: str | Path) -> dict[str, Any]:
    output = Path(root)
    summary_path = output / "collection_summary.json"
    manifest_path = output / "audio_manifest.jsonl"
    source_summary_path = output / "source_summary.csv"
    for required in (summary_path, manifest_path, source_summary_path):
        if not required.is_file() or required.stat().st_size == 0:
            raise RuntimeError(f"missing or empty collection evidence: {required}")

    summary = _load_json(summary_path)
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError(f"manifest line {line_number} is not an object")
        records.append(value)

    declared_total = int(summary.get("collected_total", -1))
    declared_unique = int(summary.get("unique_audio_sha256", -1))
    if declared_total <= 0 or declared_total != len(records):
        raise RuntimeError(
            f"collection total mismatch: summary={declared_total}, manifest={len(records)}"
        )

    observed_hashes: set[str] = set()
    observed_paths: set[str] = set()
    counts_by_category: dict[str, int] = {}
    counts_by_partition: dict[str, int] = {}
    total_bytes = 0
    for index, record in enumerate(records):
        relative = str(record.get("relative_path", ""))
        pure = PurePosixPath(relative)
        if not relative or pure.is_absolute() or ".." in pure.parts:
            raise RuntimeError(f"unsafe manifest path at row {index}: {relative!r}")
        if relative in observed_paths:
            raise RuntimeError(f"duplicate manifest path: {relative}")
        observed_paths.add(relative)

        target = output / Path(*pure.parts)
        if not target.is_file():
            raise RuntimeError(f"manifest file is missing: {relative}")
        declared_bytes = int(record.get("bytes", -1))
        actual_bytes = target.stat().st_size
        if declared_bytes <= 0 or declared_bytes != actual_bytes:
            raise RuntimeError(
                f"byte-size mismatch for {relative}: {declared_bytes} != {actual_bytes}"
            )
        declared_sha = str(record.get("sha256", "")).lower()
        actual_sha = _sha256_file(target)
        if len(declared_sha) != 64 or declared_sha != actual_sha:
            raise RuntimeError(f"SHA-256 mismatch for {relative}")
        if actual_sha in observed_hashes:
            raise RuntimeError(f"duplicate audio bytes survived deduplication: {actual_sha}")
        observed_hashes.add(actual_sha)
        total_bytes += actual_bytes

        category = str(record.get("category", ""))
        partition = str(record.get("license_partition", ""))
        counts_by_category[category] = counts_by_category.get(category, 0) + 1
        counts_by_partition[partition] = counts_by_partition.get(partition, 0) + 1

    if len(observed_hashes) != declared_unique or declared_unique != declared_total:
        raise RuntimeError(
            "unique SHA count is inconsistent with the deduplicated collection"
        )
    if set(counts_by_category) != REQUIRED_CATEGORIES:
        raise RuntimeError(
            f"required categories missing or unexpected: {sorted(counts_by_category)}"
        )
    if set(counts_by_partition) != REQUIRED_PARTITIONS:
        raise RuntimeError(
            "required license partitions missing or unexpected: "
            f"{sorted(counts_by_partition)}"
        )
    if any(count <= 0 for count in counts_by_category.values()):
        raise RuntimeError("every required audio category must contain data")
    if any(count <= 0 for count in counts_by_partition.values()):
        raise RuntimeError("every required license partition must contain data")

    summary_category_counts = {
        str(key): int(value)
        for key, value in dict(summary.get("counts_by_category", {})).items()
    }
    summary_partition_counts = {
        str(key): int(value)
        for key, value in dict(
            summary.get("counts_by_license_partition", {})
        ).items()
    }
    if summary_category_counts != counts_by_category:
        raise RuntimeError("summary category counts do not match manifest bytes")
    if summary_partition_counts != counts_by_partition:
        raise RuntimeError("summary license counts do not match manifest bytes")
    if summary.get("empty_sources"):
        raise RuntimeError(f"one or more configured sources were empty: {summary['empty_sources']}")

    sources = summary.get("sources")
    if not isinstance(sources, list) or len(sources) != len(REQUIRED_CATEGORIES):
        raise RuntimeError("source summary must contain one source per required category")
    for source in sources:
        if not isinstance(source, dict):
            raise RuntimeError("source summary row must be an object")
        if int(source.get("accepted", 0)) <= 0:
            raise RuntimeError(f"source accepted no clips: {source.get('repo_id')}")
        if source.get("errors"):
            raise RuntimeError(
                f"source reported ingestion errors: {source.get('repo_id')}"
            )

    report = {
        "schema_version": "1.0",
        "verification_status": "passed",
        "collection_root": output.name,
        "manifest_records": len(records),
        "unique_audio_sha256": len(observed_hashes),
        "total_audio_bytes": total_bytes,
        "counts_by_category": counts_by_category,
        "counts_by_license_partition": counts_by_partition,
        "manifest_sha256": _sha256_file(manifest_path),
        "summary_sha256": _sha256_file(summary_path),
        "source_summary_sha256": _sha256_file(source_summary_path),
        "verification_boundary": (
            "independent file existence, byte size, SHA-256, deduplication, "
            "category, source and license-partition verification"
        ),
    }
    (output / "verification_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    report = verify_collection(args.root)
    print(
        "hf_audio_verification=passed "
        f"clips={report['manifest_records']} "
        f"bytes={report['total_audio_bytes']} "
        f"categories={report['counts_by_category']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
