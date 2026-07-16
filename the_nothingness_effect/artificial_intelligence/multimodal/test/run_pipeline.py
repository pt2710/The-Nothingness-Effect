"""Train, validate and evaluate the multimodal model with compact evidence."""

from __future__ import annotations

from pathlib import Path

from ..artifacts import run_multimodal_pipeline_artifacts


def run(output_dir: str | Path | None = None, *, seed: int = 0):
    output = (
        Path(output_dir)
        if output_dir is not None
        else Path(__file__).resolve().parent / "artifacts"
    )
    return run_multimodal_pipeline_artifacts(
        output,
        seed=seed,
        epochs=12,
        simulation=False,
    )


if __name__ == "__main__":
    result = run()
    print(
        {
            "figures": len(result["figures"]),
            "animations": len(result["animations"]),
            "tables": len(result["tables"]),
            "manifest": result["manifest"],
        }
    )
