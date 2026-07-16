"""Test QENN across every required visual and auditory output group."""

from __future__ import annotations

from pathlib import Path

from the_nothingness_effect.artificial_intelligence.qenn.model import QENNModel
from the_nothingness_effect.artificial_intelligence.shared.architecture_capability_artifacts import run_architecture_capability_suite


def run_all(output_dir: str | Path | None = None, *, seed: int = 0):
    output = Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent / "artifacts"
    return run_architecture_capability_suite("qenn", QENNModel, output, seed=seed, simulation=False)


def test_qenn_exercises_all_six_outputs(tmp_path: Path) -> None:
    result = run_all(tmp_path, seed=0)
    assert result["capability_count"] == 6
    assert set(result["capabilities"]) == {
        "color_classification", "sound_classification",
        "bidirectional_color_classification", "bidirectional_sound_classification",
        "color_cloning", "sound_cloning",
    }


if __name__ == "__main__":
    print(run_all())
