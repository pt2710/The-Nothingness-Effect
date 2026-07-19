"""Regenerate the complete tracked DTQC artifact tree."""

from __future__ import annotations

import argparse
from pathlib import Path

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.canonical_artifact_suite import (
    _bundle,
    generate_complete_canonical_artifacts,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.contracts import (
    contracts,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.quantum_wave_bridge import (
    generate_fp_quantum_artifacts,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.simulation.run_contract_suite import (
    finalize_artifact_tree,
    prepare_artifact_output,
    run_suite,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.visualization import (
    run_dtqc_evidence,
)


def run_all(
    output_dir: str | Path | None = None,
    *,
    seed: int = 0,
    generation_source_commit: str | None = None,
):
    assert contracts()
    output = (
        Path(output_dir)
        if output_dir is not None
        else Path(__file__).resolve().parent / "artifacts"
    )
    prepare_artifact_output(output)
    result = run_dtqc_evidence(run_suite, output, seed=seed, simulation=True)
    result["complete_canonical_artifacts"] = generate_complete_canonical_artifacts(
        output,
        seed=seed,
        simulation=True,
    )
    result["fp_quantum_wave_artifacts"] = generate_fp_quantum_artifacts(
        output,
        lambda phase: _bundle(48, phase),
        simulation=True,
    )
    result["artifact_tree"] = finalize_artifact_tree(
        output,
        generation_source_commit=generation_source_commit,
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--generation-source-commit")
    args = parser.parse_args()
    print(
        run_all(
            args.output,
            seed=args.seed,
            generation_source_commit=args.generation_source_commit,
        )
    )


if __name__ == "__main__":
    main()
