"""Producer-local metrics and visual evidence for multimodal SOInets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
import torch

from the_nothingness_effect._runtime.artifacts.io import (
    ensure_dir,
    save_csv,
    save_figure,
    write_metadata,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import (
    git_commit,
    parameter_hash,
)

from .multimodal import MULTIMODAL_REFERENCE_SHA256, TNEMultimodalSOInet


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def _fixture(seed: int) -> dict[str, torch.Tensor]:
    generator = torch.Generator().manual_seed(seed)
    time = torch.linspace(0.0, 1.0, 64)
    phase = torch.linspace(0.0, torch.pi / 3.0, 8).unsqueeze(1)
    sound = torch.sin(2.0 * torch.pi * 5.0 * time.unsqueeze(0) + phase)
    return {
        "color": torch.rand((8, 3), generator=generator) + 0.1,
        "sound": sound.unsqueeze(1),
        "vision": torch.rand((8, 1, 8, 8), generator=generator),
    }


def run_multimodal_artifact_suite(
    output_dir: str | Path,
    *,
    seed: int = 0,
    simulation: bool = False,
) -> dict[str, Any]:
    output = ensure_dir(output_dir)
    torch.manual_seed(seed)
    model = TNEMultimodalSOInet(6, 8, 4)
    model.eval()
    with torch.no_grad():
        result = model(_fixture(seed))

    names = result.modality_names
    weights = result.modality_weights.detach().cpu()
    entropy = result.modality_entropy.detach().cpu()
    ratios = result.elastic_dubler_state.ratio.detach().cpu()
    rows = []
    for index, name in enumerate(names):
        reconstruction = result.reconstructed_tokens[name].detach().cpu()
        token = result.modality_tokens[:, index, :].detach().cpu()
        rows.append(
            {
                "modality": name,
                "mean_entropy": float(entropy[:, index].mean()),
                "mean_weight": float(weights[:, index].mean()),
                "token_reconstruction_rmse": float(
                    torch.sqrt(torch.mean((reconstruction - token) ** 2))
                ),
                "closure_status": result.closure_status.value,
            }
        )
    metrics = save_csv(output / "multimodal_soinet_metrics.csv", rows)

    figure_handle, axes = plt.subplots(
        1, 2, figsize=(10.5, 4.3), constrained_layout=True
    )
    axes[0].bar(names, weights.mean(dim=0).numpy(), color="#4c78a8")
    axes[0].set(
        title="Elastic Dubler modality precision",
        ylabel="mean normalized Elastic-pi weight",
        ylim=(0.0, 1.0),
    )
    ratio_mean = ratios.mean(dim=0).numpy()
    image = axes[1].imshow(ratio_mean, cmap="magma", aspect="equal")
    axes[1].set(
        title="Mean exact Dubler ratio",
        xticks=range(len(names)),
        yticks=range(len(names)),
        xticklabels=names,
        yticklabels=names,
    )
    figure_handle.colorbar(image, ax=axes[1], label="R_AB")
    figure = save_figure(
        figure_handle, output / "multimodal_soinet_dubler_figure.png", dpi=160
    )
    plt.close(figure_handle)

    generated = [metrics.name, figure.name]
    animation_path: Path | None = None
    if simulation:
        animation_handle, axis = plt.subplots(figsize=(6.4, 4.0), constrained_layout=True)
        bars = axis.bar(names, weights[0].numpy(), color="#f58518")
        axis.set(
            title="Elastic Dubler modality weights by sample",
            ylabel="normalized weight",
            ylim=(0.0, 1.0),
        )

        def update(frame: int):
            for bar, height in zip(bars, weights[frame].tolist(), strict=True):
                bar.set_height(height)
            axis.set_xlabel(f"sample {frame}")
            return tuple(bars)

        movie = animation.FuncAnimation(
            animation_handle,
            update,
            frames=weights.shape[0],
            interval=400,
            blit=False,
        )
        animation_path = output / "multimodal_soinet_weight_animation.gif"
        movie.save(animation_path, writer=animation.PillowWriter(fps=2))
        plt.close(animation_handle)
        generated.append(animation_path.name)

    parameters = {
        "architecture": "TNE Multimodal SOInet",
        "input_dim": 6,
        "hidden_dim": 8,
        "output_dim": 4,
        "modalities": list(names),
        "seed": seed,
        "simulation": simulation,
    }
    manifest = write_metadata(
        output / "multimodal_soinet_manifest.json",
        {
            "architecture": "TNE Multimodal SOInet",
            "repository_start_commit": START_COMMIT,
            "repository_result_commit": git_commit(Path(__file__).resolve().parents[3]),
            "parameters": parameters,
            "parameter_hash": parameter_hash(parameters),
            "seed": seed,
            "closure_status": result.closure_status.value,
            "residual_vector": [
                float(value.detach().cpu()) for value in result.residuals.values()
            ],
            "numeric_tolerances": {"absolute": 1e-5},
            "dependency_chain": list(result.metadata["dependency_chain"]),
            "mpl_tc_commits": list(result.metadata["mpl_tc_commits"]),
            "external_reference_context_sha256": MULTIMODAL_REFERENCE_SHA256,
            "external_reference_policy": "design context only; no source copied",
            "generated_files": generated,
            "regeneration_command": (
                "python -m the_nothingness_effect.artificial_intelligence.soinets."
                f"{'simulation' if simulation else 'test'}.run_multimodal"
            ),
            "source_status": "synthetic_deterministic_fixture",
        },
    )
    return {
        "metrics": metrics,
        "figure": figure,
        "animation": animation_path,
        "manifest": manifest,
        "result": result,
    }
