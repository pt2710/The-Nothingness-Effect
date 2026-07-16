from pathlib import Path

import json
import numpy as np

from empirical.comparison.compare_spiral_rotation import run as run_spiral_comparison
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.animation.animate_spiral_galaxy_2d import run as run_spiral_galaxy_2d
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.animation.animate_spiral_galaxy_3d import run as run_spiral_galaxy_3d


def test_spiral_animation_outputs(tmp_path):
    result = run_spiral_galaxy_2d(output_dir=tmp_path, quick=True, arm_mode=3)
    for key in ["animation", "frame_strip", "data", "metadata"]:
        path = Path(result[key])
        assert path.exists()
        assert path.stat().st_size > 0


def test_spiral_animation_deterministic_with_fixed_seed(tmp_path):
    result_a = run_spiral_galaxy_2d(output_dir=tmp_path / "a", quick=True, arm_mode=4)
    result_b = run_spiral_galaxy_2d(output_dir=tmp_path / "b", quick=True, arm_mode=4)
    data_a = np.load(result_a["data"], allow_pickle=True)
    data_b = np.load(result_b["data"], allow_pickle=True)
    assert np.allclose(data_a["history"], data_b["history"])
    assert np.allclose(data_a["density_history"], data_b["density_history"])


def test_spiral_animation_has_no_nans(tmp_path):
    result = run_spiral_galaxy_2d(output_dir=tmp_path, quick=True, arm_mode="mixed")
    data = np.load(result["data"], allow_pickle=True)
    assert np.all(np.isfinite(data["history"]))
    assert np.all(np.isfinite(data["density_history"]))
    assert np.all(np.isfinite(data["tension_history"]))


def test_spiral_metadata_written(tmp_path):
    result = run_spiral_galaxy_2d(output_dir=tmp_path, quick=True, arm_mode=2)
    metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
    assert metadata["animation_name"] == "spiral_galaxy_formation_2d"
    assert metadata["arm_mode"] == 2
    assert metadata["fallback_mode"] in {"mp4", "gif", "frame_strip"}
    assert "metrics" in metadata


def test_spiral_3d_animation_outputs(tmp_path):
    result = run_spiral_galaxy_3d(output_dir=tmp_path, quick=True, preferred_format="frames", arm_mode=3)
    for key in ["animation", "frame_strip", "data", "metadata"]:
        path = Path(result[key])
        assert path.exists()
        assert path.stat().st_size > 0


def test_frame_strip_exists_for_both_animation_modes(tmp_path):
    result_2d = run_spiral_galaxy_2d(output_dir=tmp_path / "two_d", quick=True, preferred_format="frames", arm_mode=4)
    result_3d = run_spiral_galaxy_3d(output_dir=tmp_path / "three_d", quick=True, preferred_format="frames", arm_mode="mixed")
    assert Path(result_2d["frame_strip"]).exists()
    assert Path(result_3d["frame_strip"]).exists()


def test_empirical_spiral_comparison_still_runs(tmp_path):
    result = run_spiral_comparison(output_dir=tmp_path, use_fixtures=True, quick=True)
    assert Path(result["paths"]["data"]).exists()
    assert Path(result["paths"]["metrics"]).exists()
    assert Path(result["paths"]["figure"]).exists()
    assert result["metrics"]["passed_validation"] is True
