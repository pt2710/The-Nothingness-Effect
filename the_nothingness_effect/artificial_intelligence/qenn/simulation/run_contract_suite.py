"""Generate fresh authoritative QENN theorem artifacts."""
from __future__ import annotations

import argparse
from pathlib import Path

from the_nothingness_effect.artificial_intelligence.qenn.authoritative_artifacts import run_suite


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "artifacts",
    )
    parser.add_argument("--seed", type=int, default=0)
    arguments = parser.parse_args()
    print(run_suite(arguments.output, seed=arguments.seed))
