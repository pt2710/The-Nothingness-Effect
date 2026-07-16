"""Run all six SOInet capabilities on larger splits across multiple seeds."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import torch

from the_nothingness_effect.artificial_intelligence.shared.capability_artifacts import (
    CAPABILITIES,
)
from the_nothingness_effect.artificial_intelligence.shared.soinet_large_benchmark import (
    CLAIM_BOUNDARY,
    PROFILE_NAME,
    large_multi_seed_benchmark,
)


def run(
    output_dir: str | Path | None = None,
    *,
    seeds: tuple[int, ...] = (0, 1, 2),
):
    output = (
        Path(output_dir)
        if output_dir is not None
        else Path(__file__).resolve().parent / "artifacts" / "capability_benchmark"
    )
    output.mkdir(parents=True, exist_ok=True)
    checkpoint_dir = output / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    evaluations = large_multi_seed_benchmark(CAPABILITIES, seeds=seeds)
    rows = [evaluation.row for evaluation in evaluations]
    checkpoint_paths = []
    for evaluation in evaluations:
        filename = (
            f"{evaluation.row['capability']}_seed_{evaluation.row['seed']}_checkpoint.pt"
        )
        checkpoint_path = checkpoint_dir / filename
        torch.save(evaluation.checkpoint, checkpoint_path)
        checkpoint_paths.append(checkpoint_path)

    table = output / "soinets_six_capability_multiseed.csv"
    manifest = output / "soinets_six_capability_multiseed.json"
    with table.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest.write_text(
        json.dumps(
            {
                "architecture": "SOInet",
                "metric_producer": "SOInet",
                "architecture_coupled_metrics": True,
                "benchmark_profile": PROFILE_NAME,
                "capabilities": list(CAPABILITIES),
                "seeds": list(seeds),
                "row_count": len(rows),
                "split_profiles": {
                    capability: {
                        key: value
                        for key, value in rows[index * len(seeds)].items()
                        if key in {
                            "train_samples",
                            "validation_samples",
                            "test_samples",
                        }
                    }
                    for index, capability in enumerate(CAPABILITIES)
                },
                "source_status": "larger_multi_seed_train_validation_test_benchmark",
                "generated_files": [
                    table.name,
                    *[
                        str(path.relative_to(output))
                        for path in checkpoint_paths
                    ],
                ],
                "claim_boundary": CLAIM_BOUNDARY,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return {
        "table": table,
        "manifest": manifest,
        "checkpoints": tuple(checkpoint_paths),
        "rows": rows,
    }


if __name__ == "__main__":
    result = run()
    print(result["manifest"])
