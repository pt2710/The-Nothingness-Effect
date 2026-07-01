"""Generate all missing TNE paper figure support artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from simulations.run_black_hole_dynamics_section18 import run as run_section18
from simulations.run_dubler_effect_figure31 import run as run_section15
from simulations.run_elastic_pi_ripple_figure7 import run as run_section19
from simulations.run_locality_spiral_figure6 import run as run_section16
from simulations.run_noether_figures48_49 import run as run_section23
from utils.output_io import CLAIM_BOUNDARY, save_csv, write_metadata


def run(output_dir: str | Path = "outputs", quick: bool = False) -> dict[str, Path | list[dict]]:
    root = Path(output_dir)
    section15 = run_section15(root, quick=quick)
    section16 = run_section16(root, quick=quick)
    section18 = run_section18(root, quick=quick)
    section19 = run_section19(root, quick=quick)
    section23 = run_section23(root, quick=quick)

    rows = [
        _summary_row("15.4", "Figure 31", section15["figure"], section15["data"], section15["metrics"], section15["passed_validation"], "Dubler shift numerical support figure."),
        _summary_row("16.4", "Figure 6", section16["figure"], section16["data"], section16["metrics"], section16["passed_validation"], "Locality-driven spiral finite toy model."),
        _summary_row("18.6/18.13", "Section 18 artifacts", ";".join(str(path.as_posix()) for path in section18["figures"].values()), section18["data"], section18["metrics"], section18["passed_validation"], "Elastic-pi horizon, radiation proxy, observer memory, feasibility."),
        _summary_row("19.4", "Figure 7", section19["figure"], section19["data"], section19["metrics"], section19["passed_validation"], "Elastic-pi ripple ringdown support figure."),
        _summary_row("23.4", "Figures 48-49/Table 19", f"{section23['figure48'].as_posix()};{section23['figure49'].as_posix()}", ";".join(str(path.as_posix()) for path in section23["data"]), section23["metrics"], section23["passed_validation"], "Noether phase-shift and fp-Gauss validation metrics."),
    ]
    summary_path = root / "metrics" / "missing_paper_figures_summary.csv"
    metadata_path = root / "data" / "missing_paper_figures_metadata.json"
    save_csv(summary_path, rows)
    write_metadata(
        metadata_path,
        {
            "script": "simulations.run_missing_paper_figures",
            "sections": ["15.4", "16.4", "18.6/18.13", "19.4", "23.4"],
            "parameters": {"quick": quick},
            "random_seed": "section-specific deterministic defaults",
            "output_files": {
                "summary": str(summary_path.as_posix()),
                "metadata": str(metadata_path.as_posix()),
            },
        },
    )
    print("Generated all missing TNE paper computational support artifacts.")
    for row in rows:
        print(f"{row['section']} {row['figure_or_table']}: {row['passed_validation']}")
    print(f"Scope: {CLAIM_BOUNDARY}")
    return {"summary": summary_path, "metadata": metadata_path, "rows": rows}


def _summary_row(
    section: str,
    figure: str,
    output_path: object,
    data_path: object,
    metrics_path: object,
    passed_validation: object,
    notes: str,
) -> dict[str, object]:
    return {
        "section": section,
        "figure_or_table": figure,
        "output_path": str(output_path),
        "data_path": str(data_path),
        "metrics_path": str(metrics_path),
        "passed_validation": bool(passed_validation),
        "notes": notes,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate all missing TNE paper figure artifacts.")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    run(args.output_dir, quick=args.quick)


if __name__ == "__main__":
    main()
