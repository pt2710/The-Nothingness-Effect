from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.simulation.run_legacy_faithful_suite import (
    ANIMATED_FILES,
    CHECKSUM_FILE,
    EXPECTED_INVENTORY,
    MANIFEST_FILE,
    STATIC_FILES,
    run_legacy_faithful_suite,
)


def test_legacy_faithful_suite_materializes_exact_byte_verified_inventory(tmp_path: Path) -> None:
    result = run_legacy_faithful_suite(
        tmp_path,
        seed=17,
        grid_size=64,
        time_steps=12,
        point_count=600,
        sphere_resolution=48,
    )

    assert tuple(sorted(path.name for path in tmp_path.iterdir())) == tuple(sorted(EXPECTED_INVENTORY))
    assert result["manifest"] == tmp_path / MANIFEST_FILE
    manifest = json.loads((tmp_path / MANIFEST_FILE).read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "2.0"
    assert manifest["radial_channels"] == 60
    assert manifest["mathematical_bindings"]["legacy_visual_elastic_pi"].startswith(
        "pi*mean_i(exp(S_i/K_D))"
    )
    assert manifest["mathematical_bindings"]["canonical_dubler_ratio"].startswith(
        "exp(-delta_S/K_D)"
    )
    assert "intrinsically phase-evolving" in manifest["mathematical_bindings"]["flowpoint"]
    assert all(value > 0.0 for value in manifest["source_removal"].values())
    assert "not a formal proof" in manifest["claim_boundary"]

    with np.load(tmp_path / "dtqc_legacy_state.npz") as state:
        assert state["radial_profiles"].shape == (60, 64)
        assert state["flowpoint_frames"].shape == (12, 64, 64)
        assert state["scatter_trajectory_4d"].shape == (12, 600, 4)
        assert state["projection_3d"].shape == (12, 600, 3)
        assert float(
            np.linalg.norm(state["flowpoint_frames"][1] + state["flowpoint_frames"][0])
        ) > 1.0
        assert float(
            np.linalg.norm(state["scatter_trajectory_4d"][1] - state["scatter_trajectory_4d"][0])
        ) > 1.0
        assert not np.allclose(state["elastic_pi"], state["canonical_elastic_pi"])

    checksums = json.loads((tmp_path / CHECKSUM_FILE).read_text(encoding="utf-8"))
    assert set(checksums["files"]) == set(EXPECTED_INVENTORY) - {CHECKSUM_FILE}
    for name, expected in checksums["files"].items():
        assert hashlib.sha256((tmp_path / name).read_bytes()).hexdigest() == expected

    for name in STATIC_FILES:
        with Image.open(tmp_path / name) as image:
            image.verify()
    for name in ANIMATED_FILES:
        with Image.open(tmp_path / name) as movie:
            assert movie.is_animated
            assert movie.n_frames >= 8


def test_tracked_legacy_faithful_inventory_matches_committed_checksums() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    artifact_dir = (
        repository_root
        / "the_nothingness_effect"
        / "gravitational_cosmological_and_quantum_dynamics_architecture"
        / "discrete_time_quasicrystals_in_the_flowpoint"
        / "simulation"
        / "artifacts"
        / "legacy_faithful"
    )

    assert tuple(sorted(path.name for path in artifact_dir.iterdir() if path.is_file())) == tuple(
        sorted(EXPECTED_INVENTORY)
    )
    checksums = json.loads((artifact_dir / CHECKSUM_FILE).read_text(encoding="utf-8"))
    assert checksums["schema_version"] == "2.0"
    assert set(checksums["files"]) == set(EXPECTED_INVENTORY) - {CHECKSUM_FILE}
    for name, expected in checksums["files"].items():
        assert hashlib.sha256((artifact_dir / name).read_bytes()).hexdigest() == expected
