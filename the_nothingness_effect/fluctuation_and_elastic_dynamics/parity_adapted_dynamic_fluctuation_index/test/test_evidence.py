"""Exercise parity-conditioned DFI contracts and colocate test evidence."""

from pathlib import Path

from the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.contracts import contracts
from the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.simulation.run_contract_suite import run_suite
from the_nothingness_effect._runtime.artifacts.module_evidence import run_module_evidence


def run_all(output_dir: str | Path | None = None, *, seed: int = 0):
    assert contracts()
    output = Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent
    return run_module_evidence("parity_dfi", run_suite, output, seed=seed, simulation=False)


def test_parity_dfi_evidence(tmp_path: Path) -> None:
    result = run_all(tmp_path)
    assert result["contract_count"] >= 3
    assert result["manifest"].is_file()


if __name__ == "__main__":
    print(run_all())
