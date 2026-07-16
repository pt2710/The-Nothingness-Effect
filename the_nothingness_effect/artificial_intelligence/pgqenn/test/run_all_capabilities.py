"""Test PGQENN across every required visual and auditory output group."""

from __future__ import annotations

from pathlib import Path

from the_nothingness_effect.artificial_intelligence.pgqenn.model import PGQENNModel
from the_nothingness_effect.artificial_intelligence.shared.architecture_capability_artifacts import run_architecture_capability_suite


def run_all(output_dir: str | Path | None = None, *, seed: int = 0):
    output = Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent / "artifacts"
    return run_architecture_capability_suite("pgqenn", PGQENNModel, output, seed=seed, simulation=False)


def test_pgqenn_exercises_all_six_outputs(tmp_path: Path) -> None:
    result = run_all(tmp_path, seed=0)
    assert result["capability_count"] == 6
    assert len(result["architecture"]["residuals"]) >= 4


if __name__ == "__main__":
    print(run_all())
