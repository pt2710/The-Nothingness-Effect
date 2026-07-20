from pathlib import Path
import argparse

from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.recertified_artifacts import run_suite as _run
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.extended_artifacts import run_suite as _run_extended


def run_suite(output_dir: str | Path, *, seed: int = 0):
    base = _run(output_dir, seed=seed)
    extended = _run_extended(output_dir, seed=seed)
    return {
        "metrics": base["metrics"],
        "figure": base["figure"],
        "extended_metrics": extended["metrics"],
        "manifests": [*base["manifests"], *extended["manifests"]],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "artifacts")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    print(run_suite(args.output, seed=args.seed))
