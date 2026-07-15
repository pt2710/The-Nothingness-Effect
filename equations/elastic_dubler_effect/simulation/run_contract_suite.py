from pathlib import Path
import argparse
from equations.gravitational_cosmological_quantum_dynamics.contract_artifacts import run_suite as _run


def run_suite(output_dir: str | Path, *, seed: int = 0):
    return _run("elastic_dubler_effect", output_dir, seed=seed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/elastic_dubler_effect"))
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    print(run_suite(args.output, seed=args.seed))
