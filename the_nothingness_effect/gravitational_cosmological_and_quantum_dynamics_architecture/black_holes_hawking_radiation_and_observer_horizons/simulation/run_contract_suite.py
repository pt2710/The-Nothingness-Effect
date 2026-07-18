from pathlib import Path
import argparse

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.authoritative_contract_artifacts import run_active_suite
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.contracts import contracts


def run_suite(output_dir: str | Path, *, seed: int = 0):
    return run_active_suite(
        "black_hole_dynamics",
        contracts(),
        output_dir,
        seed=seed,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "artifacts",
    )
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    print(run_suite(args.output, seed=args.seed))
