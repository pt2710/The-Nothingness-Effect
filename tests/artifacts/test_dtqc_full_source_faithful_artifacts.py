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
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.simulation.run_legacy_faithful_suite import (
    ANIMATED_FILES,
    EXPECTED_INVENTORY,
    STATIC_FILES,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_full_tree(artifact_dir: Path) -> None:
    legacy_dir = artifact_dir / "legacy_faithful"
    metadata = json.loads((artifact_dir / ROOT_METADATA_FILE).read_text(encoding="utf-8"))
    checksums = json.loads((artifact_dir / ROOT_CHECKSUM_FILE).read_text(encoding="utf-8"))

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

    actual_root_files = {path.name for path in artifact_dir.iterdir() if path.is_file()}
    actual_legacy_files = {path.name for path in legacy_dir.iterdir() if path.is_file()}
    assert actual_root_files == set(metadata["root_inventory"])
    assert actual_legacy_files == set(metadata["legacy_faithful_inventory"])
    assert actual_legacy_files == set(EXPECTED_INVENTORY)

    assert checksums["schema_version"] == "3.0"
    assert checksums["algorithm"] == "sha256"
    assert "recursive DTQC source-faithful tree" in checksums["scope"]
    for name, expected in checksums["root_files"].items():
        assert _sha256(artifact_dir / name) == expected
    for name, expected in checksums["legacy_faithful_files"].items():
        assert _sha256(legacy_dir / name) == expected

    for source_name, target_name in PROMOTED_ARTIFACTS.items():
        assert (legacy_dir / source_name).is_file()
        assert (artifact_dir / target_name).is_file()
        assert (artifact_dir / target_name).read_bytes() == (legacy_dir / source_name).read_bytes()

    assert not any(path.name.startswith("dtqc_legacy_") for path in artifact_dir.iterdir() if path.is_file())
    with Image.open(artifact_dir / ROOT_COMPATIBILITY_FIGURE) as image:
        image.verify()
    for name in STATIC_FILES:
        with Image.open(legacy_dir / name) as image:
            image.verify()
    for name in ANIMATED_FILES:
        with Image.open(legacy_dir / name) as movie:
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
    _validate_full_tree(tmp_path)

    with np.load(tmp_path / "legacy_faithful" / "dtqc_legacy_state.npz") as state:
        assert state["radial_profiles"].shape == (60, 64)
        assert state["flowpoint_frames"].shape == (12, 64, 64)
        assert state["scatter_trajectory_4d"].shape == (12, 600, 4)
        assert float(np.linalg.norm(state["flowpoint_frames"][1] + state["flowpoint_frames"][0])) > 1.0
        assert float(
            np.linalg.norm(state["scatter_trajectory_4d"][1] - state["scatter_trajectory_4d"][0])
        ) > 1.0
        assert not np.allclose(state["elastic_pi"], state["canonical_elastic_pi"])


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
    _validate_full_tree(artifact_dir)
