import csv
import json
from pathlib import Path

from the_nothingness_effect.the_completeness_theorem.simulation.run_completeness_supplementary import (
    main as run_completeness_supplementary,
)
from the_nothingness_effect.the_completeness_theorem.simulation.run_godel_boundary_figures import (
    main as run_godel_boundary_figures,
)


REQUIRED_TRACES = [
    "godel_boundary_trace.json",
    "fully_pairable_system_trace.json",
    "missing_dual_system_trace.json",
    "circular_dependency_system_trace.json",
    "contradiction_system_trace.json",
    "unpaired_boundary_system_trace.json",
]

REQUIRED_METRICS = [
    "closure_iteration_metrics.csv",
    "duality_pair_coverage.csv",
    "closure_failure_modes.csv",
    "fixed_point_summary.csv",
]

REQUIRED_FIGURES = [
    "godel_boundary_graph.png",
    "dual_closure_lattice.png",
    "closure_iteration_trace.png",
    "incompleteness_vs_dual_closure_phase.png",
    "closure_fixed_point_trace.png",
    "duality_pair_coverage.png",
    "closure_failure_modes.png",
    "completeness_operator_convergence.png",
    "closure_state_space_projection.png",
]


def test_runner_scripts_generate_required_outputs(tmp_path: Path):
    output_root = tmp_path / "supplementary"
    run_godel_boundary_figures(output_root)
    run_completeness_supplementary(output_root)

    for filename in REQUIRED_TRACES:
        path = output_root / "traces" / filename
        assert path.exists(), filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert "finite illustrative model" in payload["claim_boundary"]
        assert "not a formal proof substitute" in payload["claim_boundary"]
        assert payload["steps"]

    for filename in REQUIRED_METRICS:
        path = output_root / "metrics" / filename
        assert path.exists(), filename
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        assert rows, filename
        assert "scope_note" in rows[0]
        assert "not a formal proof substitute" in rows[0]["scope_note"]

    for filename in REQUIRED_FIGURES:
        path = output_root / "figures" / filename
        assert path.exists(), filename
        assert path.stat().st_size > 0

