"""Generate finite completeness supplementary closure artifacts.

The outputs are deterministic toy-system traces, metrics, and figures for
repository-linked computational support. They do not replace mathematical
arguments in the manuscript.
"""

from __future__ import annotations

from pathlib import Path

from the_nothingness_effect.the_completeness_theorem.simulation.artifacts import (
    prepare_output_dirs,
    write_metrics,
    write_traces,
)
from the_nothingness_effect.the_completeness_theorem.simulation.dual_closure import DualClosureOperator
from the_nothingness_effect.the_completeness_theorem.simulation.godel_boundary import supplementary_systems
from the_nothingness_effect.the_completeness_theorem.simulation.visualization import save_supplementary_figures


def build_traces(max_steps: int = 8):
    operator = DualClosureOperator()
    return [operator.run(system, max_steps=max_steps) for system in supplementary_systems()]


def main(output_root: str | Path | None = None) -> dict[str, list[Path]]:
    dirs = prepare_output_dirs(Path(output_root) if output_root is not None else None)
    traces = build_traces()
    trace_paths = write_traces(traces, dirs["traces"])
    metrics_paths = write_metrics(traces, dirs["metrics"])
    figure_paths = save_supplementary_figures(traces, dirs["figures"])

    print("Generated finite completeness supplementary simulation artifacts.")
    print("Scope: finite toy systems; computational support artifacts; not formal proof substitutes.")
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

