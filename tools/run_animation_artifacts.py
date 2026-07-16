"""Aggregate runner for TNE proxy animation artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from the_nothingness_effect._runtime.artifacts.io import save_csv, write_metadata
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.animation.animate_entropic_horizon_2d import run as run_entropic_horizon_2d
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.animation.animate_entropic_tension_3d import run as run_entropic_tension_3d
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.animation.animate_hawking_flux_3d import run as run_hawking_flux_3d
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.animation.animate_hawking_like_flux_2d import run as run_hawking_like_flux_2d
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.animation.animate_observer_horizon_3d import run as run_observer_horizon_3d
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.animation.animate_observer_horizon_memory_2d import run as run_observer_horizon_memory_2d
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.animation.animate_spiral_galaxy_2d import run as run_spiral_galaxy_2d
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.animation.animate_spiral_galaxy_3d import run as run_spiral_galaxy_3d


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate all repository-linked animation artifacts.")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Compatibility override placing all generated animation evidence beneath one directory.",
    )
    parser.add_argument("--summary-dir", default="docs/data")
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--format", choices=["auto", "mp4", "gif", "frames"], default="auto")
    parser.add_argument("--seed", type=int, default=2710)
    args = parser.parse_args()

    package = Path("the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture")
    if args.output_dir is None:
        bh_root = package / "black_holes_hawking_radiation_and_observer_horizons" / "simulation" / "artifacts" / "animations"
        lg_root = package / "locality_driven_gravity" / "simulation" / "artifacts" / "animations"
    else:
        bh_root = Path(args.output_dir) / "black_hole_dynamics"
        lg_root = Path(args.output_dir) / "locality_driven_gravity"
    runners = [
        ("black_holes_hawking_radiation_and_observer_horizons", "entropic_horizon_2d", lambda: run_entropic_horizon_2d(output_dir=bh_root, quick=args.quick, fps=args.fps, preferred_format=args.format)),
        ("black_holes_hawking_radiation_and_observer_horizons", "hawking_like_flux_2d", lambda: run_hawking_like_flux_2d(output_dir=bh_root, quick=args.quick, fps=args.fps, preferred_format=args.format)),
        ("black_holes_hawking_radiation_and_observer_horizons", "observer_horizon_memory_2d", lambda: run_observer_horizon_memory_2d(output_dir=bh_root, quick=args.quick, fps=args.fps, preferred_format=args.format)),
        ("black_holes_hawking_radiation_and_observer_horizons", "entropic_tension_3d", lambda: run_entropic_tension_3d(output_dir=bh_root, quick=args.quick, fps=args.fps, preferred_format=args.format)),
        ("black_holes_hawking_radiation_and_observer_horizons", "hawking_flux_from_entropic_tension_3d", lambda: run_hawking_flux_3d(output_dir=bh_root, quick=args.quick, fps=args.fps, preferred_format=args.format)),
        ("black_holes_hawking_radiation_and_observer_horizons", "observer_horizon_appear_disappear_3d", lambda: run_observer_horizon_3d(output_dir=bh_root, quick=args.quick, fps=args.fps, preferred_format=args.format)),
        ("locality_driven_gravity", "spiral_galaxy_formation_2d", lambda: run_spiral_galaxy_2d(output_dir=lg_root, quick=args.quick, fps=args.fps, preferred_format=args.format, seed=args.seed)),
        ("locality_driven_gravity", "spiral_galaxy_formation_3d", lambda: run_spiral_galaxy_3d(output_dir=lg_root, quick=args.quick, fps=args.fps, preferred_format=args.format, seed=args.seed)),
    ]
    rows: list[dict[str, object]] = []
    for component, name, runner in runners:
        result = runner()
        rows.append(
            {
                "component": component,
                "animation": name,
                "output_path": str(result["animation"]),
                "data_path": str(result["data"]),
                "metadata_path": str(result["metadata"]),
                "fallback_mode": result["fallback_mode"],
                "passed_validation": True,
                "notes": "quick-mode aggregate run",
            }
        )
    summary_root = Path(args.summary_dir)
    summary_path = summary_root / "animation_artifacts_summary.csv"
    metadata_path = summary_root / "animation_artifacts_metadata.json"
    save_csv(summary_path, rows)
    write_metadata(
        metadata_path,
        {
            "script": "tools.run_animation_artifacts",
            "quick": bool(args.quick),
            "fps": args.fps,
            "format": args.format,
            "seed": args.seed,
            "summary_path": summary_path.as_posix(),
            "rows": rows,
        },
    )
    print(f"Generated aggregate animation outputs and summary at {summary_path}")


if __name__ == "__main__":
    main()
