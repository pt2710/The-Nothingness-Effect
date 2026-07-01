"""Generate Run 6 empirical audit artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from empirical.io import audit_paths, repo_relative, save_rows, write_manifest, write_report


MODEL_NOTES: dict[str, dict[str, str]] = {
    "redshift_clock": {
        "classification": "empirical_comparison",
        "diagnosis": "Small-sample benchmark with strong residual fit, but unit/sign interpretation and baseline provenance remain the main risks.",
        "implemented": "Explicit sign-convention metadata, bounded fit metadata, residual diagnostics, and report-level formula documentation.",
        "deferred": "Additional holdout analysis is not meaningful with only two benchmark rows.",
    },
    "galaxy_rotation": {
        "classification": "empirical_comparison",
        "diagnosis": "The main weakness is observable mapping and parameter regime selection, not raw data availability. Rotation-curve proxy quality depends strongly on radial binning and bounded parameter sweeps.",
        "implemented": "Tangential-velocity extraction, bounded deterministic parameter sweep, simple baseline family, and morphology diagnostics.",
        "deferred": "Full multi-galaxy catalog support and stronger astrophysical calibration remain future work.",
    },
    "eht_observables": {
        "classification": "empirical_comparison",
        "diagnosis": "The limiting factor is summary-observable mapping and angular scaling rather than missing raw imaging products. Shared-scale fits remain coarse; per-source scaling is diagnostic only.",
        "implemented": "Threshold-crossing proxy audit, weighted residuals, shared-scale vs per-source diagnostics, and residual plots.",
        "deferred": "No GRMHD image reconstruction or instrument forward model is included.",
    },
    "ligo_waveforms": {
        "classification": "empirical_comparison",
        "diagnosis": "Observer-memory proxy alignment remains weak. The main issue is model sufficiency relative to waveform morphology, not dataset access.",
        "implemented": "Residual-envelope diagnostics and clearer weak-fit documentation.",
        "deferred": "A richer waveform-adapter family would be needed for stronger proxy alignment.",
    },
    "ligo_ringdown": {
        "classification": "empirical_comparison",
        "diagnosis": "Ringdown alignment is limited by proxy projection quality and short noisy segment selection. The baseline remains competitive or better under the same window.",
        "implemented": "Window alignment, raw/normalized strain columns, bounded TNE projection search, holdout diagnostics, and residual-envelope outputs.",
        "deferred": "A stronger reduced-order TNE waveform family would be required to outperform the damped-sinusoid baseline consistently.",
    },
}


def _metric_value(row: dict[str, Any], key: str) -> float | str:
    value = row.get(key, "")
    try:
        return float(value)
    except Exception:
        return value


def generate_empirical_audit(
    summary_rows: list[dict[str, Any]],
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    notes = []
    for row in summary_rows:
        dataset = str(row["empirical_dataset"])
        note = MODEL_NOTES[dataset]
        notes.append(
            {
                "model": row["model"],
                "empirical_dataset": dataset,
                "data_status": row["data_status"],
                "comparison_type": row["comparison_type"],
                "RMSE": _metric_value(row, "RMSE"),
                "MAE": _metric_value(row, "MAE"),
                "R2": _metric_value(row, "R2"),
                "chi_square": _metric_value(row, "chi_square"),
                "AIC": _metric_value(row, "AIC"),
                "BIC": _metric_value(row, "BIC"),
                "baseline_model": row.get("baseline_model", ""),
                "limitations": row.get("limitations", ""),
                "classification": note["classification"],
                "diagnosis": note["diagnosis"],
                "implemented_improvements": note["implemented"],
                "deferred_improvements": note["deferred"],
            }
        )

    paths = audit_paths(output_dir)
    save_rows(paths["metrics"], notes)
    write_manifest(
        paths["manifest"],
        {
            "run": "run6_empirical_audit",
            "rows": notes,
            "classification_groups": {
                "empirical_comparisons": [row["empirical_dataset"] for row in notes],
                "theoretical_benchmarks": ["hawking_theoretical_benchmark"],
                "internal_consistency_diagnostics": ["noether_tne", "fp_gauss"],
            },
            "limitations": "Audit diagnoses preliminary model-to-observable alignment only; it is not an empirical validation layer.",
        },
    )

    lines = [
        "# Run 6 Empirical Audit",
        "",
        "This report audits the current empirical comparison outputs after the Run 6 mapping-improvement pass. It remains a preliminary observable-mapping audit, not an empirical validation claim.",
        "",
        "## Current Comparison Summary",
        "",
        "| Dataset | Status | RMSE | MAE | R2 | Baseline |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in notes:
        lines.append(
            f"| {row['empirical_dataset']} | {row['data_status']} | {float(row['RMSE']):.6f} | "
            f"{float(row['MAE']):.6f} | {float(row['R2']):.6f} | {row['baseline_model']} |"
        )
    lines.extend(
        [
            "",
            "## Diagnosis by Model",
            "",
        ]
    )
    for row in notes:
        lines.extend(
            [
                f"### {row['empirical_dataset']}",
                "",
                f"- classification: {row['classification']}",
                f"- current limitation: {row['limitations']}",
                f"- diagnosis: {row['diagnosis']}",
                f"- implemented in Run 6: {row['implemented_improvements']}",
                f"- deferred: {row['deferred_improvements']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Classification Split",
            "",
            "- empirical comparisons: redshift, galaxy rotation, EHT horizon, observer memory, elastic-pi ringdown",
            "- theoretical benchmarks: Hawking temperature/power/evaporation/spectrum comparison",
            "- internal consistency diagnostics: Noether/fp-Gauss remain outside the empirical summary",
            "",
            "## Claim Boundary",
            "",
            "Improved fit metrics, if any, are preliminary model-to-observable comparison results under explicit proxy mappings. Residual diagnostics here do not establish empirical validation of TNE.",
        ]
    )
    write_report(paths["report"], "\n".join(lines))
    return paths
