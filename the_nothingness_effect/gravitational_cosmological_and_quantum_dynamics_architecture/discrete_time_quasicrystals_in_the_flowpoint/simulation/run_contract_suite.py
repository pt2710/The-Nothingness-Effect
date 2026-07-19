from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

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

# The full visual/data inventory remains in the verified legacy_faithful
# subdirectory. The root compatibility figure is explicitly rebound so the
# top-level artifact tree no longer exposes the stale generic FieldLaw plot.
PROMOTED_ARTIFACTS = {
    "dtqc_legacy_summary.png": ROOT_COMPATIBILITY_FIGURE,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _clear_root_files(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for existing in output.iterdir():
        if existing.is_file():
            existing.unlink()


def _bind_full_source_faithful_tree(output: Path, legacy_output: Path) -> dict[str, object]:
    shutil.copyfile(
        legacy_output / STATIC_FILES[0],
        output / ROOT_COMPATIBILITY_FIGURE,
    )

    legacy_manifest = json.loads((legacy_output / LEGACY_MANIFEST_FILE).read_text(encoding="utf-8"))
    legacy_checksums = json.loads((legacy_output / LEGACY_CHECKSUM_FILE).read_text(encoding="utf-8"))
    legacy_checksum_scope = dict(legacy_checksums["files"])
    legacy_checksum_scope[LEGACY_CHECKSUM_FILE] = _sha256(legacy_output / LEGACY_CHECKSUM_FILE)

    theorem_manifests = sorted(path.name for path in output.glob("*_manifest.json"))
    root_payload_before_metadata = sorted(path.name for path in output.iterdir() if path.is_file())
    root_inventory = sorted(
        [*root_payload_before_metadata, ROOT_METADATA_FILE, ROOT_CHECKSUM_FILE]
    )
    legacy_inventory = sorted(path.name for path in legacy_output.iterdir() if path.is_file())
    metadata = {
        "schema_version": "3.0",
        "suite": "dtqc_full_source_faithful_artifact_tree",
        "pipeline_partition": {
            "theorem_runtime": "existing Fibonacci/Pisot/Floquet and typed contract runtime retained",
            "visual_runtime": "legacy source-faithful decagonal/DFI/Elastic-pi/Flowpoint pipeline",
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

    # The theorem manifests already carry their own provenance checks and embed
    # the producing Git commit. The recursive stable checksum scope covers the
    # root numerical/visual payload plus every file in legacy_faithful.
    root_stable_payload = (
        "dtqc_contract_metrics.csv",
        ROOT_COMPATIBILITY_FIGURE,
        ROOT_METADATA_FILE,
    )
    checksums = {
        "schema_version": "3.0",
        "algorithm": "sha256",
        "scope": "stable recursive DTQC source-faithful tree; theorem manifests verified separately",
        "root_files": {name: _sha256(output / name) for name in root_stable_payload},
        "legacy_faithful_files": legacy_checksum_scope,
    }
    checksum_path = output / ROOT_CHECKSUM_FILE
    checksum_path.write_text(json.dumps(checksums, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    final_root_inventory = sorted(path.name for path in output.iterdir() if path.is_file())
    if final_root_inventory != root_inventory:
        raise RuntimeError(
            "unexpected root DTQC artifact inventory: "
            f"actual={final_root_inventory}, expected={root_inventory}"
        )
    final_legacy_inventory = sorted(path.name for path in legacy_output.iterdir() if path.is_file())
    if final_legacy_inventory != legacy_inventory:
        raise RuntimeError(
            "unexpected legacy DTQC artifact inventory: "
            f"actual={final_legacy_inventory}, expected={legacy_inventory}"
        )

    return {
        "metadata": metadata_path,
        "checksums": checksum_path,
        "root_files": [output / name for name in final_root_inventory],
        "legacy_files": [legacy_output / name for name in final_legacy_inventory],
    }


def run_suite(
    output_dir: str | Path,
    *,
    seed: int = 1,
    grid_size: int = 240,
    time_steps: int = 48,
    point_count: int = 8000,
    sphere_resolution: int = 64,
):
    output = Path(output_dir)
    _clear_root_files(output)

    result = dict(_run("dtqc", output, seed=seed))
    legacy_result = run_legacy_faithful_suite(
        output / "legacy_faithful",
        seed=seed,
        grid_size=grid_size,
        time_steps=time_steps,
        point_count=point_count,
        sphere_resolution=sphere_resolution,
    )
    result["legacy_faithful"] = legacy_result
    result["source_faithful_tree"] = _bind_full_source_faithful_tree(
        output,
        Path(legacy_result["output_dir"]),
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--grid-size", type=int, default=240)
    parser.add_argument("--time-steps", type=int, default=48)
    parser.add_argument("--point-count", type=int, default=8000)
    parser.add_argument("--sphere-resolution", type=int, default=64)
    args = parser.parse_args()
    print(
        run_suite(
            args.output,
            seed=args.seed,
            grid_size=args.grid_size,
            time_steps=args.time_steps,
            point_count=args.point_count,
            sphere_resolution=args.sphere_resolution,
        )
    )
