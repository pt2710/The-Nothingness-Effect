"""Test SOInets across every required visual and auditory output group."""

from __future__ import annotations

from pathlib import Path

from equations.artificial_intelligence.shared.architecture_capability_artifacts import run_architecture_capability_suite
from equations.artificial_intelligence.soinets.model import SOInetModel


def run_all(output_dir: str | Path | None = None, *, seed: int = 0):
    output = Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent
    return run_architecture_capability_suite("soinets", SOInetModel, output, seed=seed, simulation=False)


def test_soinets_exercises_all_six_outputs(tmp_path: Path) -> None:
    result = run_all(tmp_path, seed=0)
    assert result["capability_count"] == 6
    assert result["architecture"]["metadata"]["architecture"] == "SOInet"


if __name__ == "__main__":
    print(run_all())
