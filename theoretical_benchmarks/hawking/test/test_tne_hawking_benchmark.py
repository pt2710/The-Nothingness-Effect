from __future__ import annotations

import csv
import json
from pathlib import Path

from theoretical_benchmarks.hawking.compare_tne_hawking_like_flux import run as run_comparison
from theoretical_benchmarks.hawking.simulation.simulate_hawking_theoretical_benchmark import run as run_benchmark


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_hawking_benchmark_outputs_are_generated():
    benchmark = run_benchmark()
    comparison = run_comparison()

    required_files = [
        benchmark["paths"]["data"],
        benchmark["paths"]["metrics"],
        benchmark["paths"]["metadata"],
        comparison["report"],
        comparison["manifest"],
        Path("theoretical_benchmarks/benchmark_summary.csv"),
        Path("theoretical_benchmarks/benchmark_summary.md"),
        Path("theoretical_benchmarks/benchmark_summary_metadata.json"),
    ]
    for path in required_files:
        assert Path(path).exists(), path

    metrics_rows = _read_csv(Path("theoretical_benchmarks/hawking/comparison/tne_vs_hawking_metrics.csv"))
    assert metrics_rows
    assert metrics_rows[0]["data_status"] == "theoretical_benchmark"

    manifest = json.loads(Path("theoretical_benchmarks/hawking/comparison/tne_vs_hawking_manifest.json").read_text(encoding="utf-8"))
    assert manifest["data_status"] == "theoretical_benchmark"

    report = Path("theoretical_benchmarks/hawking/comparison/tne_vs_hawking_report.md").read_text(encoding="utf-8").lower()
    assert "not empirical validation" in report
    assert "theoretical benchmark" in report
