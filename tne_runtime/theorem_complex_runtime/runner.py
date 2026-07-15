"""CLI for inventory validation and implemented-contract execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .registry import TheoremComplexRegistry


DEFAULT_MATRIX = Path("docs/data/theorem_complex_implementation_matrix.csv")


def inventory_report(matrix: str | Path = DEFAULT_MATRIX) -> dict[str, object]:
    registry = TheoremComplexRegistry.from_csv(matrix)
    counts = registry.counts()
    return {
        "counts": counts,
        "duplicate_complex_ids": 0,
        "status_counts": _status_counts(registry),
    }


def _status_counts(registry: TheoremComplexRegistry) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in registry.inventory():
        counts[record.implementation_status] = counts.get(record.implementation_status, 0) + 1
    return dict(sorted(counts.items()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = inventory_report(args.matrix)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
