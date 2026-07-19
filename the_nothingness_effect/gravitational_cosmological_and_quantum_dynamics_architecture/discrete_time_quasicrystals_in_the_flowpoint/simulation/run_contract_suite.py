from pathlib import Path
import argparse

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_artifacts import run_suite as _run

from .run_legacy_faithful_suite import run_legacy_faithful_suite


def run_suite(output_dir: str | Path, *, seed: int = 0):
    output = Path(output_dir)
    result = dict(_run("dtqc", output, seed=seed))
    result["legacy_faithful"] = run_legacy_faithful_suite(
        output / "legacy_faithful",
        seed=seed,
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    print(run_suite(args.output, seed=args.seed))
