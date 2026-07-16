from __future__ import annotations

import csv
import json

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.finite_floquet_reference import (
    CLAIM_BOUNDARY,
    finite_floquet_benchmark,
    simulate_finite_floquet,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.simulation.simulate_discrete_time_quasicrystals_in_the_flowpoint import (
    run,
)


def test_finite_floquet_reference_is_unitary_and_period_doubled() -> None:
    canonical = simulate_finite_floquet(seed=0, flowpoint_enabled=True)
    ablation = simulate_finite_floquet(seed=0, flowpoint_enabled=False)

    assert float(canonical.unitarity_residual) <= 1e-9
    assert float(canonical.period_two_correlation) >= 0.5
    assert float(canonical.one_period_anticorrelation) >= 0.5
    assert float(canonical.subharmonic_fraction) >= 0.25
    assert float(canonical.subharmonic_fraction) > float(ablation.subharmonic_fraction)
    assert canonical.closure_status == "numerical_candidate"
    assert canonical.claim_boundary == CLAIM_BOUNDARY
    assert "thermodynamic-limit" in canonical.claim_boundary
    assert "formal physical" in canonical.claim_boundary


def test_finite_floquet_multiseed_benchmark_is_source_removal_sensitive() -> None:
    rows = finite_floquet_benchmark(seeds=(0, 1, 2))
    assert len(rows) == 3
    assert {row["seed"] for row in rows} == {0, 1, 2}
    assert all(float(row["unitarity_residual"]) <= 1e-9 for row in rows)
    assert all(float(row["subharmonic_source_removal_delta"]) > 0.0 for row in rows)
    assert all(row["closure_status"] == "numerical_candidate" for row in rows)
    assert all(row["claim_boundary"] == CLAIM_BOUNDARY for row in rows)


def test_dtqc_simulation_emits_bounded_floquet_reference_artifacts(tmp_path) -> None:
    inventory_path = run(tmp_path)
    assert inventory_path.is_file()

    expected = (
        "dtqc_runtime_summary.png",
        "dtqc_runtime_trajectory.gif",
        "dtqc_runtime_trace.csv",
        "dtqc_finite_floquet_reference.csv",
        "dtqc_finite_floquet_reference.png",
        "dtqc_finite_floquet_reference.json",
        "dtqc_runtime_manifest.json",
    )
    assert all((tmp_path / name).is_file() for name in expected)

    floquet_manifest = json.loads(
        (tmp_path / "dtqc_finite_floquet_reference.json").read_text(
            encoding="utf-8"
        )
    )
    assert floquet_manifest["source_status"] == "finite_many_body_floquet_reference"
    assert floquet_manifest["seed_count"] == 3
    assert floquet_manifest["claim_boundary"] == CLAIM_BOUNDARY
    assert floquet_manifest["subharmonic_fraction"] > floquet_manifest[
        "flowpoint_ablation_subharmonic_fraction"
    ]

    with (tmp_path / "dtqc_finite_floquet_reference.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 3
    assert all(float(row["subharmonic_source_removal_delta"]) > 0.0 for row in rows)

    runtime_manifest = json.loads(
        (tmp_path / "dtqc_runtime_manifest.json").read_text(encoding="utf-8")
    )
    assert runtime_manifest["finite_floquet_reference_manifest"] == (
        "dtqc_finite_floquet_reference.json"
    )
    assert "not a formal physical existence proof" in runtime_manifest[
        "claim_boundary"
    ]
