from pathlib import Path

import json
import numpy as np

from equations.black_hole_dynamics.animation.animate_entropic_horizon_2d import run as run_entropic_horizon_2d
from equations.black_hole_dynamics.animation.animate_entropic_tension_3d import run as run_entropic_tension_3d
from equations.black_hole_dynamics.animation.animate_hawking_flux_3d import run as run_hawking_flux_3d
from equations.black_hole_dynamics.animation.animate_hawking_like_flux_2d import run as run_hawking_like_flux_2d
from equations.black_hole_dynamics.animation.animate_observer_horizon_3d import run as run_observer_horizon_3d
from equations.black_hole_dynamics.animation.animate_observer_horizon_memory_2d import run as run_observer_horizon_memory_2d
from equations.black_hole_dynamics.black_hole_dynamics import detect_threshold_crossing
from equations.run_animation_artifacts import main as run_animation_artifacts_main


def _assert_core_outputs(result: dict[str, object]) -> None:
    for key in ["animation", "frame_strip", "data", "metadata"]:
        path = Path(result[key])
        assert path.exists()
        assert path.stat().st_size > 0


def test_horizon_crossing_animation_outputs(tmp_path):
    result = run_entropic_horizon_2d(output_dir=tmp_path, quick=True)
    _assert_core_outputs(result)
    data = np.load(result["data"])
    assert data["pi_E_time"].ndim == 2
    assert np.all(np.isfinite(data["pi_E_time"]))
    metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
    assert metadata["animation_name"] == "entropic_horizon_crossing_2d"


def test_horizon_crossing_detector_interpolates():
    r = np.array([1.0, 2.0, 3.0])
    field = np.array([0.2, 0.6, 0.9])
    crossing = detect_threshold_crossing(r, field, threshold=0.5)
    assert np.isfinite(crossing)
    assert 1.0 < crossing < 2.0


def test_hawking_flux_animation_has_visible_range(tmp_path):
    result = run_hawking_like_flux_2d(output_dir=tmp_path, quick=True)
    _assert_core_outputs(result)
    data = np.load(result["data"])
    assert data["flux_proxy"].ndim == 1
    assert float(np.ptp(data["flux_proxy"])) > 0.0


def test_observer_memory_animation_has_visible_range(tmp_path):
    result = run_observer_horizon_memory_2d(output_dir=tmp_path, quick=True)
    _assert_core_outputs(result)
    data = np.load(result["data"])
    assert float(np.ptp(data["memory"])) > 0.0
    assert float(np.ptp(data["observer_distance"])) > 0.0


def test_animation_metadata_records_fallback_mode(tmp_path):
    result = run_entropic_horizon_2d(output_dir=tmp_path, quick=True)
    metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
    assert metadata["fallback_mode"] in {"mp4", "gif", "frame_strip"}


def test_black_hole_3d_animation_outputs(tmp_path):
    for runner in [run_entropic_tension_3d, run_hawking_flux_3d, run_observer_horizon_3d]:
        result = runner(output_dir=tmp_path, quick=True, preferred_format="frames")
        _assert_core_outputs(result)
        data = np.load(result["data"])
        assert np.all(np.isfinite(data[list(data.files)[0]]))


def test_aggregate_runner_quick_mode(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_animation_artifacts",
            "--quick",
            "--output-dir",
            str(tmp_path),
            "--format",
            "frames",
        ],
    )
    run_animation_artifacts_main()
    assert (tmp_path / "animation_artifacts_summary.csv").exists()
    assert (tmp_path / "animation_artifacts_metadata.json").exists()
