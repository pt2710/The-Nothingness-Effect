from pathlib import Path
import argparse

from equations.fluctuation_elastic_artifacts import run_suite as _run


def run_suite(output_dir: str | Path, *, seed: int = 0):
    return _run("elastic_pi", output_dir, seed=seed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/elastic_pi"))
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    print(run_suite(args.output, seed=args.seed))
