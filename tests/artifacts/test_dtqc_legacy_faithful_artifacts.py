from __future__ import annotations

import hashlib
import json
import math

import numpy as np
from pathlib import Path

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
    result = run_legacy_faithful_suite(tmp_path, seed=17, grid_size=48)

    assert tuple(sorted(path.name for path in tmp_path.iterdir())) == tuple(sorted(EXPECTED_INVENTORY))
    assert result["manifest"] == tmp_path / MANIFEST_FILE
    manifest = json.loads((tmp_path / MANIFEST_FILE).read_text(encoding="utf-8"))
    assert manifest["mathematical_bindings"]["elastic_pi"] == "pi*exp(-S/K_D)"
    assert manifest["mathematical_bindings"]["flowpoint"] == "sigma_n=(-1)^n"
    assert all(value > 0.0 for value in manifest["source_removal"].values())
    assert "not a formal proof" in manifest["claim_boundary"]

    with np.load(tmp_path / "dtqc_legacy_state.npz") as state:
        np.testing.assert_allclose(
            state["flowpoint_frames"][2:],
            state["flowpoint_frames"][:-2],
            atol=0.0,
            rtol=0.0,
        )
        np.testing.assert_allclose(
            state["elastic_pi"],
            math.pi * np.exp(-state["entropy"] / manifest["entropy_scale"]),
            rtol=1e-14,
            atol=1e-14,
        )
        assert np.linalg.matrix_rank(state["projection_5d"]) == 5
        assert 0 < len(state["half_sphere_points"]) < len(state["sphere_points"])

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
