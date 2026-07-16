"""Test sound cloning and generate evidence under this test module's artifacts directory."""

from __future__ import annotations

from pathlib import Path

import pytest
import torch

from the_nothingness_effect.artificial_intelligence.shared.capability_artifacts import run_capability_test
from the_nothingness_effect.artificial_intelligence.shared.types import AIObstructionError
from the_nothingness_effect.artificial_intelligence.sound_cloning import SoundCloner


CAPABILITY = "sound_cloning"


def run_test(output_dir: str | Path | None = None, *, seed: int = 0):
    output = Path(__file__).resolve().parent / "artifacts" if output_dir is None else Path(output_dir)
    return run_capability_test(CAPABILITY, output, seed=seed)


def test_capability(tmp_path: Path) -> None:
    outputs = run_test(tmp_path)
    assert outputs["metrics"].parent == tmp_path
    assert outputs["figure"].parent == tmp_path
    assert outputs["manifest"].parent == tmp_path


def test_non_finite_sound_clone_fails_closed() -> None:
    with pytest.raises(AIObstructionError):
        SoundCloner()(torch.full((256,), float("nan")))


def main() -> int:
    outputs = run_test()
    print(f"generated_files={len(outputs['generated_files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
