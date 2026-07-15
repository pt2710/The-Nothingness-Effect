"""Simulate QENN across every required visual and auditory output group."""

from __future__ import annotations

from pathlib import Path

from the_nothingness_effect.artificial_intelligence.qenn.model import QENNModel
from the_nothingness_effect.artificial_intelligence.shared.architecture_capability_artifacts import run_architecture_capability_suite


def run_all(output_dir: str | Path | None = None, *, seed: int = 0):
    output = Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent
    return run_architecture_capability_suite("qenn", QENNModel, output, seed=seed, simulation=True)


if __name__ == "__main__":
    print(run_all())
