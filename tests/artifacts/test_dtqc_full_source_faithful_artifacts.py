from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.spatial_elastic_pi import (
    spatial_2d_diagnostics,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.simulation.run_contract_suite import (
    PROMOTED_ARTIFACTS,
    ROOT_CHECKSUM_FILE,
    ROOT_COMPATIBILITY_FIGURE,
    ROOT_METADATA_FILE,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.simulation.run_evidence import (
    run_all,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.simulation.run_legacy_faithful_suite import (
    ANIMATED_FILES,
    EXPECTED_INVENTORY,
    STATIC_FILES,
)


EXPECTED_ROOT_FILES = {
    "artifact_policy.json",
    "dfi_surface.png",
    "diffraction_fft.png",
    "diophantine_parseval_locking_invariant_manifest.json",
    "dtqc__dual_support_equivalence_support_mismatch_leakage_manifest.json",
    ROOT_CHECKSUM_FILE,
    ROOT_METADATA_FILE,
    "dtqc_contract_metrics.csv",
    "dtqc_phase_clock_animation.gif",
    "dtqc_simulation_evidence_manifest.json",
    "dtqc_simulation_phase_trace.csv",
    "dtqc_simulation_residual_animation.gif",
    "dtqc_simulation_residual_trace.csv",
    "dtqc_simulation_visualization_manifest.json",
    ROOT_COMPATIBILITY_FIGURE,
    "elastic_dtqc_spectral_measure_dual_of_dtqc_manifest.json",
    "elastic_gain_support_transport_isomorphism_manifest.json",
    "elastic_parseval_quasicrystal_isometry_manifest.json",
    "elastic_pi_intrinsic_axes.png",
    "elastic_pi_surface.png",
    "irrational_drive_locking_commensurate_resonance_collapse_manifest.json",
    "manifest.json",
    "parseval_energy_bijection_l_2_energy_mismatch_manifest.json",
    "qc_contour.png",
    "wavelet_central_row.png",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_full_tree(artifact_dir: Path) -> None:
    legacy_dir = artifact_dir / "legacy_faithful"
    metadata = json.loads((artifact_dir / ROOT_METADATA_FILE).read_text(encoding="utf-8"))
    checksums = json.loads((artifact_dir / ROOT_CHECKSUM_FILE).read_text(encoding="utf-8"))

    assert metadata["schema_version"] == "5.0"
    assert metadata["suite"] == "dtqc_complete_recursive_artifact_pipeline"
    assert set(metadata["generator_inventory"]) == {
        "typed_contracts",
        "canonical_simulation_visuals",
        "legacy_source_faithful_visuals",
        "full_orchestrator",
    }
    assert "Fibonacci/Pisot/Floquet" in metadata["pipeline_partition"]["theorem_runtime"]
    assert "stale generic FieldLaw line plot is not retained" in metadata[
        "pipeline_partition"
    ]["compatibility_figure"]
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

    canonical = metadata["spatial_regression"]["canonical"]
    assert canonical["row_broadcast_residual"] > 0.1
    assert canonical["column_broadcast_residual"] > 0.1
    assert canonical["axis_gradient_balance"] > 0.1
    assert canonical["effective_rank"] > 1.5
    assert canonical["axis_count"] == 5
    assert canonical["axis_names"] == ["x", "y", "z", "w", "u"]
    assert canonical["all_intrinsic_axes_applied"] is True
    assert canonical["minimum_axis_source_removal_residual"] > 1e-4
    assert canonical["minimum_dfi_axis_norm"] > 0.0
    assert canonical["axis_application_residual"] < 1e-12
    assert canonical["direct_law_residual"] < 1e-12
    assert all(value > 1e-3 for value in canonical["axis_elastic_pi_spans"])

    for diagnostics in metadata["spatial_regression"]["legacy"].values():
        assert diagnostics["row_broadcast_residual"] > 0.1
        assert diagnostics["column_broadcast_residual"] > 0.1
        assert diagnostics["axis_gradient_balance"] > 0.1
        assert diagnostics["effective_rank"] > 1.5

    actual_root_files = {path.name for path in artifact_dir.iterdir() if path.is_file()}
    actual_legacy_files = {path.name for path in legacy_dir.iterdir() if path.is_file()}
    assert actual_root_files == set(metadata["root_inventory"]) == EXPECTED_ROOT_FILES
    assert actual_legacy_files == set(metadata["legacy_faithful_inventory"]) == set(
        EXPECTED_INVENTORY
    )

    assert checksums["schema_version"] == "5.0"
    assert checksums["algorithm"] == "sha256"
    assert "all tracked DTQC root payloads" in checksums["scope"]
    assert set(checksums["root_files"]) == EXPECTED_ROOT_FILES - {ROOT_CHECKSUM_FILE}
    assert set(checksums["legacy_faithful_files"]) == set(EXPECTED_INVENTORY)
    for name, expected in checksums["root_files"].items():
        assert _sha256(artifact_dir / name) == expected
    for name, expected in checksums["legacy_faithful_files"].items():
        assert _sha256(legacy_dir / name) == expected

    for source_name, target_name in PROMOTED_ARTIFACTS.items():
        source = artifact_dir / source_name
        target = artifact_dir / target_name
        assert source.is_file()
        assert target.is_file()
        assert target.read_bytes() == source.read_bytes()

    with Image.open(artifact_dir / ROOT_COMPATIBILITY_FIGURE) as image:
        image.verify()
    for name in ("dfi_surface.png", "elastic_pi_surface.png", "elastic_pi_intrinsic_axes.png"):
        with Image.open(artifact_dir / name) as image:
            image.verify()
    for name in STATIC_FILES:
        with Image.open(legacy_dir / name) as image:
            image.verify()
    for name in ANIMATED_FILES:
        with Image.open(legacy_dir / name) as movie:
            assert movie.is_animated
            assert movie.n_frames >= 8
    for name in ("dtqc_phase_clock_animation.gif", "dtqc_simulation_residual_animation.gif"):
        with Image.open(artifact_dir / name) as movie:
            assert movie.is_animated
            assert movie.n_frames >= 8


def test_full_pipeline_replaces_stale_root_and_regenerates_every_artifact_class(
    tmp_path: Path,
) -> None:
    (tmp_path / "stale_dtqc_visual.png").write_bytes(b"stale")
    run_all(
        tmp_path,
        seed=0,
        generation_source_commit="0" * 40,
    )

    assert not (tmp_path / "stale_dtqc_visual.png").exists()
    _validate_full_tree(tmp_path)

    with np.load(tmp_path / "legacy_faithful" / "dtqc_legacy_state.npz") as state:
        assert state["radial_profiles"].shape == (60, 240)
        assert state["flowpoint_frames"].shape == (48, 240, 240)
        assert state["scatter_trajectory_4d"].shape == (48, 8000, 4)
        assert float(np.linalg.norm(state["flowpoint_frames"][1] + state["flowpoint_frames"][0])) > 1.0
        assert float(
            np.linalg.norm(state["scatter_trajectory_4d"][1] - state["scatter_trajectory_4d"][0])
        ) > 1.0
        assert not np.allclose(state["elastic_pi"], state["canonical_elastic_pi"])
        for name in ("entropy", "elastic_pi", "canonical_elastic_pi"):
            diagnostics = spatial_2d_diagnostics(state[name])
            assert diagnostics["row_broadcast_residual"] > 0.1
            assert diagnostics["column_broadcast_residual"] > 0.1
            assert diagnostics["axis_gradient_balance"] > 0.1
            assert diagnostics["effective_rank"] > 1.5


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
