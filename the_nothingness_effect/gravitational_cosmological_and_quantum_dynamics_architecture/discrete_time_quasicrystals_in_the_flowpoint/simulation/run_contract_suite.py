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
    ANIMATED_FILES,
    DATA_FILES,
    MANIFEST_FILE as LEGACY_MANIFEST_FILE,
    STATIC_FILES,
    run_legacy_faithful_suite,
)


ROOT_METADATA_FILE = "dtqc_artifact_metadata.json"
ROOT_CHECKSUM_FILE = "dtqc_artifact_checksums.json"
ROOT_COMPATIBILITY_FIGURE = "dtqc_spatial_closure.png"

PROMOTED_ARTIFACTS = {
    "dtqc_legacy_summary.png": "dtqc_source_faithful_summary.png",
    "dtqc_legacy_quasicrystal_contour.png": "dtqc_quasicrystal_contour.png",
    "dtqc_legacy_diffraction_fft.png": "dtqc_diffraction_fft.png",
    "dtqc_legacy_dfi_surface.png": "dtqc_dfi_surface.png",
    "dtqc_legacy_elastic_pi_surface.png": "dtqc_elastic_pi_surface.png",
    "dtqc_legacy_wavelet_ridges.png": "dtqc_wavelet_ridges.png",
    "dtqc_legacy_flowpoint_flicker.gif": "dtqc_flowpoint_flicker.gif",
    "dtqc_legacy_5d_scatter.gif": "dtqc_5d_scatter.gif",
    "dtqc_legacy_elastic_pi_sphere.gif": "dtqc_elastic_pi_sphere.gif",
    "dtqc_legacy_elastic_pi_half_sphere.gif": "dtqc_elastic_pi_half_sphere.gif",
    "dtqc_legacy_metrics.csv": "dtqc_source_faithful_metrics.csv",
    "dtqc_legacy_state.npz": "dtqc_source_faithful_state.npz",
    "dtqc_legacy_source_removal.csv": "dtqc_source_removal.csv",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _clear_root_files(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for existing in output.iterdir():
        if existing.is_file():
            existing.unlink()


def _promote_source_faithful_artifacts(output: Path, legacy_output: Path) -> dict[str, object]:
    for source_name, target_name in PROMOTED_ARTIFACTS.items():
        shutil.copyfile(legacy_output / source_name, output / target_name)

    # Historical callers expect this filename. It now contains the complete
    # source-faithful DTQC composite rather than the old generic 1-D FieldLaw plot.
    shutil.copyfile(
        legacy_output / STATIC_FILES[0],
        output / ROOT_COMPATIBILITY_FIGURE,
    )

    legacy_manifest = json.loads((legacy_output / LEGACY_MANIFEST_FILE).read_text(encoding="utf-8"))
    theorem_manifests = sorted(path.name for path in output.glob("*_manifest.json"))
    root_payload_before_metadata = sorted(path.name for path in output.iterdir() if path.is_file())
    metadata = {
        "schema_version": "3.0",
        "suite": "dtqc_full_source_faithful_artifact_tree",
        "pipeline_partition": {
            "theorem_runtime": "existing Fibonacci/Pisot/Floquet and typed contract runtime retained",
            "visual_runtime": "legacy source-faithful decagonal/DFI/Elastic-pi/Flowpoint pipeline",
            "compatibility_figure": (
                "dtqc_spatial_closure.png is rebound to the source-faithful composite; "
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
        "root_payload_before_metadata": root_payload_before_metadata,
        "legacy_faithful_inventory": legacy_manifest["generated_files"] + [LEGACY_MANIFEST_FILE],
        "claim_boundary": legacy_manifest["claim_boundary"],
    }
    metadata_path = output / ROOT_METADATA_FILE
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checksummed_files = sorted(path.name for path in output.iterdir() if path.is_file())
    checksums = {
        "schema_version": "3.0",
        "algorithm": "sha256",
        "files": {name: _sha256(output / name) for name in checksummed_files},
    }
    checksum_path = output / ROOT_CHECKSUM_FILE
    checksum_path.write_text(json.dumps(checksums, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    final_inventory = sorted(path.name for path in output.iterdir() if path.is_file())
    expected_inventory = sorted([*checksummed_files, ROOT_CHECKSUM_FILE])
    if final_inventory != expected_inventory:
        raise RuntimeError(
            f"unexpected root DTQC artifact inventory: actual={final_inventory}, expected={expected_inventory}"
        )

    return {
        "metadata": metadata_path,
        "checksums": checksum_path,
        "files": [output / name for name in final_inventory],
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
    result["source_faithful_root"] = _promote_source_faithful_artifacts(
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
