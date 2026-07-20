"""Fail-closed CIFAR archive ingestion for real-data TNE AI evaluation.

The loader reads the original CIFAR Python tar archives directly. It does not
use labels to construct modality features. Exact image hashes are used for
within-source deduplication and train/test leakage removal before deterministic
stratified sampling.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import io
from pathlib import Path, PurePosixPath
import pickle
import tarfile
from typing import Any, Iterable

import numpy as np
import torch
from torch.nn import functional

from the_nothingness_effect.artificial_intelligence.shared.types import (
    AIObstructionError,
)

from .data import MultimodalBatch, MultimodalDataset


_MAX_MEMBER_BYTES = 256 * 1024 * 1024


class _RestrictedUnpickler(pickle.Unpickler):
    """Restricted unpickler sufficient for official CIFAR numpy payloads."""

    _ALLOWED: dict[tuple[str, str], object] = {
        ("_codecs", "encode"): __import__("_codecs").encode,
        ("numpy", "ndarray"): np.ndarray,
        ("numpy", "dtype"): np.dtype,
        ("numpy.core.multiarray", "_reconstruct"): np.core.multiarray._reconstruct,
        ("numpy._core.multiarray", "_reconstruct"): np.core.multiarray._reconstruct,
        ("numpy.core.multiarray", "scalar"): np.core.multiarray.scalar,
        ("numpy._core.multiarray", "scalar"): np.core.multiarray.scalar,
    }

    def find_class(self, module: str, name: str) -> object:
        value = self._ALLOWED.get((module, name))
        if value is None:
            raise pickle.UnpicklingError(
                f"CIFAR archive requested forbidden pickle global {module}.{name}"
            )
        return value


def _restricted_pickle_load(payload: bytes) -> dict[Any, Any]:
    value = _RestrictedUnpickler(io.BytesIO(payload), encoding="bytes").load()
    if not isinstance(value, dict):
        raise AIObstructionError("CIFAR pickle member must decode to a mapping")
    return value


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_member_name(name: str) -> str:
    candidate = PurePosixPath(name)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise AIObstructionError(f"unsafe archive member path: {name}")
    return str(candidate)


def _read_members(path: Path) -> dict[str, bytes]:
    members: dict[str, bytes] = {}
    try:
        with tarfile.open(path, mode="r:*") as archive:
            for member in archive.getmembers():
                if not member.isfile():
                    continue
                name = _safe_member_name(member.name)
                if member.size < 0 or member.size > _MAX_MEMBER_BYTES:
                    raise AIObstructionError(
                        f"CIFAR archive member exceeds safety bound: {name}"
                    )
                handle = archive.extractfile(member)
                if handle is None:
                    raise AIObstructionError(f"unable to read archive member: {name}")
                payload = handle.read(_MAX_MEMBER_BYTES + 1)
                if len(payload) != member.size or len(payload) > _MAX_MEMBER_BYTES:
                    raise AIObstructionError(f"archive member size mismatch: {name}")
                members[name] = payload
    except (tarfile.TarError, OSError) as exc:
        raise AIObstructionError(f"invalid CIFAR tar archive: {path}") from exc
    if not members:
        raise AIObstructionError("CIFAR archive contains no regular files")
    return members


def _find_member(members: dict[str, bytes], suffix: str) -> tuple[str, bytes]:
    matches = [(name, value) for name, value in members.items() if name.endswith(suffix)]
    if len(matches) != 1:
        raise AIObstructionError(
            f"expected exactly one CIFAR archive member ending in {suffix!r}"
        )
    return matches[0]


def _decode_names(values: Iterable[object]) -> tuple[str, ...]:
    names: list[str] = []
    for value in values:
        if isinstance(value, bytes):
            names.append(value.decode("utf-8", errors="strict"))
        else:
            names.append(str(value))
    if not names or len(set(names)) != len(names):
        raise AIObstructionError("CIFAR class names must be unique and non-empty")
    return tuple(names)


@dataclass(frozen=True)
class _ImageRecord:
    image: np.ndarray
    label: int
    digest: str
    member: str
    source_index: int


def _records_from_payload(
    member_name: str,
    payload: bytes,
    *,
    label_key: bytes,
) -> list[_ImageRecord]:
    decoded = _restricted_pickle_load(payload)
    data = decoded.get(b"data", decoded.get("data"))
    labels = decoded.get(label_key, decoded.get(label_key.decode("ascii")))
    if data is None or labels is None:
        raise AIObstructionError(f"CIFAR member lacks data or labels: {member_name}")
    array = np.asarray(data)
    label_array = np.asarray(labels, dtype=np.int64).reshape(-1)
    if array.ndim != 2 or array.shape[1] != 3072:
        raise AIObstructionError(f"CIFAR image matrix has invalid shape: {array.shape}")
    if array.shape[0] != label_array.shape[0]:
        raise AIObstructionError("CIFAR images and labels have unequal lengths")
    if not np.issubdtype(array.dtype, np.integer):
        raise AIObstructionError("CIFAR image matrix must contain integer bytes")
    array = np.asarray(array, dtype=np.uint8)
    records: list[_ImageRecord] = []
    for index, (flat, label) in enumerate(zip(array, label_array, strict=True)):
        raw = flat.tobytes(order="C")
        records.append(
            _ImageRecord(
                image=flat.reshape(3, 32, 32).copy(),
                label=int(label),
                digest=_sha256_bytes(raw),
                member=member_name,
                source_index=index,
            )
        )
    return records


def _deduplicate(records: Iterable[_ImageRecord]) -> tuple[list[_ImageRecord], int]:
    unique: list[_ImageRecord] = []
    observed: set[str] = set()
    duplicates = 0
    for record in records:
        if record.digest in observed:
            duplicates += 1
            continue
        observed.add(record.digest)
        unique.append(record)
    return unique, duplicates


def _image_modalities(record: _ImageRecord) -> dict[str, torch.Tensor]:
    vision = torch.from_numpy(record.image.copy()).to(torch.float32) / 255.0
    channel_mean = vision.mean(dim=(1, 2))
    channel_std = vision.std(dim=(1, 2), unbiased=False)
    color = torch.cat((channel_mean, channel_std), dim=0)
    gray = vision.mean(dim=0, keepdim=True)
    texture = functional.adaptive_avg_pool2d(gray.unsqueeze(0), (8, 8)).squeeze(0)
    spectrum = torch.abs(torch.fft.rfft2(gray.squeeze(0), norm="ortho"))
    spectrum = functional.adaptive_avg_pool2d(
        spectrum.unsqueeze(0).unsqueeze(0), (8, 8)
    ).squeeze(0)
    edge_x = torch.mean(torch.abs(gray[:, :, 1:] - gray[:, :, :-1]))
    edge_y = torch.mean(torch.abs(gray[:, 1:, :] - gray[:, :-1, :]))
    centre = gray[:, 8:24, 8:24].mean()
    border = torch.cat(
        (
            gray[:, :4, :].reshape(-1),
            gray[:, -4:, :].reshape(-1),
            gray[:, 4:-4, :4].reshape(-1),
            gray[:, 4:-4, -4:].reshape(-1),
        )
    ).mean()
    state = torch.stack(
        (
            vision.mean(),
            vision.std(unbiased=False),
            vision.min(),
            vision.max(),
            edge_x,
            edge_y,
            centre,
            border,
        )
    )
    return {
        "color": color,
        "spectrum": spectrum,
        "state": state,
        "texture": texture,
        "vision": vision,
    }


def _batch(records: list[_ImageRecord], class_map: dict[int, int]) -> MultimodalBatch:
    if len(records) < 2:
        raise AIObstructionError("each CIFAR split requires at least two observations")
    modality_rows: dict[str, list[torch.Tensor]] = {}
    labels: list[int] = []
    for record in records:
        for name, value in _image_modalities(record).items():
            modality_rows.setdefault(name, []).append(value)
        labels.append(class_map[record.label])
    return MultimodalBatch(
        {name: torch.stack(rows) for name, rows in modality_rows.items()},
        torch.tensor(labels, dtype=torch.long),
    ).validate()


def _split_digest(records: Iterable[_ImageRecord]) -> str:
    joined = "\n".join(sorted(record.digest for record in records)).encode("ascii")
    return _sha256_bytes(joined)


def _group_by_class(records: Iterable[_ImageRecord]) -> dict[int, list[_ImageRecord]]:
    grouped: dict[int, list[_ImageRecord]] = {}
    for record in records:
        grouped.setdefault(record.label, []).append(record)
    return grouped


def _deterministic_permutation(length: int, seed: int) -> list[int]:
    generator = torch.Generator().manual_seed(seed)
    return torch.randperm(length, generator=generator).tolist()


@dataclass(frozen=True)
class CIFARMultimodalLoad:
    dataset: MultimodalDataset
    report: dict[str, Any]


def load_cifar_multimodal_dataset(
    archive_path: str | Path,
    *,
    variant: str,
    seed: int = 0,
    samples_per_class: int = 24,
    max_classes: int | None = None,
) -> CIFARMultimodalLoad:
    """Load a bounded, deterministic, leakage-free CIFAR-10/100 dataset.

    ``samples_per_class`` is the total selected count per class. Sixty percent
    is drawn from the official training source, twenty percent is used for
    validation, and the remainder is drawn from the official test source.
    """

    path = Path(archive_path)
    normalized_variant = variant.strip().lower().replace("_", "-")
    if normalized_variant not in {"cifar-10", "cifar-100"}:
        raise ValueError("variant must be 'cifar-10' or 'cifar-100'")
    if samples_per_class < 10:
        raise ValueError("samples_per_class must be at least 10")
    if max_classes is not None and max_classes < 2:
        raise ValueError("max_classes must be at least two when specified")
    if not path.is_file():
        raise AIObstructionError(f"CIFAR archive does not exist: {path}")

    members = _read_members(path)
    source_member_hashes = {
        name: _sha256_bytes(payload) for name, payload in sorted(members.items())
    }
    if normalized_variant == "cifar-10":
        meta_name, meta_payload = _find_member(members, "/batches.meta")
        meta = _restricted_pickle_load(meta_payload)
        names = _decode_names(meta.get(b"label_names", meta.get("label_names", ())))
        train_members = sorted(
            (name, payload)
            for name, payload in members.items()
            if "/data_batch_" in name
        )
        test_members = [_find_member(members, "/test_batch")]
        label_key = b"labels"
    else:
        meta_name, meta_payload = _find_member(members, "/meta")
        meta = _restricted_pickle_load(meta_payload)
        names = _decode_names(
            meta.get(b"fine_label_names", meta.get("fine_label_names", ()))
        )
        train_members = [_find_member(members, "/train")]
        test_members = [_find_member(members, "/test")]
        label_key = b"fine_labels"

    if not train_members or not test_members:
        raise AIObstructionError("CIFAR archive lacks official train/test members")
    train_raw = [
        record
        for member_name, payload in train_members
        for record in _records_from_payload(member_name, payload, label_key=label_key)
    ]
    test_raw = [
        record
        for member_name, payload in test_members
        for record in _records_from_payload(member_name, payload, label_key=label_key)
    ]
    train_unique, train_duplicates = _deduplicate(train_raw)
    test_unique, test_duplicates = _deduplicate(test_raw)
    train_hashes = {record.digest for record in train_unique}
    leakage_records = [record for record in test_unique if record.digest in train_hashes]
    leakage_hashes = {record.digest for record in leakage_records}
    test_clean = [record for record in test_unique if record.digest not in train_hashes]

    train_by_class = _group_by_class(train_unique)
    test_by_class = _group_by_class(test_clean)
    available_classes = sorted(
        label for label in train_by_class if label in test_by_class and 0 <= label < len(names)
    )
    if max_classes is not None:
        available_classes = available_classes[:max_classes]
    if len(available_classes) < 2:
        raise AIObstructionError("fewer than two CIFAR classes remain after filtering")

    train_count = max(2, int(samples_per_class * 0.60))
    validation_count = max(2, int(samples_per_class * 0.20))
    test_count = samples_per_class - train_count - validation_count
    if test_count < 2:
        raise AIObstructionError("CIFAR split policy requires at least two test samples")

    selected_train: list[_ImageRecord] = []
    selected_validation: list[_ImageRecord] = []
    selected_test: list[_ImageRecord] = []
    for class_id in available_classes:
        train_candidates = train_by_class[class_id]
        test_candidates = test_by_class[class_id]
        if len(train_candidates) < train_count + validation_count:
            raise AIObstructionError(
                f"CIFAR class {class_id} lacks enough unique official train images"
            )
        if len(test_candidates) < test_count:
            raise AIObstructionError(
                f"CIFAR class {class_id} lacks enough leakage-free test images"
            )
        train_order = _deterministic_permutation(
            len(train_candidates), seed * 1009 + class_id * 37 + 11
        )
        test_order = _deterministic_permutation(
            len(test_candidates), seed * 1013 + class_id * 41 + 17
        )
        selected_train.extend(train_candidates[index] for index in train_order[:train_count])
        selected_validation.extend(
            train_candidates[index]
            for index in train_order[train_count : train_count + validation_count]
        )
        selected_test.extend(test_candidates[index] for index in test_order[:test_count])

    class_map = {class_id: index for index, class_id in enumerate(available_classes)}
    class_names = tuple(names[class_id] for class_id in available_classes)
    split_hash_sets = {
        "train": {record.digest for record in selected_train},
        "validation": {record.digest for record in selected_validation},
        "test": {record.digest for record in selected_test},
    }
    intersections = {
        "train_validation": len(split_hash_sets["train"] & split_hash_sets["validation"]),
        "train_test": len(split_hash_sets["train"] & split_hash_sets["test"]),
        "validation_test": len(
            split_hash_sets["validation"] & split_hash_sets["test"]
        ),
    }
    if any(intersections.values()):
        raise AIObstructionError("CIFAR selected splits contain exact byte leakage")

    dataset = MultimodalDataset(
        train=_batch(selected_train, class_map),
        validation=_batch(selected_validation, class_map),
        test=_batch(selected_test, class_map),
        class_names=class_names,
    )
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "dataset": normalized_variant,
        "archive_name": path.name,
        "archive_sha256": _sha256_file(path),
        "meta_member": meta_name,
        "source_member_sha256": source_member_hashes,
        "seed": int(seed),
        "samples_per_class": int(samples_per_class),
        "selected_original_class_ids": available_classes,
        "class_names": list(class_names),
        "modalities": sorted(dataset.train.modalities),
        "raw_train_records": len(train_raw),
        "raw_test_records": len(test_raw),
        "within_train_duplicates_removed": train_duplicates,
        "within_test_duplicates_removed": test_duplicates,
        "cross_source_leakage_removed": len(leakage_records),
        "cross_source_leakage_unique_hashes": len(leakage_hashes),
        "selected_split_counts": {
            "train": len(selected_train),
            "validation": len(selected_validation),
            "test": len(selected_test),
        },
        "selected_split_sha256": {
            "train": _split_digest(selected_train),
            "validation": _split_digest(selected_validation),
            "test": _split_digest(selected_test),
        },
        "selected_split_intersections": intersections,
        "leakage_free": not any(intersections.values()),
        "feature_policy": (
            "image-derived-only: color statistics, spatial texture, spectral "
            "magnitude, state statistics, and raw vision; labels are not features"
        ),
        "claim_boundary": (
            "bounded deterministic evaluation on public CIFAR archive bytes; "
            "not unrestricted real-world generalization or formal theorem proof"
        ),
    }
    return CIFARMultimodalLoad(dataset=dataset, report=report)
