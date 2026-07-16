"""Execute every implemented suite and build one aggregate provenance manifest."""

from __future__ import annotations

import argparse
import csv
from importlib import import_module
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np

if __package__:
    from tools.consistency_catalog import ARTIFACT_SUITES
else:
    from consistency_catalog import ARTIFACT_SUITES

from the_nothingness_effect._runtime.artifacts.io import save_csv
from the_nothingness_effect._runtime.theorem_complex_runtime.artifacts import write_artifact_manifest
from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import active_contracts
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import (
    AdditiveDerivationInput,
    SpatialClosureInput,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import build_manifest
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ComplexLevel, SimulationResult


def _implemented_ids(matrix: Path) -> set[str]:
    with matrix.open(newline="", encoding="utf-8") as handle:
        return {row["complex_id"] for row in csv.DictReader(handle) if row["implementation_status"] == "implemented"}


def _commit() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()


def _producer_local_files() -> list[Path]:
    roots = [Path("the_nothingness_effect")]
    allowed_suffixes = {".py", ".json", ".csv", ".png", ".gif", ".wav", ".md"}
    return sorted(
        {
            path
            for root in roots
            if root.is_dir()
            for path in root.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and "artifacts" in path.parts
            and path.suffix.lower() in allowed_suffixes
        }
    )


def _animation_generators() -> list[Path]:
    candidates = {
        *Path("the_nothingness_effect").glob("**/animation/animate_*.py"),
        *Path("the_nothingness_effect").glob("**/simulation/run_evidence.py"),
        *Path("the_nothingness_effect").glob("**/test/test_evidence.py"),
        *Path("the_nothingness_effect/artificial_intelligence").glob("**/simulation/run_simulation.py"),
        *Path("the_nothingness_effect/artificial_intelligence").glob("**/simulation/run_all_capabilities.py"),
        *Path("the_nothingness_effect/artificial_intelligence").glob("**/simulation/run_pipeline.py"),
        *Path("the_nothingness_effect/artificial_intelligence").glob("**/test/run_pipeline.py"),
    }
    return sorted(candidates)


def _generate_uncovered_contracts(output_root: Path, covered: set[str], expected: set[str]) -> None:
    """Generate deterministic residual/source-removal evidence for derived laws."""

    catalog = {str(contract.complex_id): contract for contract in active_contracts()}
    destination = output_root / "appendix_derived"
    destination.mkdir(parents=True, exist_ok=True)
    for identifier in sorted(expected - covered):
        contract = catalog[identifier]
        fields = {
            str(source_id): np.full((6, 4), float(index + 1))
            for index, source_id in enumerate(contract.source_ids)
        }
        if contract.level is ComplexLevel.B:
            value = AdditiveDerivationInput(fields)
        elif contract.level is ComplexLevel.C:
            value = SpatialClosureInput(fields)
        else:
            raise ValueError(f"uncovered non-derived contract: {identifier}")
        evaluation = evaluate_contract(contract, value)
        removals = [check(value) for check in contract.source_removal_checks]
        residual = () if evaluation.residual is None else evaluation.residual.vector
        table = save_csv(
            destination / f"{identifier.replace('::', '__')}_source_removal.csv",
            [
                {
                    "theorem_complex_id": identifier,
                    "source_id": str(item.source_id),
                    "necessity_residual": item.necessity_residual,
                    "necessary": item.necessary,
                    "closure_status": evaluation.status.value,
                }
                for item in removals
            ],
        )
        simulation = SimulationResult(
            contract.complex_id,
            evaluation.status,
            {"fixture": "deterministic-derived-source-fields-v1"},
            0,
            {"absolute": 1e-10},
            tuple(float(item) for item in residual),
            (table.name,),
            {"exact_semantics": contract.exact_semantics, "source_removal_count": len(removals)},
        )
        write_artifact_manifest(
            destination / f"{identifier.replace('::', '__')}_manifest.json",
            build_manifest(
                simulation,
                appendix_filename=contract.appendix,
                appendix_source_sha256=contract.appendix_source_sha256,
                repository_start_commit="b97a2da379ff9fc503c4c43185030674f887b85c",
                repository_result_commit=_commit(),
                regeneration_command=(
                    "python tools/generate_artifact_provenance.py "
                    f"--output-root {output_root.as_posix()}"
                ),
            ),
        )


def generate(output_root: Path, aggregate_path: Path, representative_dir: Path | None = None) -> dict[str, object]:
    output_root.mkdir(parents=True, exist_ok=True)
    for suite_name, module_name in ARTIFACT_SUITES:
        import_module(module_name).run_suite(output_root / suite_name, seed=0)
    manifest_paths = sorted(output_root.rglob("*_manifest.json"))
    manifests = [json.loads(path.read_text(encoding="utf-8")) for path in manifest_paths]
    expected = _implemented_ids(Path("docs/data/theorem_complex_implementation_matrix.csv"))
    _generate_uncovered_contracts(
        output_root,
        {item["theorem_complex_id"] for item in manifests},
        expected,
    )
    manifest_paths = sorted(output_root.rglob("*_manifest.json"))
    manifests = [json.loads(path.read_text(encoding="utf-8")) for path in manifest_paths]
    output_token = output_root.as_posix()
    for manifest in manifests:
        manifest["regeneration_command"] = manifest["regeneration_command"].replace(output_token, "<output-root>")
    identifiers = [item["theorem_complex_id"] for item in manifests]
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
