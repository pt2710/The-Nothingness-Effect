"""Simulate Elastic Dubler Interferometry with producer-local artifacts."""

from pathlib import Path

from equations.elastic_dubler_interferometry.contracts import contracts
from equations.elastic_dubler_interferometry.simulation.run_contract_suite import run_suite
from tne_runtime.artifacts.module_evidence import run_module_evidence


def run_all(output_dir: str | Path | None = None, *, seed: int = 0):
    assert contracts()
    output = Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent
    return run_module_evidence("elastic_dubler_interferometry", run_suite, output, seed=seed, simulation=True)


if __name__ == "__main__":
    print(run_all())
