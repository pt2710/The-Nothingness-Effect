"""Test bidirectional color classification and generate evidence beside this script when run directly."""

from __future__ import annotations

from pathlib import Path

import pytest
import torch

from the_nothingness_effect.artificial_intelligence.bidirectional_color_classification import BidirectionalColorClassifier
from the_nothingness_effect.artificial_intelligence.shared.capability_artifacts import run_capability_test
from the_nothingness_effect.artificial_intelligence.shared.types import AIObstructionError


CAPABILITY = "bidirectional_color_classification"


def run_test(output_dir: str | Path | None = None, *, seed: int = 0):
    output = Path(__file__).resolve().parent if output_dir is None else Path(output_dir)
    return run_capability_test(CAPABILITY, output, seed=seed)


def test_capability(tmp_path: Path) -> None:
    outputs = run_test(tmp_path)
    assert outputs["metrics"].parent == tmp_path
    assert outputs["figure"].parent == tmp_path
    assert outputs["manifest"].parent == tmp_path


def test_out_of_range_color_fails_closed() -> None:
    with pytest.raises(AIObstructionError):
        BidirectionalColorClassifier()(torch.full((1, 4, 4, 3), 1.5))


def main() -> int:
    outputs = run_test()
    print(f"generated_files={len(outputs['generated_files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
