"""CLI for comprehensive TNE Artificial Intelligence evaluation."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from the_nothingness_effect.artificial_intelligence.comprehensive_evaluation import (
    run_comprehensive_ai_evaluation,
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
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument(
        "--samples-per-class",
        type=int,
        default=16,
    )
    args = parser.parse_args()
    report = run_comprehensive_ai_evaluation(
        args.output,
        seeds=tuple(args.seeds),
        epochs=args.epochs,
        samples_per_class=args.samples_per_class,
    )
    seed_summary = report["seed_summary"]
    mean_test_accuracy = sum(
        float(row["test_accuracy"])
        for row in seed_summary
    ) / len(seed_summary)
    print(
        "comprehensive_ai_evaluation=passed "
        f"seeds={len(seed_summary)} "
        f"artifacts={report['artifact_count']} "
        f"plots={report['plot_count']} "
        f"mean_test_accuracy={mean_test_accuracy:.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
