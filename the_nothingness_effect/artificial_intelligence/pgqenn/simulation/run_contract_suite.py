"""Generate PGQENN metrics, graph figure, and provenance manifests."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import torch

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure
from the_nothingness_effect.artificial_intelligence.pgqenn.contracts import APPENDIX, APPENDIX_SHA256, PGQENNContractInput, contracts
from the_nothingness_effect.artificial_intelligence.pgqenn.growth_law import CanonicalPrimeGrowth
from the_nothingness_effect._runtime.theorem_complex_runtime import ComplexId, SimulationResult
from the_nothingness_effect._runtime.theorem_complex_runtime.artifacts import write_artifact_manifest
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import build_manifest, git_commit


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def fixture(seed: int = 0) -> PGQENNContractInput:
    generator = torch.Generator().manual_seed(seed)
    graph = CanonicalPrimeGrowth().build(11)
    base = torch.linspace(0.3, 1.1, 6).repeat(11, 1)
    features = base + 0.04 * torch.randn((11, 6), generator=generator)
    return PGQENNContractInput(graph, features)


def run_suite(output_dir: str | Path, *, seed: int = 0):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    value = fixture(seed)
    evaluations = [(contract, evaluate_contract(contract, value)) for contract in contracts()]
    rows = [{
        "theorem_complex_id": str(contract.complex_id), "level": contract.level.value,
        "residual_norm": 0.0 if evaluation.residual is None else evaluation.residual.norm,
        "closure_status": evaluation.status.value, "exact_semantics": contract.exact_semantics,
    } for contract, evaluation in evaluations]
    metrics = save_csv(output / "pgqenn_contract_metrics.csv", rows)
    figure_handle, axis = plt.subplots(figsize=(7.2, 5.2), constrained_layout=True)
    angles = torch.linspace(0.0, 2.0 * torch.pi, len(value.graph.primes) + 1)[:-1]
    x, y = torch.cos(angles), torch.sin(angles)
    adjacency = value.graph.adjacency
    for first in range(len(value.graph.primes)):
        for second in range(first + 1, len(value.graph.primes)):
            if adjacency[first, second] > 0:
                axis.plot((x[first], x[second]), (y[first], y[second]), color="0.75", linewidth=float(adjacency[first, second]))
    axis.scatter(x, y, c=[depth.value for depth in value.graph.two_adic_depths], cmap="viridis", s=90)
    for index, prime in enumerate(value.graph.primes):
        axis.text(float(x[index]), float(y[index]), str(prime), ha="center", va="center", fontsize=7)
    axis.set(title="Canonical prime/parity PGQENN graph", aspect="equal")
    axis.axis("off")
    figure = save_figure(figure_handle, output / "pgqenn_prime_graph.png", dpi=160)
    plt.close(figure_handle)
    commit = git_commit(Path(__file__).resolve().parents[4])
    manifests = []
    for contract, evaluation in evaluations:
        residual = () if evaluation.residual is None else evaluation.residual.vector
        simulation = SimulationResult(
            ComplexId(str(contract.complex_id)), evaluation.status,
            {"module": "pgqenn", "fixture": "prime-graph-v1", "node_count": len(value.graph.primes), "growth_mode": value.graph.growth_mode},
            seed, {"absolute": value.tolerance}, tuple(float(item) for item in residual),
            (metrics.name, figure.name), {"exact_semantics": contract.exact_semantics, "device": "cpu"},
        )
        manifests.append(write_artifact_manifest(
            output / f"{contract.complex_id}_manifest.json",
            build_manifest(
                simulation, appendix_filename=APPENDIX, appendix_source_sha256=APPENDIX_SHA256,
                repository_start_commit=START_COMMIT, repository_result_commit=commit,
                regeneration_command=f"python -m the_nothingness_effect.artificial_intelligence.pgqenn.simulation.run_contract_suite --output {output.as_posix()}",
            ),
        ))
    return {"metrics": metrics, "figure": figure, "manifests": manifests}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "artifacts")
    parser.add_argument("--seed", type=int, default=0)
    arguments = parser.parse_args()
    print(run_suite(arguments.output, seed=arguments.seed))
