from __future__ import annotations

import io
import json
import pickle
import tarfile

import numpy as np

from tools.collect_hf_audio_datasets import (
    AudioSource,
    collect_audio_sources,
    license_partition,
)
from the_nothingness_effect.artificial_intelligence.multimodal.real_data import (
    load_cifar_multimodal_dataset,
)


def _tar_member(archive: tarfile.TarFile, name: str, value: object) -> None:
    payload = pickle.dumps(value, protocol=2)
    info = tarfile.TarInfo(name)
    info.size = len(payload)
    archive.addfile(info, io.BytesIO(payload))


def _images(labels: list[int], *, offset: int) -> np.ndarray:
    rows = []
    for index, label in enumerate(labels):
        value = (offset + label * 41 + index * 7) % 256
        row = np.full((3072,), value, dtype=np.uint8)
        row[index % 3072] = (value + 13) % 256
        rows.append(row)
    return np.stack(rows)


def _build_cifar10(path) -> None:
    train_labels = [0] * 10 + [1] * 10
    test_labels = [0] * 4 + [1] * 4
    train = _images(train_labels, offset=3)
    test = _images(test_labels, offset=131)
    test[0] = train[0]
    with tarfile.open(path, "w:gz") as archive:
        _tar_member(
            archive,
            "cifar-10-batches-py/batches.meta",
            {b"label_names": [b"zero", b"one"]},
        )
        _tar_member(
            archive,
            "cifar-10-batches-py/data_batch_1",
            {b"data": train, b"labels": train_labels},
        )
        _tar_member(
            archive,
            "cifar-10-batches-py/test_batch",
            {b"data": test, b"labels": test_labels},
        )


def _build_cifar100(path) -> None:
    train_labels = [0] * 10 + [1] * 10
    test_labels = [0] * 4 + [1] * 4
    with tarfile.open(path, "w:gz") as archive:
        _tar_member(
            archive,
            "cifar-100-python/meta",
            {b"fine_label_names": [b"alpha", b"beta"]},
        )
        _tar_member(
            archive,
            "cifar-100-python/train",
            {b"data": _images(train_labels, offset=19), b"fine_labels": train_labels},
        )
        _tar_member(
            archive,
            "cifar-100-python/test",
            {b"data": _images(test_labels, offset=173), b"fine_labels": test_labels},
        )


def test_cifar10_loader_is_deterministic_deduplicated_and_leakage_free(tmp_path):
    archive = tmp_path / "cifar-10-python.tar.gz"
    _build_cifar10(archive)
    first = load_cifar_multimodal_dataset(
        archive,
        variant="cifar-10",
        seed=7,
        samples_per_class=10,
    )
    second = load_cifar_multimodal_dataset(
        archive,
        variant="cifar-10",
        seed=7,
        samples_per_class=10,
    )
    assert first.dataset.class_names == ("zero", "one")
    assert set(first.dataset.train.modalities) == {
        "color",
        "spectrum",
        "state",
        "texture",
        "vision",
    }
    assert first.report["cross_source_leakage_removed"] == 1
    assert first.report["leakage_free"] is True
    assert first.report["selected_split_intersections"] == {
        "train_validation": 0,
        "train_test": 0,
        "validation_test": 0,
    }
    assert first.report["selected_split_sha256"] == second.report[
        "selected_split_sha256"
    ]
    assert first.dataset.train.labels.shape[0] == 12
    assert first.dataset.validation.labels.shape[0] == 4
    assert first.dataset.test.labels.shape[0] == 4


def test_cifar100_fine_label_loader(tmp_path):
    archive = tmp_path / "cifar-100-python.tar.gz"
    _build_cifar100(archive)
    loaded = load_cifar_multimodal_dataset(
        archive,
        variant="cifar-100",
        seed=3,
        samples_per_class=10,
        max_classes=2,
    )
    assert loaded.dataset.class_names == ("alpha", "beta")
    assert loaded.report["dataset"] == "cifar-100"
    assert loaded.report["leakage_free"] is True


def test_hf_audio_collector_partitions_licenses_and_deduplicates(tmp_path):
    sources = [
        AudioSource("example/speech", "speech", declared_license="cc-by-4.0"),
        AudioSource("example/music", "music", declared_license="unknown"),
        AudioSource(
            "example/effects",
            "sound_effects",
            declared_license="cc-by-nc-2.0",
        ),
    ]

    def loader(source):
        payload = (source.category + "-clip").encode()
        return (
            [
                {"audio": {"bytes": payload, "path": "clip.wav"}, "label": 1},
                {"audio": {"bytes": payload, "path": "duplicate.wav"}, "label": 1},
            ],
            source.declared_license,
        )

    summary = collect_audio_sources(
        sources,
        tmp_path / "audio",
        max_per_source=2,
        max_total=6,
        loader=loader,
    )
    assert summary["collected_total"] == 3
    assert summary["unique_audio_sha256"] == 3
    assert summary["counts_by_license_partition"] == {
        "noncommercial": 1,
        "permissive": 1,
        "unknown_or_mixed": 1,
    }
    manifest = [
        json.loads(line)
        for line in (tmp_path / "audio" / "audio_manifest.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert len(manifest) == 3
    assert all(
        (tmp_path / "audio" / row["relative_path"]).is_file() for row in manifest
    )
    assert license_partition("CC-BY-4.0") == "permissive"
    assert license_partition("CC-BY-NC-2.0") == "noncommercial"
    assert license_partition("custom") == "unknown_or_mixed"
