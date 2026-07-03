from __future__ import annotations

import csv
import json
from pathlib import Path


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_aggregate_runner_writes_required_fixture_outputs(empirical_fixture_run):
    summary_paths = empirical_fixture_run["summary_paths"]
    output_root = Path(summary_paths["metrics"]).parent.parent

    required_files = [
        output_root / "data" / "dubler_redshift_comparison.csv",
        output_root / "data" / "spiral_rotation_comparison.csv",
        output_root / "data" / "eht_horizon_comparison.csv",
        output_root / "data" / "observer_memory_comparison.csv",
        output_root / "data" / "elastic_pi_ringdown_comparison.csv",
        output_root / "metrics" / "dubler_redshift_metrics.csv",
        output_root / "metrics" / "spiral_rotation_metrics.csv",
        output_root / "metrics" / "eht_horizon_metrics.csv",
        output_root / "metrics" / "observer_memory_metrics.csv",
        output_root / "metrics" / "elastic_pi_ringdown_metrics.csv",
        output_root / "metrics" / "empirical_comparison_summary.csv",
        output_root / "metrics" / "empirical_audit_run6.csv",
        output_root / "figures" / "dubler_redshift_comparison.png",
        output_root / "figures" / "dubler_redshift_residuals.png",
        output_root / "figures" / "spiral_rotation_comparison.png",
        output_root / "figures" / "spiral_rotation_residuals.png",
        output_root / "figures" / "spiral_morphology_comparison.png",
        output_root / "figures" / "spiral_rotation_arm_mode_comparison.png",
        output_root / "figures" / "eht_horizon_comparison.png",
        output_root / "figures" / "eht_horizon_residuals.png",
        output_root / "figures" / "observer_memory_comparison.png",
        output_root / "figures" / "elastic_pi_ringdown_comparison.png",
        output_root / "figures" / "elastic_pi_ringdown_residuals.png",
        output_root / "figures" / "elastic_pi_ringdown_envelope.png",
        output_root / "figures" / "elastic_pi_ringdown_window_sensitivity.png",
        output_root / "figures" / "elastic_pi_ringdown_basis_stability.png",
        output_root / "reports" / "dubler_redshift_report.md",
        output_root / "reports" / "spiral_rotation_report.md",
        output_root / "reports" / "spiral_rotation_arm_mode_report.md",
        output_root / "reports" / "eht_horizon_report.md",
        output_root / "reports" / "observer_memory_report.md",
        output_root / "reports" / "elastic_pi_ringdown_report.md",
        output_root / "reports" / "empirical_comparison_summary.md",
        output_root / "reports" / "empirical_audit_run6.md",
        output_root / "manifests" / "source_registry.json",
        output_root / "manifests" / "dubler_redshift_manifest.json",
        output_root / "manifests" / "spiral_rotation_manifest.json",
        output_root / "manifests" / "spiral_rotation_arm_mode_manifest.json",
        output_root / "manifests" / "eht_horizon_manifest.json",
        output_root / "manifests" / "observer_memory_manifest.json",
        output_root / "manifests" / "elastic_pi_ringdown_manifest.json",
        output_root / "manifests" / "empirical_comparison_metadata.json",
        output_root / "manifests" / "empirical_audit_run6.json",
    ]

    for path in required_files:
        assert path.exists(), path

    summary_rows = _read_csv(output_root / "metrics" / "empirical_comparison_summary.csv")
    assert len(summary_rows) == 5
    assert {row["data_status"] for row in summary_rows} == {"fixture_only"}
    assert "hawking_theoretical_benchmark" not in {row["empirical_dataset"] for row in summary_rows}

    for csv_path in output_root.glob("data/*.csv"):
        rows = _read_csv(csv_path)
        assert rows
        assert {row["source_status"] for row in rows} == {"fixture_only"}

    for csv_path in output_root.glob("metrics/*.csv"):
        rows = _read_csv(csv_path)
        assert rows

    for json_path in output_root.glob("manifests/*.json"):
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        assert "claim_boundary" in payload
