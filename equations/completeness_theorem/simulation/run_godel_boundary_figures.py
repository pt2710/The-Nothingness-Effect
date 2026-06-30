"""Generate finite illustrative Godel-boundary dual-closure figures.

This runner creates repository-linked computational support artifacts. The
generated trace and figures are finite toy-model visualizations and are not a
formal proof substitute.
"""

from __future__ import annotations

from pathlib import Path

from equations.completeness_theorem.simulation.artifacts import (
    prepare_output_dirs,
    write_metrics,
    write_traces,
)
from equations.completeness_theorem.simulation.dual_closure import DualClosureOperator
from equations.completeness_theorem.simulation.godel_boundary import godel_boundary_system
from equations.completeness_theorem.simulation.visualization import save_godel_boundary_figures


def build_trace(max_steps: int = 8):
    operator = DualClosureOperator()
    return operator.run(godel_boundary_system(), max_steps=max_steps)


def main(output_root: str | Path | None = None) -> dict[str, list[Path]]:
    dirs = prepare_output_dirs(Path(output_root) if output_root is not None else None)
    trace = build_trace()
    trace_paths = write_traces([trace], dirs["traces"])
    metrics_paths = write_metrics([trace], dirs["metrics"])
    figure_paths = save_godel_boundary_figures(trace, dirs["figures"])

    print("Generated finite illustrative Godel-boundary artifacts.")
    print("Scope: computational support artifact; not a formal proof substitute.")
    print(f"Trace files: {len(trace_paths)}")
    print(f"Metric files: {len(metrics_paths)}")
    print(f"Figure files: {len(figure_paths)}")
    return {
        "traces": trace_paths,
        "metrics": metrics_paths,
        "figures": figure_paths,
    }


if __name__ == "__main__":
    main()

