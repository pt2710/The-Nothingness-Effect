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


def _producer_local_files() -> list[Path]:
    roots = [
        Path("equations/artificial_intelligence"),
        *(Path("equations") / name for name in (
            "cosmological_spark_dynamics",
            "dtqc",
            "elastic_dubler_interferometry",
            "elastic_pi_norm",
            "mathematical_closure",
            "parity_dfi",
        )),
        Path("equations/black_hole_dynamics/hawking"),
    ]
    allowed_suffixes = {".py", ".json", ".csv", ".png", ".gif", ".wav", ".md"}
    return sorted(
        {
            path
            for root in roots
            if root.is_dir()
            for path in root.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix.lower() in allowed_suffixes
        }
    )


def _animation_generators() -> list[Path]:
    candidates = {
        *Path("equations").glob("**/animation/animate_*.py"),
        *Path("equations").glob("**/simulation/run_evidence.py"),
        *Path("equations").glob("**/test/test_evidence.py"),
        *Path("equations/artificial_intelligence").glob("**/simulation/run_simulation.py"),
        *Path("equations/artificial_intelligence").glob("**/simulation/run_all_capabilities.py"),
    }
    return sorted(candidates)


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
    producer_files = _producer_local_files()
    producer_manifests = [path for path in producer_files if path.name.endswith("_manifest.json")]
    producer_tables = [path for path in producer_files if path.suffix == ".csv"]
    producer_figures = [path for path in producer_files if path.suffix == ".png"]
    producer_animations = [path for path in producer_files if path.suffix == ".gif"]
    producer_audio = [path for path in producer_files if path.suffix == ".wav"]
    animation_generators = _animation_generators()
    payload = {
        "schema_version": "1.0",
        "repository_start_commit": "b97a2da379ff9fc503c4c43185030674f887b85c",
        "repository_result_commit": _commit(),
        "claim_boundary": "finite computational support; not a formal proof substitute",
        "summary": {
            "theorem_manifests": len(manifests),
            "generated_tables": len(tables) + len(producer_tables),
            "generated_static_figures": len(figures) + len(producer_figures),
            "producer_local_manifests": len(producer_manifests),
            "producer_local_animations": len(producer_animations),
            "producer_local_audio_files": len(producer_audio),
            "animation_generators": len(animation_generators),
            "deterministic_seed": 0,
        },
        "local_artifact_policy": "Large frame dumps and videos remain outside Git; compact producer-local metrics, manifests, representative figures, audio, and selected GIF evidence are tracked.",
        "suites": [{"name": name, "module": module} for name, module in ARTIFACT_SUITES],
        "producer_local_artifacts": [path.as_posix() for path in producer_files],
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
