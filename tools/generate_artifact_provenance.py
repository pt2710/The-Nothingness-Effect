"""Execute every implemented suite and build one aggregate provenance manifest."""

from __future__ import annotations

import argparse
import csv
from importlib import import_module
import json
from pathlib import Path
import shutil
import subprocess

from tools.consistency_catalog import ARTIFACT_SUITES


def _implemented_ids(matrix: Path) -> set[str]:
    with matrix.open(newline="", encoding="utf-8") as handle:
        return {row["complex_id"] for row in csv.DictReader(handle) if row["implementation_status"] == "implemented"}


def _commit() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()


def generate(output_root: Path, aggregate_path: Path, representative_dir: Path | None = None) -> dict[str, object]:
    output_root.mkdir(parents=True, exist_ok=True)
    for suite_name, module_name in ARTIFACT_SUITES:
        import_module(module_name).run_suite(output_root / suite_name, seed=0)
    manifest_paths = sorted(output_root.rglob("*_manifest.json"))
    manifests = [json.loads(path.read_text(encoding="utf-8")) for path in manifest_paths]
    output_token = output_root.as_posix()
    for manifest in manifests:
        manifest["regeneration_command"] = manifest["regeneration_command"].replace(output_token, "<output-root>")
    identifiers = [item["theorem_complex_id"] for item in manifests]
    expected = _implemented_ids(Path("docs/data/theorem_complex_implementation_matrix.csv"))
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("duplicate theorem-complex artifact manifests")
    if set(identifiers) != expected:
        raise ValueError(f"artifact coverage mismatch: missing={sorted(expected - set(identifiers))[:5]} extra={sorted(set(identifiers) - expected)[:5]}")
    if representative_dir is not None:
        representative_dir.mkdir(parents=True, exist_ok=True)
        for suite in ("qenn", "pgqenn", "soinets"):
            source = next((output_root / suite).glob("*.png"))
            shutil.copyfile(source, representative_dir / source.name)
    tables = sorted(output_root.rglob("*.csv"))
    figures = sorted(output_root.rglob("*.png"))
    animation_generators = sorted(Path("equations").glob("**/animation/animate_*.py"))
    payload = {
        "schema_version": "1.0",
        "repository_start_commit": "b97a2da379ff9fc503c4c43185030674f887b85c",
        "repository_result_commit": _commit(),
        "claim_boundary": "finite computational support; not a formal proof substitute",
        "summary": {
            "theorem_manifests": len(manifests),
            "generated_tables": len(tables),
            "generated_static_figures": len(figures),
            "animation_generators": len(animation_generators),
            "deterministic_seed": 0,
        },
        "local_artifact_policy": "Large/regenerable outputs remain outside Git; aggregate provenance and representative static figures are tracked.",
        "suites": [{"name": name, "module": module} for name, module in ARTIFACT_SUITES],
        "manifests": sorted(manifests, key=lambda item: item["theorem_complex_id"]),
    }
    aggregate_path.parent.mkdir(parents=True, exist_ok=True)
    aggregate_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--aggregate", type=Path, default=Path("docs/data/artifact_provenance_manifest.json"))
    parser.add_argument("--representative-dir", type=Path)
    arguments = parser.parse_args()
    result = generate(arguments.output_root.resolve(), arguments.aggregate.resolve(), arguments.representative_dir)
    print(json.dumps(result["summary"], sort_keys=True))
