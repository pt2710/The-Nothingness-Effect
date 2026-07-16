"""Test color cloning and generate evidence under this test module's artifacts directory."""

from __future__ import annotations

from pathlib import Path

import pytest
import torch

from the_nothingness_effect.artificial_intelligence.color_cloning import ColorCloner
from the_nothingness_effect.artificial_intelligence.shared.capability_artifacts import run_capability_test
from the_nothingness_effect.artificial_intelligence.shared.types import AIObstructionError


CAPABILITY = "color_cloning"


def run_test(output_dir: str | Path | None = None, *, seed: int = 0):
    output = Path(__file__).resolve().parent / "artifacts" if output_dir is None else Path(output_dir)
    return run_capability_test(CAPABILITY, output, seed=seed)


def test_capability(tmp_path: Path) -> None:
    outputs = run_test(tmp_path)
    assert outputs["metrics"].parent == tmp_path
    assert outputs["figure"].parent == tmp_path
    assert outputs["manifest"].parent == tmp_path


def test_invalid_color_clone_domain_fails_closed() -> None:
    with pytest.raises(AIObstructionError):
        ColorCloner()(torch.full((8, 8, 3), -0.1))


def main() -> int:
    outputs = run_test()
    print(f"generated_files={len(outputs['generated_files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
