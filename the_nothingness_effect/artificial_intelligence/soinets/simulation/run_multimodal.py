"""Simulate the canonical multimodal SOInet with producer-local artifacts."""

from __future__ import annotations

from pathlib import Path

from the_nothingness_effect.artificial_intelligence.soinets.multimodal_artifacts import (
    run_multimodal_artifact_suite,
)


def run(output_dir: str | Path | None = None, *, seed: int = 0):
    output = (
        Path(output_dir)
        if output_dir is not None
        else Path(__file__).resolve().parent / "artifacts" / "multimodal"
    )
    return run_multimodal_artifact_suite(output, seed=seed, simulation=True)


if __name__ == "__main__":
    print(run())
