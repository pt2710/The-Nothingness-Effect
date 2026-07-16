"""Run one canonical TNE AI architecture across all six observable outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from the_nothingness_effect.artificial_intelligence.shared.capability_artifacts import CAPABILITIES, run_capability
from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure, write_metadata
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import git_commit, parameter_hash
from the_nothingness_effect.artificial_intelligence.shared.network_artifacts import (
    generate_architecture_network_artifacts,
)


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def _architecture_input(architecture: str, seed: int) -> tuple[tuple[Any, ...], dict[str, int]]:
    generator = torch.Generator().manual_seed(seed)
    if architecture == "qenn":
        signal = torch.linspace(0.2, 1.4, 16).repeat(12, 1)
        signal = signal + 0.025 * torch.randn(signal.shape, generator=generator)
        return (signal,), {"input_dim": 16, "hidden_dim": 12, "output_dim": 6}
    if architecture == "pgqenn":
        base = torch.linspace(0.3, 1.1, 6).repeat(13, 1)
        features = base + 0.03 * torch.randn(base.shape, generator=generator)
        return (features,), {"input_dim": 6, "hidden_dim": 12, "output_dim": 6}
    if architecture == "soinets":
        position = torch.linspace(0.2, 1.4, 18)
        features = torch.stack((position, position.square(), torch.sin(position), torch.cos(position)), dim=-1)
        qenn_features = features + 0.01 * torch.randn(features.shape, generator=generator)
        pgqenn_features = 1.1 * features + 0.01 * torch.randn(features.shape, generator=generator)
        return (qenn_features, pgqenn_features), {"input_dim": 4, "hidden_dim": 12, "output_dim": 6}
    raise ValueError(f"Unknown architecture {architecture!r}")


def _evaluate_architecture(architecture: str, model_type: type[Any], seed: int) -> dict[str, Any]:
    torch.manual_seed(seed)
    inputs, dimensions = _architecture_input(architecture, seed)
    model = model_type(**dimensions)
    model.eval()
    with torch.no_grad():
        result = model(*inputs)
    residuals = {name: float(value.detach().cpu()) for name, value in result.residuals.items()}
    observation = [float(value) for value in result.observation.detach().cpu().reshape(-1)]
    return {
        "residuals": residuals,
        "observation": observation,
        "closure_status": result.closure_status.value,
        "metadata": dict(result.metadata),
    }


def run_architecture_capability_suite(
    architecture: str,
    model_type: type[Any],
    output_dir: str | Path,
    *,
    seed: int = 0,
    simulation: bool = False,
) -> dict[str, Any]:
    """Exercise the architecture and all six color/sound output groups."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    mode = "simulation" if simulation else "test"
    architecture_result = _evaluate_architecture(architecture, model_type, seed)
    network = generate_architecture_network_artifacts(
        architecture,
        output,
        observation=architecture_result["observation"],
        residuals=architecture_result["residuals"],
        seed=seed,
        simulation=simulation,
    )
    capability_results: dict[str, dict[str, Any]] = {}
    for offset, capability in enumerate(CAPABILITIES):
        capability_results[capability] = run_capability(
            capability,
            output / capability,
            seed=seed + offset,
            simulation=simulation,
            producer_architecture=architecture,
            producer_module=f"the_nothingness_effect.artificial_intelligence.{architecture}.{mode}.run_all_capabilities",
        )

    rows = []
    for capability, result in capability_results.items():
        evaluation = result["evaluation"]
        rows.append(
            {
                "architecture": architecture,
                "mode": mode,
                "output_group": capability,
                "closure_status": evaluation.closure_status,
                "residual_norm": sum(value * value for value in evaluation.residuals) ** 0.5,
                **evaluation.metrics,
            }
        )
    summary = save_csv(output / f"{architecture}_{mode}_six_output_summary.csv", rows)
    figure_handle, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), constrained_layout=True)
    residual_names = list(architecture_result["residuals"])
    axes[0].bar(range(len(residual_names)), list(architecture_result["residuals"].values()), color="#4c78a8")
    axes[0].set_xticks(range(len(residual_names)), residual_names, rotation=35, ha="right")
    axes[0].set(title=f"{architecture.upper()} residuals", ylabel="residual")
    axes[1].bar(range(len(architecture_result["observation"])), architecture_result["observation"], color="#f58518")
    axes[1].set(title="Architecture observation/collapse", xlabel="output index", ylabel="probability")
    figure = save_figure(figure_handle, output / f"{architecture}_{mode}_architecture_figure.png", dpi=160)
    plt.close(figure_handle)

    generated = [summary.name, figure.name]
    generated.extend(
        path.name
        for path in (
            *network["figures"],
            network["table"],
            *network["animations"],
            network["manifest"],
        )
    )
    for capability, result in capability_results.items():
        generated.extend(
            f"{capability}/{Path(path).name}"
            for path in result["generated_files"]
        )
    parameters = {
        "architecture": architecture,
        "mode": mode,
        "seed": seed,
        "output_groups": list(CAPABILITIES),
    }
    manifest = write_metadata(
        output / f"{architecture}_{mode}_six_output_manifest.json",
        {
            "architecture": architecture,
            "output_groups": list(CAPABILITIES),
            "capability_count": len(CAPABILITIES),
            "repository_start_commit": START_COMMIT,
            "repository_result_commit": git_commit(Path(__file__).resolve().parents[3]),
            "parameters": parameters,
            "parameter_hash": parameter_hash(parameters),
            "seed": seed,
            "architecture_closure_status": architecture_result["closure_status"],
            "architecture_residuals": architecture_result["residuals"],
            "architecture_metadata": architecture_result["metadata"],
            "generated_files": generated,
            "regeneration_command": (
                f"python -m the_nothingness_effect.artificial_intelligence.{architecture}.{mode}.run_all_capabilities"
            ),
            "source_status": "synthetic_deterministic_fixture",
        },
    )
    return {
        "architecture": architecture_result,
        "capabilities": capability_results,
        "capability_count": len(capability_results),
        "summary": summary,
        "figure": figure,
        "manifest": manifest,
        "network": network,
    }
