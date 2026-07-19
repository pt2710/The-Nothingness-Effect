from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import git_commit
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_artifacts import (
    run_suite as _run,
)

from .run_legacy_faithful_suite import (
    CHECKSUM_FILE as LEGACY_CHECKSUM_FILE,
    MANIFEST_FILE as LEGACY_MANIFEST_FILE,
    STATIC_FILES,
    run_legacy_faithful_suite,
)


ROOT_METADATA_FILE = "dtqc_artifact_metadata.json"
ROOT_CHECKSUM_FILE = "dtqc_artifact_checksums.json"
ROOT_COMPATIBILITY_FIGURE = "dtqc_spatial_closure.png"
ARTIFACT_POLICY_FILE = "artifact_policy.json"
MODULE_MANIFEST_FILE = "manifest.json"
CANONICAL_REGENERATION_COMMAND = (
    "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture."
    "discrete_time_quasicrystals_in_the_flowpoint.simulation.run_evidence"
)

PROMOTED_ARTIFACTS = {
    "legacy_faithful/dtqc_legacy_summary.png": ROOT_COMPATIBILITY_FIGURE,
}

PRODUCTION_LEGACY_CONFIG = {
    "seed": 1,
    "grid_size": 240,
    "time_steps": 48,
    "point_count": 8000,
    "sphere_resolution": 64,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_artifact_output(output_dir: str | Path) -> Path:
    """Remove every producer-owned root artifact before a full regeneration."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for existing in output.iterdir():
        if existing.is_file():
            existing.unlink()
    return output


def _normalize_root_manifests(output: Path, generation_source_commit: str) -> None:
    """Remove output-path and checkout-commit volatility from root JSON evidence."""

    for path in sorted(output.glob("*.json")):
        if path.name in {ROOT_METADATA_FILE, ROOT_CHECKSUM_FILE, ARTIFACT_POLICY_FILE}:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        changed = False
        if "repository_result_commit" in payload:
            payload["repository_result_commit"] = generation_source_commit
            changed = True
        if "regeneration_command" in payload:
            payload["regeneration_command"] = CANONICAL_REGENERATION_COMMAND
            changed = True
        if changed:
            path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_artifact_policy(output: Path) -> Path:
    path = output / ARTIFACT_POLICY_FILE
    path.write_text(
        json.dumps(
            {
                "claim_boundary": "finite computational support; not a formal proof substitute",
                "large_binary_policy": "tracked deterministic release artifacts plus CI regeneration evidence",
                "mode": "simulation",
                "module": (
                    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
                    "discrete_time_quasicrystals_in_the_flowpoint"
                ),
                "policy": "all tracked files in this artifact tree are producer-owned and regenerated together",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _write_module_manifest(output: Path, generation_source_commit: str) -> Path:
    from ...contract_runtime import APPENDIX, APPENDIX_SHA256
    from ..contracts import contracts

    identifiers = [str(contract.complex_id) for contract in contracts()]
    generated_files = sorted(
        path.name
        for path in output.iterdir()
        if path.is_file() and path.name not in {MODULE_MANIFEST_FILE, ROOT_METADATA_FILE, ROOT_CHECKSUM_FILE}
    )
    path = output / MODULE_MANIFEST_FILE
    path.write_text(
        json.dumps(
            {
                "appendix_filename": APPENDIX,
                "appendix_source_sha256": APPENDIX_SHA256,
                "appendix_sources": [{"filename": APPENDIX, "sha256": APPENDIX_SHA256}],
                "claim_boundary": "finite computational support; not a formal proof substitute",
                "closure_status": "mixed_exact_and_finite_runtime_evidence",
                "exact_or_approximate": "typed_runtime_plus_source_faithful_visualization",
                "generated_files": generated_files,
                "invariant_results": {
                    "tracked_root_files_regenerated": True,
                    "legacy_visual_source_bound": True,
                    "fibonacci_pisot_floquet_runtime_preserved": True,
                },
                "module": (
                    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
                    "discrete_time_quasicrystals_in_the_flowpoint"
                ),
                "numeric_tolerances": {"absolute": 1e-10},
                "parameters": {
                    "theorem_contract_seed": 0,
                    "legacy_visual_seed": PRODUCTION_LEGACY_CONFIG["seed"],
                    "legacy_grid_size": PRODUCTION_LEGACY_CONFIG["grid_size"],
                    "legacy_time_steps": PRODUCTION_LEGACY_CONFIG["time_steps"],
                },
                "regeneration_command": CANONICAL_REGENERATION_COMMAND,
                "repository_result_commit": generation_source_commit,
                "repository_start_commit": "b97a2da379ff9fc503c4c43185030674f887b85c",
                "schema_version": "2.0",
                "seed": 0,
                "theorem_complex_id": "module_inventory",
                "theorem_complex_ids": identifiers,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def run_suite(
    output_dir: str | Path,
    *,
    seed: int = 0,
    legacy_seed: int = 1,
    grid_size: int = 240,
    time_steps: int = 48,
    point_count: int = 8000,
    sphere_resolution: int = 64,
):
    """Generate typed contract artifacts and the independent legacy-faithful suite.

    The complete root tree is finalized by :func:`finalize_artifact_tree` after
    the canonical simulation visualizer has added its outputs.
    """

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    result = dict(_run("dtqc", output, seed=seed))
    legacy_result = run_legacy_faithful_suite(
        output / "legacy_faithful",
        seed=legacy_seed,
        grid_size=grid_size,
        time_steps=time_steps,
        point_count=point_count,
        sphere_resolution=sphere_resolution,
    )
    shutil.copyfile(
        Path(legacy_result["output_dir"]) / STATIC_FILES[0],
        output / ROOT_COMPATIBILITY_FIGURE,
    )
    result["legacy_faithful"] = legacy_result
    return result


def finalize_artifact_tree(
    output_dir: str | Path,
    *,
    generation_source_commit: str | None = None,
) -> dict[str, object]:
    """Finalize metadata, recursive inventory, and byte checksums after all generators."""

    output = Path(output_dir)
    legacy_output = output / "legacy_faithful"
    generation_commit = generation_source_commit or git_commit(Path(__file__).resolve().parents[6])

    _normalize_root_manifests(output, generation_commit)
    _write_artifact_policy(output)
    _write_module_manifest(output, generation_commit)

    legacy_manifest = json.loads((legacy_output / LEGACY_MANIFEST_FILE).read_text(encoding="utf-8"))
    legacy_checksums = json.loads((legacy_output / LEGACY_CHECKSUM_FILE).read_text(encoding="utf-8"))
    legacy_checksum_scope = dict(legacy_checksums["files"])
    legacy_checksum_scope[LEGACY_CHECKSUM_FILE] = _sha256(legacy_output / LEGACY_CHECKSUM_FILE)

    theorem_manifests = sorted(
        path.name
        for path in output.glob("*_manifest.json")
        if path.name not in {"dtqc_simulation_evidence_manifest.json", "dtqc_simulation_visualization_manifest.json"}
    )
    root_payload_before_metadata = sorted(path.name for path in output.iterdir() if path.is_file())
    root_inventory = sorted([*root_payload_before_metadata, ROOT_METADATA_FILE, ROOT_CHECKSUM_FILE])
    legacy_inventory = sorted(path.name for path in legacy_output.iterdir() if path.is_file())
    metadata = {
        "schema_version": "4.0",
        "suite": "dtqc_complete_recursive_artifact_pipeline",
        "generation_source_commit": generation_commit,
        "generator_inventory": {
            "typed_contracts": (
                "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture."
                "contract_artifacts.run_suite"
            ),
            "canonical_simulation_visuals": (
                "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture."
                "discrete_time_quasicrystals_in_the_flowpoint.visualization.run_dtqc_evidence"
            ),
            "legacy_source_faithful_visuals": (
                "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture."
                "discrete_time_quasicrystals_in_the_flowpoint.simulation.run_legacy_faithful_suite"
            ),
            "full_orchestrator": (
                "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture."
                "discrete_time_quasicrystals_in_the_flowpoint.simulation.run_evidence"
            ),
        },
        "pipeline_partition": {
            "theorem_runtime": "Fibonacci/Pisot/Floquet and typed theorem-contract runtime retained",
            "canonical_visual_runtime": "finite canonical DTQC source-response projection and phase clock",
            "legacy_visual_runtime": "legacy source-faithful decagonal/DFI/Elastic-pi/Flowpoint pipeline",
            "compatibility_figure": (
                "dtqc_spatial_closure.png is rebound to legacy_faithful/dtqc_legacy_summary.png; "
                "the stale generic FieldLaw line plot is not retained"
            ),
        },
        "source_audit": legacy_manifest["source_audit"],
        "mathematical_bindings": legacy_manifest["mathematical_bindings"],
        "source_removal": legacy_manifest["source_removal"],
        "production_configuration": {
            key: legacy_manifest[key]
            for key in (
                "seed",
                "grid_size",
                "time_steps",
                "legacy_frame_stride",
                "represented_legacy_frames",
                "point_count",
                "radial_channels",
                "entropy_scale",
            )
        },
        "promoted_artifacts": PROMOTED_ARTIFACTS,
        "theorem_manifests": theorem_manifests,
        "root_inventory": root_inventory,
        "legacy_faithful_inventory": legacy_inventory,
        "claim_boundary": legacy_manifest["claim_boundary"],
    }
    metadata_path = output / ROOT_METADATA_FILE
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    root_checksum_files = sorted(
        path.name for path in output.iterdir() if path.is_file() and path.name != ROOT_CHECKSUM_FILE
    )
    checksums = {
        "schema_version": "4.0",
        "algorithm": "sha256",
        "scope": "all tracked DTQC root payloads plus the complete legacy_faithful subdirectory",
        "generation_source_commit": generation_commit,
        "root_files": {name: _sha256(output / name) for name in root_checksum_files},
        "legacy_faithful_files": legacy_checksum_scope,
    }
    checksum_path = output / ROOT_CHECKSUM_FILE
    checksum_path.write_text(json.dumps(checksums, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    final_root_inventory = sorted(path.name for path in output.iterdir() if path.is_file())
    final_legacy_inventory = sorted(path.name for path in legacy_output.iterdir() if path.is_file())
    if final_root_inventory != root_inventory:
        raise RuntimeError(
            f"unexpected root DTQC artifact inventory: actual={final_root_inventory}, expected={root_inventory}"
        )
    if final_legacy_inventory != legacy_inventory:
        raise RuntimeError(
            f"unexpected legacy DTQC artifact inventory: actual={final_legacy_inventory}, expected={legacy_inventory}"
        )

    return {
        "metadata": metadata_path,
        "checksums": checksum_path,
        "root_files": [output / name for name in final_root_inventory],
        "legacy_files": [legacy_output / name for name in final_legacy_inventory],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--generation-source-commit")
    args = parser.parse_args()
    output = prepare_artifact_output(args.output)
    result = run_suite(output, seed=args.seed)
    result["artifact_tree"] = finalize_artifact_tree(
        output,
        generation_source_commit=args.generation_source_commit,
    )
    print(result)


if __name__ == "__main__":
    main()
