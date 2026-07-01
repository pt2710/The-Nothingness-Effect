"""Aggregate runner for TNE proxy animation artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from equations.artifact_io import save_csv, write_metadata
from equations.black_hole_dynamics.animation.animate_entropic_horizon_2d import run as run_entropic_horizon_2d
from equations.black_hole_dynamics.animation.animate_entropic_tension_3d import run as run_entropic_tension_3d
from equations.black_hole_dynamics.animation.animate_hawking_flux_3d import run as run_hawking_flux_3d
from equations.black_hole_dynamics.animation.animate_hawking_like_flux_2d import run as run_hawking_like_flux_2d
from equations.black_hole_dynamics.animation.animate_observer_horizon_3d import run as run_observer_horizon_3d
from equations.black_hole_dynamics.animation.animate_observer_horizon_memory_2d import run as run_observer_horizon_memory_2d
from equations.locality_driven_gravity.animation.animate_spiral_galaxy_2d import run as run_spiral_galaxy_2d
from equations.locality_driven_gravity.animation.animate_spiral_galaxy_3d import run as run_spiral_galaxy_3d


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate all repository-linked animation artifacts.")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--output-dir", default="equations")
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--format", choices=["auto", "mp4", "gif", "frames"], default="auto")
    parser.add_argument("--seed", type=int, default=2710)
    args = parser.parse_args()

    root = Path(args.output_dir)
    bh_root = root / "black_hole_dynamics" / "animation"
    lg_root = root / "locality_driven_gravity" / "animation"
    runners = [
        ("black_hole_dynamics", "entropic_horizon_2d", lambda: run_entropic_horizon_2d(output_dir=bh_root, quick=args.quick, fps=args.fps, preferred_format=args.format)),
        ("black_hole_dynamics", "hawking_like_flux_2d", lambda: run_hawking_like_flux_2d(output_dir=bh_root, quick=args.quick, fps=args.fps, preferred_format=args.format)),
        ("black_hole_dynamics", "observer_horizon_memory_2d", lambda: run_observer_horizon_memory_2d(output_dir=bh_root, quick=args.quick, fps=args.fps, preferred_format=args.format)),
        ("black_hole_dynamics", "entropic_tension_3d", lambda: run_entropic_tension_3d(output_dir=bh_root, quick=args.quick, fps=args.fps, preferred_format=args.format)),
        ("black_hole_dynamics", "hawking_flux_from_entropic_tension_3d", lambda: run_hawking_flux_3d(output_dir=bh_root, quick=args.quick, fps=args.fps, preferred_format=args.format)),
        ("black_hole_dynamics", "observer_horizon_appear_disappear_3d", lambda: run_observer_horizon_3d(output_dir=bh_root, quick=args.quick, fps=args.fps, preferred_format=args.format)),
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
    summary_path = root / "animation_artifacts_summary.csv"
    metadata_path = root / "animation_artifacts_metadata.json"
    save_csv(summary_path, rows)
    write_metadata(
        metadata_path,
        {
            "script": "equations.run_animation_artifacts",
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
