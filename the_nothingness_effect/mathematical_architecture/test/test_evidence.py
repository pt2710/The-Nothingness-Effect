"""Exercise mathematical closure source laws and colocate test evidence."""

from pathlib import Path

from the_nothingness_effect.mathematical_architecture.contracts import mathematical_closure_contracts
from the_nothingness_effect.mathematical_architecture.simulation.run_suite import run_suite
from the_nothingness_effect._runtime.artifacts.module_evidence import run_module_evidence


def run_all(output_dir: str | Path | None = None, *, seed: int = 0):
    assert mathematical_closure_contracts()
    output = Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent / "artifacts"
    return run_module_evidence("mathematical_closure", run_suite, output, seed=seed, simulation=False)


def test_mathematical_closure_evidence(tmp_path: Path) -> None:
    result = run_all(tmp_path)
    assert result["contract_count"] == 7
    assert result["animation"].is_file()


if __name__ == "__main__":
    print(run_all())
