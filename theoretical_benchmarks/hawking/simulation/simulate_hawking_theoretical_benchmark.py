"""Generate standard Hawking theoretical benchmark artifacts."""

from __future__ import annotations

import argparse

from theoretical_benchmarks.hawking.hawking_theoretical_benchmark import (
    build_hawking_benchmark,
    write_hawking_benchmark_outputs,
)


def run() -> dict[str, object]:
    benchmark = build_hawking_benchmark()
    paths = write_hawking_benchmark_outputs(benchmark)
    print("Generated Hawking theoretical benchmark artifacts.")
    print("Scope: theoretical benchmark only; not empirical validation.")
    return {"benchmark": benchmark, "paths": paths}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Hawking theoretical benchmark artifacts.")
    parser.parse_args(argv)
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
