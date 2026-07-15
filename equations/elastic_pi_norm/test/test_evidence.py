"""Exercise Elastic-pi norm contracts and colocate test evidence."""

from pathlib import Path

from equations.elastic_pi_norm.contracts import contracts
from equations.elastic_pi_norm.simulation.run_contract_suite import run_suite
from tne_runtime.artifacts.module_evidence import run_module_evidence


def run_all(output_dir: str | Path | None = None, *, seed: int = 0):
    assert contracts()
    output = Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent
    return run_module_evidence("elastic_pi_norm", run_suite, output, seed=seed, simulation=False)


def test_elastic_pi_norm_evidence(tmp_path: Path) -> None:
    result = run_all(tmp_path)
    assert result["contract_count"] >= 3
    assert result["trace"].is_file()


if __name__ == "__main__":
    print(run_all())
