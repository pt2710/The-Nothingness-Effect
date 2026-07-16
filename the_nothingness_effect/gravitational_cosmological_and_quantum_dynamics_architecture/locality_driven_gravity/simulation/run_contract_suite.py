from pathlib import Path
import argparse
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_artifacts import run_suite as _run


def run_suite(output_dir: str | Path, *, seed: int = 0):
    return _run("locality_driven_gravity", output_dir, seed=seed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "artifacts")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    print(run_suite(args.output, seed=args.seed))
