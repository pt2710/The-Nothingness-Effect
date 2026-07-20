from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.package_theorem_diagnostic_artifacts import package


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_package_records_relative_paths_and_exact_bytes(tmp_path: Path):
    source = tmp_path / "source"
    destination = tmp_path / "package"
    (source / "complex_a").mkdir(parents=True)
    (source / "complex_b").mkdir(parents=True)
    first = source / "complex_a" / "metrics.json"
    second = source / "complex_b" / "trace.npz"
    first.write_text('{"residual": 0.0}\n', encoding="utf-8")
    second.write_bytes(b"finite-trace-bytes")

    report = package(source, destination)

    assert report["file_count"] == 2
    assert report["total_bytes"] == first.stat().st_size + second.stat().st_size
    assert report["paths_are_relative"] is True
    assert report["payload_files_embedded"] is False
    records = {item["path"]: item for item in report["files"]}
    assert set(records) == {
        "complex_a/metrics.json",
        "complex_b/trace.npz",
    }
    assert records["complex_a/metrics.json"]["sha256"] == _digest(first)
    assert records["complex_b/trace.npz"]["sha256"] == _digest(second)
    assert all(not Path(path).is_absolute() for path in records)

    manifest = destination / "theorem_diagnostic_file_manifest.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["tree_sha256"] == report["tree_sha256"]
    assert payload["suffix_counts"] == {".json": 1, ".npz": 1}
    assert (destination / "SHA256SUMS").is_file()
    assert (destination / "README.md").is_file()
    checksum_record = (
        destination / "theorem_diagnostic_file_manifest.json.sha256"
    ).read_text(encoding="utf-8")
    assert checksum_record.startswith(_digest(manifest))


def test_package_is_deterministic_for_unchanged_tree(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.csv").write_text("x,y\n1,2\n", encoding="utf-8")
    (source / "b.png").write_bytes(b"diagnostic-png-placeholder")

    first = package(source, tmp_path / "first")
    second = package(source, tmp_path / "second")

    assert first["tree_sha256"] == second["tree_sha256"]
    assert first["files"] == second["files"]
    assert (
        tmp_path / "first" / "theorem_diagnostic_file_manifest.json"
    ).read_bytes() == (
        tmp_path / "second" / "theorem_diagnostic_file_manifest.json"
    ).read_bytes()


def test_package_rejects_empty_tree_and_nested_output(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    with pytest.raises(RuntimeError, match="contains no files"):
        package(source, tmp_path / "output")

    (source / "file.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="outside the input tree"):
        package(source, source / "package")


def test_package_rejects_symlinks(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    target = tmp_path / "target.txt"
    target.write_text("not part of the tree", encoding="utf-8")
    link = source / "link.txt"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlinks are not supported on this platform")

    with pytest.raises(RuntimeError, match="symlink is not permitted"):
        package(source, tmp_path / "output")
