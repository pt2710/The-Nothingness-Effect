"""Collect a bounded, licensed and hash-audited Hugging Face audio corpus.

The collector streams source datasets, caps every source and the global total,
routes non-commercial or unknown licenses into separate partitions, removes
exact duplicate audio bytes, and records reproducible provenance. It never
silently promotes an unknown license into the permissive partition.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
from typing import Any, Callable, Iterable, Mapping

import numpy as np
import soundfile as sf


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


PERMISSIVE_LICENSE_TOKENS = {
    "apache-2.0",
    "bsd-2-clause",
    "bsd-3-clause",
    "cc-by-3.0",
    "cc-by-4.0",
    "cc0-1.0",
    "mit",
    "mpl-2.0",
    "odc-by",
    "public-domain",
}
NONCOMMERCIAL_TOKENS = {
    "cc-by-nc",
    "cc-by-nc-2.0",
    "cc-by-nc-3.0",
    "cc-by-nc-4.0",
    "research-only",
    "non-commercial",
    "noncommercial",
}


@dataclass(frozen=True)
class AudioSource:
    repo_id: str
    category: str
    split: str = "train"
    config: str | None = None
    revision: str = "main"
    audio_column: str = "audio"
    declared_license: str = "unknown"
    max_items: int | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "AudioSource":
        repo_id = str(value.get("repo_id", "")).strip()
        category = str(value.get("category", "")).strip().lower()
        if not repo_id or category not in {"speech", "music", "sound_effects"}:
            raise ValueError(
                "each source requires repo_id and category in "
                "{speech,music,sound_effects}"
            )
        max_items = value.get("max_items")
        return cls(
            repo_id=repo_id,
            category=category,
            split=str(value.get("split", "train")),
            config=(str(value["config"]) if value.get("config") is not None else None),
            revision=str(value.get("revision", "main")),
            audio_column=str(value.get("audio_column", "audio")),
            declared_license=str(value.get("license", "unknown")),
            max_items=(int(max_items) if max_items is not None else None),
        )


def _slug(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-.")
    return text or "unnamed"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _normalize_license(value: object) -> str:
    if isinstance(value, (list, tuple, set)):
        return ",".join(sorted(_normalize_license(item) for item in value))
    return str(value or "unknown").strip().lower().replace("_", "-")


def license_partition(value: object) -> str:
    normalized = _normalize_license(value)
    tokens = {
        token.strip() for token in re.split(r"[,;/|]", normalized) if token.strip()
    }
    if not tokens or tokens == {"unknown"}:
        return "unknown_or_mixed"
    if any(
        token in NONCOMMERCIAL_TOKENS
        or "noncommercial" in token
        or "non-commercial" in token
        for token in tokens
    ):
        return "noncommercial"
    if tokens <= PERMISSIVE_LICENSE_TOKENS:
        return "permissive"
    return "unknown_or_mixed"


def _json_safe(value: object, *, depth: int = 0) -> object:
    if depth > 4:
        return "<depth-limit>"
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    if isinstance(value, np.generic):
        return _json_safe(value.item(), depth=depth + 1)
    if isinstance(value, np.ndarray):
        return {
            "dtype": str(value.dtype),
            "shape": list(value.shape),
            "summary_only": True,
        }
    if isinstance(value, Mapping):
        return {
            str(key): _json_safe(item, depth=depth + 1)
            for key, item in value.items()
            if str(key) not in {"array", "bytes"}
        }
    if isinstance(value, (list, tuple)):
        return [_json_safe(item, depth=depth + 1) for item in value[:64]]
    return str(value)


def _audio_bytes(value: object) -> tuple[bytes, str, dict[str, Any]]:
    metadata: dict[str, Any] = {}
    if isinstance(value, Mapping):
        raw = value.get("bytes")
        path_value = value.get("path")
        if raw is not None:
            payload = bytes(raw)
            suffix = Path(str(path_value or "audio.bin")).suffix.lower() or ".bin"
            metadata["source_path"] = str(path_value or "")
            metadata["storage"] = "original_bytes"
            return payload, suffix, metadata
        if path_value:
            raw_path = str(path_value)
            path = Path(raw_path)
            if path.is_file():
                metadata["source_path"] = raw_path
                metadata["storage"] = "original_path_bytes"
                return path.read_bytes(), path.suffix.lower() or ".bin", metadata
            if raw_path.startswith("hf://"):
                try:
                    from huggingface_hub import HfFileSystem  # type: ignore
                except ImportError as exc:
                    raise RuntimeError(
                        "remote hf:// audio paths require huggingface_hub"
                    ) from exc
                with HfFileSystem().open(raw_path, "rb") as handle:
                    payload = handle.read()
                metadata["source_path"] = raw_path
                metadata["storage"] = "huggingface_hub_path_bytes"
                return payload, Path(raw_path).suffix.lower() or ".bin", metadata
        if value.get("array") is not None and value.get("sampling_rate") is not None:
            array = np.asarray(value["array"], dtype=np.float32)
            if array.ndim == 2 and array.shape[0] < array.shape[1]:
                array = array.T
            if array.ndim not in {1, 2} or not np.isfinite(array).all():
                raise ValueError("decoded audio array must be finite mono/stereo data")
            sample_rate = int(value["sampling_rate"])
            if sample_rate <= 0:
                raise ValueError("decoded audio requires a positive sampling rate")
            buffer = io.BytesIO()
            sf.write(buffer, array, sample_rate, format="WAV", subtype="PCM_16")
            metadata.update(
                {
                    "sampling_rate": sample_rate,
                    "frames": int(array.shape[0]),
                    "channels": 1 if array.ndim == 1 else int(array.shape[1]),
                    "storage": "decoded_pcm16_wav",
                }
            )
            return buffer.getvalue(), ".wav", metadata
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value), ".bin", {"storage": "raw_bytes"}
    if isinstance(value, str) and Path(value).is_file():
        path = Path(value)
        return path.read_bytes(), path.suffix.lower() or ".bin", {
            "source_path": str(path),
            "storage": "original_path_bytes",
        }
    raise ValueError("audio value has no usable bytes, local path, or decoded array")


def _load_hf_stream(source: AudioSource) -> tuple[Iterable[Mapping[str, Any]], str]:
    try:
        from datasets import load_dataset  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Hugging Face collection requires the optional 'datasets' package"
        ) from exc
    kwargs: dict[str, Any] = {
        "path": source.repo_id,
        "split": source.split,
        "streaming": True,
        "revision": source.revision,
    }
    if source.config is not None:
        kwargs["name"] = source.config
    stream = load_dataset(**kwargs)
    # Current Datasets releases decode Audio through TorchCodec by default.
    # Streaming IterableDataset.decode(False) returns the raw {path, bytes}
    # storage representation without importing TorchCodec or FFmpeg.
    stream = stream.decode(False)
    info = getattr(stream, "info", None)
    observed_license = str(getattr(info, "license", "") or source.declared_license)
    return stream, observed_license


def collect_audio_sources(
    sources: Iterable[AudioSource],
    output_dir: str | Path,
    *,
    max_per_source: int = 100,
    max_total: int = 600,
    loader: Callable[
        [AudioSource], tuple[Iterable[Mapping[str, Any]], str]
    ] = _load_hf_stream,
) -> dict[str, Any]:
    if max_per_source < 1 or max_total < 1:
        raise ValueError("collection limits must be positive")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / "audio_manifest.jsonl"
    records: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []
    observed_hashes: set[str] = set()
    collected_total = 0

    for source_index, source in enumerate(sources):
        if collected_total >= max_total:
            break
        effective_license = source.declared_license
        partition = license_partition(effective_license)
        source_limit = min(max_per_source, source.max_items or max_per_source)
        accepted = 0
        duplicates = 0
        rejected = 0
        scanned = 0
        errors: list[str] = []
        try:
            stream, observed_license = loader(source)
            effective_license = observed_license or source.declared_license
            partition = license_partition(effective_license)
        except Exception as exc:
            source_summaries.append(
                {
                    "repo_id": source.repo_id,
                    "config": source.config,
                    "split": source.split,
                    "revision": source.revision,
                    "category": source.category,
                    "license_partition": partition,
                    "observed_license": effective_license,
                    "scanned": 0,
                    "accepted": 0,
                    "duplicates": 0,
                    "rejected": 0,
                    "errors": [f"loader: {type(exc).__name__}: {exc}"],
                }
            )
            continue
        iterator = iter(stream)
        row_index = 0
        while accepted < source_limit and collected_total < max_total:
            try:
                row = next(iterator)
            except StopIteration:
                break
            except Exception as exc:
                rejected += 1
                errors.append(
                    f"iteration {row_index}: {type(exc).__name__}: {exc}"
                )
                break
            scanned += 1
            try:
                if source.audio_column not in row:
                    raise KeyError(f"missing audio column {source.audio_column!r}")
                payload, suffix, audio_metadata = _audio_bytes(row[source.audio_column])
                if not payload:
                    raise ValueError("audio payload is empty")
                digest = _sha256(payload)
                if digest in observed_hashes:
                    duplicates += 1
                    row_index += 1
                    continue
                observed_hashes.add(digest)
                directory = (
                    output
                    / partition
                    / source.category
                    / _slug(source.repo_id)
                    / _slug(source.config or "default")
                )
                directory.mkdir(parents=True, exist_ok=True)
                filename = f"{accepted:04d}-{digest[:16]}{suffix}"
                target = directory / filename
                target.write_bytes(payload)
                relative = target.relative_to(output).as_posix()
                row_metadata = {
                    str(key): _json_safe(value)
                    for key, value in row.items()
                    if str(key) != source.audio_column
                }
                record = {
                    "schema_version": "1.0",
                    "source_index": source_index,
                    "row_index": row_index,
                    "repo_id": source.repo_id,
                    "config": source.config,
                    "split": source.split,
                    "revision": source.revision,
                    "category": source.category,
                    "audio_column": source.audio_column,
                    "declared_license": source.declared_license,
                    "observed_license": effective_license,
                    "license_partition": partition,
                    "relative_path": relative,
                    "bytes": len(payload),
                    "sha256": digest,
                    "audio_metadata": audio_metadata,
                    "row_metadata": row_metadata,
                }
                records.append(record)
                accepted += 1
                collected_total += 1
            except Exception as exc:  # fail record, continue bounded source scan
                rejected += 1
                if len(errors) < 10:
                    errors.append(f"row {row_index}: {type(exc).__name__}: {exc}")
            row_index += 1
        source_summaries.append(
            {
                "repo_id": source.repo_id,
                "config": source.config,
                "split": source.split,
                "revision": source.revision,
                "category": source.category,
                "license_partition": partition,
                "observed_license": effective_license,
                "scanned": scanned,
                "accepted": accepted,
                "duplicates": duplicates,
                "rejected": rejected,
                "errors": errors,
            }
        )

    with manifest_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    with (output / "source_summary.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        fieldnames = [
            "repo_id",
            "config",
            "split",
            "revision",
            "category",
            "license_partition",
            "observed_license",
            "scanned",
            "accepted",
            "duplicates",
            "rejected",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(source_summaries)
    empty_sources = [
        row["repo_id"] for row in source_summaries if int(row["accepted"]) == 0
    ]
    counts_by_partition: dict[str, int] = {}
    counts_by_category: dict[str, int] = {}
    for record in records:
        partition = str(record["license_partition"])
        category = str(record["category"])
        counts_by_partition[partition] = counts_by_partition.get(partition, 0) + 1
        counts_by_category[category] = counts_by_category.get(category, 0) + 1
    summary = {
        "schema_version": "1.0",
        "source_count": len(source_summaries),
        "collected_total": len(records),
        "unique_audio_sha256": len(observed_hashes),
        "max_per_source": max_per_source,
        "max_total": max_total,
        "counts_by_license_partition": counts_by_partition,
        "counts_by_category": counts_by_category,
        "sources": source_summaries,
        "empty_sources": empty_sources,
        "manifest": manifest_path.name,
        "claim_boundary": (
            "bounded corpus acquisition with source and license provenance; "
            "license partitioning is not legal advice"
        ),
    }
    (output / "collection_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if empty_sources:
        raise RuntimeError(
            "audio collection produced zero accepted clips for: "
            + ", ".join(str(value) for value in empty_sources)
        )
    return summary


def _load_catalog(path: Path) -> list[AudioSource]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list) or not value:
        raise ValueError("audio source catalog must be a non-empty JSON array")
    return [AudioSource.from_mapping(item) for item in value]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-per-source", type=int, default=100)
    parser.add_argument("--max-total", type=int, default=600)
    args = parser.parse_args()
    sources = _load_catalog(args.catalog)
    summary = collect_audio_sources(
        sources,
        args.output,
        max_per_source=args.max_per_source,
        max_total=args.max_total,
    )
    print(
        "hf_audio_collection=completed "
        f"sources={summary['source_count']} "
        f"clips={summary['collected_total']} "
        f"partitions={summary['counts_by_license_partition']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
