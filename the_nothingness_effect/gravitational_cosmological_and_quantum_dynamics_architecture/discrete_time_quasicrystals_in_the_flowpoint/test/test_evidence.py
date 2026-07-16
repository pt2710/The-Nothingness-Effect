"""Exercise DTQC contracts and regenerate static/dynamic visual evidence."""

from pathlib import Path

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.contracts import contracts
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.simulation.run_contract_suite import run_suite
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.visualization import run_dtqc_evidence


def run_all(output_dir: str | Path | None = None, *, seed: int = 0):
    assert contracts()
    output = Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent / "artifacts"
    return run_dtqc_evidence(run_suite, output, seed=seed, simulation=False)


def test_dtqc_static_and_dynamic_evidence(tmp_path: Path) -> None:
    result = run_all(tmp_path)
    assert set(result["visuals"]) == {"contour", "diffraction", "wavelet", "dfi", "elastic_pi"}
    assert result["dtqc_animation"].is_file()


if __name__ == "__main__":
    print(run_all())
