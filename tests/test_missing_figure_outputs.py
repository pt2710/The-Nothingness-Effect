from pathlib import Path

from simulations.run_missing_paper_figures import run


REQUIRED_OUTPUTS = [
    "figures/section15/figure31_dubler_shift_entropy_gradient.png",
    "figures/section16/figure6_locality_driven_spiral.png",
    "figures/section18/section18_elastic_pi_entropic_horizon.png",
    "figures/section18/section18_hawking_like_entropic_radiation.png",
    "figures/section18/section18_observer_horizon_memory.png",
    "figures/section18/section18_computational_feasibility.png",
    "figures/section19/figure7_elastic_pi_ripple_ringdown.png",
    "figures/section23/figure48_kd_flux_phase_shift.png",
    "figures/section23/figure49_fp_gauss_identity_128x128.png",
    "metrics/section23/table19_noether_validation_metrics.csv",
]


def test_aggregate_runner_generates_required_outputs(tmp_path: Path):
    run(tmp_path, quick=True)
    for relative_path in REQUIRED_OUTPUTS:
        path = tmp_path / relative_path
        assert path.exists(), relative_path
        assert path.stat().st_size > 0
