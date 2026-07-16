"""Simulate DTQC closure and regenerate static/dynamic visual evidence."""

from pathlib import Path

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.contracts import contracts
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.simulation.run_contract_suite import run_suite
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.visualization import run_dtqc_evidence


def run_all(output_dir: str | Path | None = None, *, seed: int = 0):
    assert contracts()
    output = Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent / "artifacts"
    return run_dtqc_evidence(run_suite, output, seed=seed, simulation=True)


if __name__ == "__main__":
    print(run_all())
