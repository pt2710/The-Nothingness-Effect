from pathlib import Path
import argparse

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.authoritative_contract_artifacts import run_active_suite
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.contracts import contracts


def run_suite(output_dir: str | Path, *, seed: int = 0):
    return run_active_suite(
        "locality_driven_gravity",
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
