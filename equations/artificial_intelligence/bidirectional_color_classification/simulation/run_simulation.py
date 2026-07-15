"""Simulate bidirectional color classification and keep all outputs beside this producer."""

from __future__ import annotations

from pathlib import Path

from equations.artificial_intelligence.shared.capability_artifacts import run_capability_simulation


CAPABILITY = "bidirectional_color_classification"


def run_simulation(output_dir: str | Path | None = None, *, seed: int = 0):
    output = Path(__file__).resolve().parent if output_dir is None else Path(output_dir)
    return run_capability_simulation(CAPABILITY, output, seed=seed)


def main() -> int:
    outputs = run_simulation()
    print(f"generated_files={len(outputs['generated_files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
