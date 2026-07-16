"""Producer-local residual evidence shared by theorem module test/simulation scripts."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from the_nothingness_effect._runtime.artifacts.io import save_csv, write_metadata
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import git_commit, parameter_hash


ContractRunner = Callable[..., dict[str, Any]]
START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"
CANONICAL_MODULES = {
    "cosmological_spark_dynamics": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.emergent_cosmological_spark_dynamics",
    "dtqc": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint",
    "elastic_dubler_interferometry": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature",
    "elastic_pi_norm": "the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi_norm",
    "mathematical_closure": "the_nothingness_effect.mathematical_architecture",
    "parity_dfi": "the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index",
}


def _read_residuals(path: Path) -> tuple[list[str], np.ndarray, list[str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    identifiers = [row.get("theorem_complex_id", f"contract_{index}") for index, row in enumerate(rows)]
    residuals = np.asarray(
        [float(row.get("residual_norm", row.get("residual", 0.0))) for row in rows],
        dtype=float,
    )
    statuses = [row.get("closure_status", "unknown") for row in rows]
    if not rows or not np.all(np.isfinite(residuals)):
        raise ValueError("Contract evidence requires at least one explicit finite residual row")
    return identifiers, residuals, statuses


def _save_residual_animation(path: Path, module: str, residuals: np.ndarray, *, frame_count: int) -> Path:
    figure, axis = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    x_values = np.arange(len(residuals))
    bars = axis.bar(x_values, np.zeros_like(residuals), color="#4c78a8")
    ceiling = max(float(np.max(np.abs(residuals))) * 1.15, 1e-12)
    axis.set(xlabel="contract index", ylabel="revealed residual", ylim=(0.0, ceiling))

    def update(frame: int):
        fraction = (frame + 1) / frame_count
        for index, bar in enumerate(bars):
            reveal = min(max(fraction * len(residuals) - index, 0.0), 1.0)
            bar.set_height(float(abs(residuals[index])) * reveal)
        axis.set_title(f"{module} residual trace: {fraction:0.0%}")
        return tuple(bars)

    movie = animation.FuncAnimation(figure, update, frames=frame_count, interval=90, blit=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    movie.save(path, writer=animation.PillowWriter(fps=10), dpi=100)
    plt.close(figure)
    return path


def run_module_evidence(
    module: str,
    contract_runner: ContractRunner,
    output_dir: str | Path,
    *,
    seed: int = 0,
    simulation: bool = False,
) -> dict[str, Any]:
    """Run canonical contracts and colocate their data, figure, animation, and manifest."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    mode = "simulation" if simulation else "test"
    contract_outputs = contract_runner(output, seed=seed)
    metrics = Path(contract_outputs["metrics"])
    identifiers, residuals, statuses = _read_residuals(metrics)
    trace_rows = [
        {
            "step": index,
            "theorem_complex_id": identifier,
            "residual": float(residual),
            "cumulative_residual_norm": float(np.linalg.vector_norm(residuals[: index + 1])),
            "closure_status": statuses[index],
        }
        for index, (identifier, residual) in enumerate(zip(identifiers, residuals, strict=True))
    ]
    trace = save_csv(output / f"{module}_{mode}_residual_trace.csv", trace_rows)
    movie = _save_residual_animation(
        output / f"{module}_{mode}_residual_animation.gif",
        module,
        residuals,
        frame_count=18 if simulation else 12,
    )
    generated = [metrics.name, Path(contract_outputs["figure"]).name, trace.name, movie.name]
    generated.extend(Path(path).name for path in contract_outputs.get("manifests", ()))
    parameters = {"module": module, "mode": mode, "seed": seed, "contract_count": len(identifiers)}
    manifest = write_metadata(
        output / f"{module}_{mode}_evidence_manifest.json",
        {
            "module": module,
            "mode": mode,
            "repository_start_commit": START_COMMIT,
            "repository_result_commit": git_commit(Path(__file__).resolve().parents[2]),
            "parameters": parameters,
            "parameter_hash": parameter_hash(parameters),
            "seed": seed,
            "numeric_tolerances": {"absolute": 1e-10},
            "residual_vector": [float(value) for value in residuals],
            "closure_statuses": statuses,
            "generated_files": generated,
            "regeneration_command": f"python -m {CANONICAL_MODULES[module]}.{mode}.run_evidence",
            "source_status": "canonical_contract_evaluation",
        },
    )
    return {
        "contract_outputs": contract_outputs,
        "contract_count": len(identifiers),
        "trace": trace,
        "animation": movie,
        "manifest": manifest,
    }
