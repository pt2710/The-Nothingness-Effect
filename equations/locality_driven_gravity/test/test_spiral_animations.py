from pathlib import Path

import json
import numpy as np

from equations.locality_driven_gravity.animation.animate_spiral_galaxy_2d import run as run_spiral_galaxy_2d
from equations.locality_driven_gravity.animation.animate_spiral_galaxy_3d import run as run_spiral_galaxy_3d


def test_spiral_animation_outputs(tmp_path):
    result = run_spiral_galaxy_2d(output_dir=tmp_path, quick=True)
    for key in ["animation", "frame_strip", "data", "metadata"]:
        path = Path(result[key])
        assert path.exists()
        assert path.stat().st_size > 0


def test_spiral_animation_deterministic_with_fixed_seed(tmp_path):
    result_a = run_spiral_galaxy_2d(output_dir=tmp_path / "a", quick=True)
    result_b = run_spiral_galaxy_2d(output_dir=tmp_path / "b", quick=True)
    data_a = np.load(result_a["data"])
    data_b = np.load(result_b["data"])
    assert np.allclose(data_a["history"], data_b["history"])


def test_spiral_animation_has_no_nans(tmp_path):
    result = run_spiral_galaxy_2d(output_dir=tmp_path, quick=True)
    data = np.load(result["data"])
    assert np.all(np.isfinite(data["history"]))


def test_spiral_metadata_written(tmp_path):
    result = run_spiral_galaxy_2d(output_dir=tmp_path, quick=True)
    metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
    assert metadata["animation_name"] == "spiral_galaxy_formation_2d"
    assert metadata["fallback_mode"] in {"mp4", "gif", "frame_strip"}


def test_spiral_3d_animation_outputs(tmp_path):
    result = run_spiral_galaxy_3d(output_dir=tmp_path, quick=True, preferred_format="frames")
    for key in ["animation", "frame_strip", "data", "metadata"]:
        path = Path(result[key])
        assert path.exists()
        assert path.stat().st_size > 0
