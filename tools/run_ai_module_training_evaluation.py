"""CLI for the TNE QENN/PGQENN/SOInets evaluation pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from the_nothingness_effect.artificial_intelligence.evaluation_pipeline import (
    run_ai_module_training_evaluation,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=[0, 1, 2],
    )
    parser.add_argument("--epochs", type=int, default=6)
    parser.add_argument(
        "--samples-per-class",
        type=int,
        default=10,
    )
    args = parser.parse_args()
    report = run_ai_module_training_evaluation(
        args.output,
        seeds=tuple(args.seeds),
        epochs=args.epochs,
        samples_per_class=args.samples_per_class,
    )
    summaries = report["test_performance"]["seed_summary"]
    mean_accuracy = sum(
        float(row["test_accuracy"]) for row in summaries
    ) / len(summaries)
    print(
        "ai_module_training_evaluation=passed "
        f"seeds={args.seeds} mean_test_accuracy={mean_accuracy:.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
