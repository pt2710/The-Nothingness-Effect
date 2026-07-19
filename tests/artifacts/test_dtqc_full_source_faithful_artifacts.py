from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.simulation.run_contract_suite import (
    PROMOTED_ARTIFACTS,
    ROOT_CHECKSUM_FILE,
    ROOT_COMPATIBILITY_FIGURE,
    ROOT_METADATA_FILE,
    run_suite,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_root_inventory(artifact_dir: Path) -> None:
    metadata = json.loads((artifact_dir / ROOT_METADATA_FILE).read_text(encoding="utf-8"))
    checksums = json.loads((artifact_dir / ROOT_CHECKSUM_FILE).read_text(encoding="utf-8"))
    assert checksums["schema_version"] == "3.0"
    assert checksums["algorithm"] == "sha256"
    assert "theorem manifests are verified separately" in checksums["scope"]

    actual_files = {path.name for path in artifact_dir.iterdir() if path.is_file()}
    assert actual_files == set(metadata["root_inventory"])
    assert set(checksums["files"]).issubset(actual_files)
    for name, expected in checksums["files"].items():
        assert _sha256(artifact_dir / name) == expected

    assert metadata["schema_version"] == "3.0"
    assert metadata["suite"] == "dtqc_full_source_faithful_artifact_tree"
    assert "Fibonacci/Pisot/Floquet" in metadata["pipeline_partition"]["theorem_runtime"]
    assert "stale generic FieldLaw line plot is not retained" in metadata["pipeline_partition"][
        "compatibility_figure"
    ]
    assert metadata["source_audit"]["visual_generator"].endswith(
        "flowpoint_elastic_pi/simulate_elastic_pi_quasi_crystals.py"
    )
    assert metadata["source_audit"]["canonical_dubler"].endswith(
        "elastic_dubler_effect/elastic_dubler_effect.py"
    )
    assert metadata["source_audit"]["visual_reference_directory"].endswith(
        "discrete_quasi_crystal_visualization"
    )
    assert all(value > 0.0 for value in metadata["source_removal"].values())

    assert (artifact_dir / ROOT_COMPATIBILITY_FIGURE).read_bytes() == (
        artifact_dir / "dtqc_source_faithful_summary.png"
    ).read_bytes()
    assert not any(path.name.startswith("dtqc_legacy_") for path in artifact_dir.iterdir() if path.is_file())

    for target_name in PROMOTED_ARTIFACTS.values():
        assert (artifact_dir / target_name).is_file()

    for name in (
        "dtqc_source_faithful_summary.png",
        "dtqc_quasicrystal_contour.png",
        "dtqc_diffraction_fft.png",
        "dtqc_dfi_surface.png",
        "dtqc_elastic_pi_surface.png",
        "dtqc_wavelet_ridges.png",
    ):
        with Image.open(artifact_dir / name) as image:
            image.verify()

    for name in (
        "dtqc_flowpoint_flicker.gif",
        "dtqc_5d_scatter.gif",
        "dtqc_elastic_pi_sphere.gif",
        "dtqc_elastic_pi_half_sphere.gif",
    ):
        with Image.open(artifact_dir / name) as movie:
            assert movie.is_animated
            assert movie.n_frames >= 8


def test_full_suite_replaces_stale_root_and_regenerates_all_artifact_classes(tmp_path: Path) -> None:
    (tmp_path / "stale_dtqc_visual.png").write_bytes(b"stale")
    run_suite(
        tmp_path,
        seed=17,
        grid_size=64,
        time_steps=12,
        point_count=600,
        sphere_resolution=48,
    )

    assert not (tmp_path / "stale_dtqc_visual.png").exists()
    _validate_root_inventory(tmp_path)

    with np.load(tmp_path / "dtqc_source_faithful_state.npz") as state:
        assert state["radial_profiles"].shape == (60, 64)
        assert state["flowpoint_frames"].shape == (12, 64, 64)
        assert state["scatter_trajectory_4d"].shape == (12, 600, 4)
        assert float(np.linalg.norm(state["flowpoint_frames"][1] + state["flowpoint_frames"][0])) > 1.0
        assert float(
            np.linalg.norm(state["scatter_trajectory_4d"][1] - state["scatter_trajectory_4d"][0])
        ) > 1.0
        assert not np.allclose(state["elastic_pi"], state["canonical_elastic_pi"])

    legacy_dir = tmp_path / "legacy_faithful"
    assert legacy_dir.is_dir()
    legacy_checksums = json.loads((legacy_dir / "dtqc_legacy_checksums.json").read_text(encoding="utf-8"))
    for name, expected in legacy_checksums["files"].items():
        assert _sha256(legacy_dir / name) == expected


def test_tracked_full_dtqc_artifact_tree_matches_committed_checksums() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    artifact_dir = (
        repository_root
        / "the_nothingness_effect"
        / "gravitational_cosmological_and_quantum_dynamics_architecture"
        / "discrete_time_quasicrystals_in_the_flowpoint"
        / "simulation"
        / "artifacts"
    )
    _validate_root_inventory(artifact_dir)
