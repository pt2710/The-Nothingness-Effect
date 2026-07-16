"""Run the six SOInet-coupled capabilities across multiple seeds."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from the_nothingness_effect.artificial_intelligence.shared.capability_artifacts import (
    CAPABILITIES,
)
from the_nothingness_effect.artificial_intelligence.shared.soinet_capability_runtime import (
    multi_seed_benchmark,
)


def run(
    output_dir: str | Path | None = None,
    *,
    seeds: tuple[int, ...] = (0, 1, 2),
    simulation: bool = True,
):
    output = (
        Path(output_dir)
        if output_dir is not None
        else Path(__file__).resolve().parent / "artifacts" / "capability_benchmark"
    )
    output.mkdir(parents=True, exist_ok=True)
    rows = multi_seed_benchmark(
        CAPABILITIES, seeds=seeds, simulation=simulation
    )
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
                "capabilities": list(CAPABILITIES),
                "seeds": list(seeds),
                "row_count": len(rows),
                "source_status": "multi_seed_train_validation_test_benchmark",
                "generated_files": [table.name],
                "claim_boundary": (
                    "finite synthetic multi-seed benchmark; not a real-world "
                    "generalization or formal proof claim"
                ),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return {"table": table, "manifest": manifest, "rows": rows}


if __name__ == "__main__":
    result = run()
    print(result["manifest"])
