"""Run locality-driven spiral simulations and save repository-linked artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from tne_runtime.artifacts.io import CLAIM_BOUNDARY, ensure_dir, save_csv, save_figure, save_json, save_npz, write_metadata
from equations.locality_driven_gravity.locality_driven_gravity import (
    BodyType,
    LocalityGravityParams,
    compare_spiral_arm_modes,
    compute_spiral_metrics,
    simulate_locality_spiral,
)


SCRIPT_DIR = Path(__file__).resolve().parent
ARM_MODE_ORDER: tuple[int | str, ...] = (2, 3, 4, "mixed")
MODE_CLAIM_DETAIL = (
    "Finite spiral-mode comparison for a TNE locality-driven galaxy proxy. "
    "This is a controlled arm-mode initialization study, not a full astrophysical simulation, "
    "not an empirical validation claim, and not a formal proof substitute."
)


def _metadata_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _mode_slug(arm_mode: int | str) -> str:
    return str(arm_mode)


def _mode_params(arm_mode: int | str, quick: bool, steps: int | None = None) -> LocalityGravityParams:
    return LocalityGravityParams(
        n_particles=96 if quick else 240,
        steps=72 if quick else (steps or 220),
        grid_size=32 if quick else 52,
        radial_scale=3.1,
        central_mass=200.0 if quick else 220.0,
        arm_mode=arm_mode,  # type: ignore[arg-type]
    )


def create_figure(result: dict[str, object], metrics: dict[str, float], *, title: str) -> plt.Figure:
    history = np.asarray(result["history"], dtype=float)
    density_history = np.asarray(result["density_history"], dtype=float)
    tension_history = np.asarray(result["tension_history"], dtype=float)
    masses = np.asarray(result["masses"], dtype=float)
    body_types = np.asarray(result["body_types"], dtype=object)
    initial = history[0]
    final = history[-1]
    final_density = density_history[-1]
    final_tension = tension_history[-1]
    grid_axis = np.asarray(result["grid_axis"], dtype=float)
    xx, yy = np.meshgrid(grid_axis, grid_axis)

    fig = plt.figure(figsize=(14.8, 9.2), constrained_layout=True)
    gs = fig.add_gridspec(2, 3)
    ax_initial = fig.add_subplot(gs[0, 0])
    ax_final = fig.add_subplot(gs[0, 1])
    ax_density = fig.add_subplot(gs[0, 2])
    ax_traj = fig.add_subplot(gs[1, 0])
    ax_metrics = fig.add_subplot(gs[1, 1])
    ax_tension = fig.add_subplot(gs[1, 2])

    initial_sizes = 8 + 8 * masses / (np.max(masses) + 1e-12)
    ax_initial.scatter(initial[:, 0], initial[:, 1], s=initial_sizes, c=np.linalg.norm(initial, axis=1), cmap="magma", alpha=0.9)
    ax_initial.scatter(initial[body_types == BodyType.CENTRAL_MASS.value, 0], initial[body_types == BodyType.CENTRAL_MASS.value, 1], s=120, c="#f2cf63", marker="*", label="central mass")
    ax_initial.set_title("Initial body field")
    ax_initial.legend(loc="upper right")

    density_map = ax_final.imshow(
        final_density,
        extent=(grid_axis[0], grid_axis[-1], grid_axis[0], grid_axis[-1]),
        origin="lower",
        cmap="inferno",
        alpha=0.52,
    )
    ax_final.contour(xx, yy, final_density, levels=6, colors="white", linewidths=0.7, alpha=0.6)
    ax_final.scatter(final[:, 0], final[:, 1], s=initial_sizes, c=np.linalg.norm(final, axis=1), cmap="viridis", alpha=0.82)
    ax_final.scatter(final[body_types == BodyType.CENTRAL_MASS.value, 0], final[body_types == BodyType.CENTRAL_MASS.value, 1], s=140, c="#ffe08a", marker="*", edgecolors="black")
    ax_final.set_title("Final body field")
    fig.colorbar(density_map, ax=ax_final, label="density proxy")

    density_image = ax_density.imshow(
        final_density,
        extent=(grid_axis[0], grid_axis[-1], grid_axis[0], grid_axis[-1]),
        origin="lower",
        cmap="magma",
    )
    ax_density.contour(xx, yy, final_tension, levels=6, colors="#9ecae1", linewidths=0.8)
    ax_density.set_title("Final density ridges")
    fig.colorbar(density_image, ax=ax_density, label="density proxy")

    stride = max(1, history.shape[1] // 40)
    for particle_path in history[:, 1::stride, :].transpose(1, 0, 2):
        ax_traj.plot(particle_path[:, 0], particle_path[:, 1], linewidth=0.55, alpha=0.45, color="#4c78a8")
    ax_traj.scatter(final[:, 0], final[:, 1], s=5, color="#54a24b", alpha=0.65)
    ax_traj.set_title("Trajectory winding")

    metric_lines = [
        f"arm_mode = {result['metadata']['arm_mode']}",  # type: ignore[index]
        f"spiral = {metrics['spiral_order_parameter']:.3f}",
        f"m1/m2 = {metrics['mode_1_amplitude']:.3f} / {metrics['mode_2_amplitude']:.3f}",
        f"m3/m4 = {metrics['mode_3_amplitude']:.3f} / {metrics['mode_4_amplitude']:.3f}",
        f"dominant = m{int(metrics['dominant_mode'])} ({metrics['dominant_mode_amplitude']:.3f})",
        f"target ratio = {metrics['target_mode_ratio']:.3f}",
        f"contrast = {metrics['density_arm_contrast']:.3f}",
        f"asymmetry = {metrics['arm_asymmetry_index']:.3f}",
        f"evolution score = {metrics['initialization_vs_evolution_score']:.3f}",
        f"feedback = {metrics['field_feedback_strength']:.3f}",
    ]
    ax_metrics.axis("off")
    ax_metrics.set_title("Metrics inset")
    ax_metrics.text(
        0.02,
        0.98,
        "\n".join(metric_lines),
        va="top",
        ha="left",
        fontsize=10,
        family="monospace",
        bbox={"facecolor": "#f7f7f7", "edgecolor": "#d0d0d0", "boxstyle": "round,pad=0.4"},
    )

    tension_map = ax_tension.imshow(
        final_tension,
        extent=(grid_axis[0], grid_axis[-1], grid_axis[0], grid_axis[-1]),
        origin="lower",
        cmap="cividis",
    )
    ax_tension.contour(xx, yy, final_density, levels=5, colors="white", linewidths=0.7, alpha=0.55)
    ax_tension.set_title("Final tension field")
    fig.colorbar(tension_map, ax=ax_tension, label="tension proxy")

    for ax in [ax_initial, ax_final, ax_density, ax_traj, ax_tension]:
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True, alpha=0.16)

    fig.suptitle(title, fontsize=13)
    return fig


def _save_mode_result(mode_root: Path, arm_mode: int | str, result: dict[str, object]) -> dict[str, Path]:
    slug = _mode_slug(arm_mode)
    metrics = dict(result["metrics"])
    figure_path = mode_root / f"spiral_arm_mode_{slug}_figure.png"
    data_path = mode_root / f"spiral_arm_mode_{slug}_data.npz"
    metrics_path = mode_root / f"spiral_arm_mode_{slug}_metrics.csv"
    metadata_path = mode_root / f"spiral_arm_mode_{slug}_metadata.json"

    save_npz(
        data_path,
        history=result["history"],
        velocity_history=result["velocity_history"],
        density_history=result["density_history"],
        tension_history=result["tension_history"],
        entropy_history=result["entropy_history"],
        density_gradient_history=result["density_gradient_history"],
        positions=result["positions"],
        velocities=result["velocities"],
        masses=result["masses"],
        body_types=result["body_types"],
        grid_axis=result["grid_axis"],
        arm_mode_assignment=result["arm_mode_assignment"],
        arm_phase_offsets=result["arm_phase_offsets"],
    )
    save_csv(metrics_path, [{**metrics, "arm_mode": slug, "claim_boundary": CLAIM_BOUNDARY}])
    fig = create_figure(result, metrics, title=f"Finite illustrative arm-mode {slug} galaxy proxy")
    save_figure(fig, figure_path)
    plt.close(fig)
    write_metadata(
        metadata_path,
        {
            **result["metadata"],
            "output_directory": _metadata_path(mode_root),
            "metrics": metrics,
            "claim_boundary_detail": MODE_CLAIM_DETAIL,
        },
    )
    return {
        "figure": figure_path,
        "data": data_path,
        "metrics": metrics_path,
        "metadata": metadata_path,
    }


def _write_mode_comparison(mode_root: Path, results: dict[str, dict[str, object]]) -> dict[str, Path]:
    rows: list[dict[str, object]] = []
    for slug, result in results.items():
        metrics = dict(result["metrics"])
        rows.append({"arm_mode": slug, **metrics})
    csv_path = mode_root / "spiral_arm_mode_comparison.csv"
    json_path = mode_root / "spiral_arm_mode_comparison.json"
    figure_path = mode_root / "spiral_arm_mode_comparison.png"
    report_path = mode_root / "spiral_arm_mode_comparison_report.md"
    save_csv(csv_path, rows)
    save_json(
        json_path,
        {
            "claim_boundary": CLAIM_BOUNDARY,
            "comparison_type": "finite spiral-mode comparison",
            "arm_modes": rows,
            "claim_boundary_detail": MODE_CLAIM_DETAIL,
        },
    )

    fig = plt.figure(figsize=(16, 10), constrained_layout=True)
    gs = fig.add_gridspec(3, 4)
    grid_axis = None
    for idx, arm_mode in enumerate(ARM_MODE_ORDER):
        slug = _mode_slug(arm_mode)
        result = results[slug]
        history = np.asarray(result["history"], dtype=float)
        final = history[-1]
        masses = np.asarray(result["masses"], dtype=float)
        grid_axis = np.asarray(result["grid_axis"], dtype=float)
        density = np.asarray(result["density_history"], dtype=float)[-1]
        ax = fig.add_subplot(gs[0, idx])
        ax.imshow(density, extent=(grid_axis[0], grid_axis[-1], grid_axis[0], grid_axis[-1]), origin="lower", cmap="inferno", alpha=0.55)
        ax.scatter(final[:, 0], final[:, 1], s=8 + 8 * masses / (np.max(masses) + 1e-12), c=np.linalg.norm(final, axis=1), cmap="viridis", alpha=0.8)
        ax.set_title(f"arm_mode={slug}")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, alpha=0.15)

    ax_modes = fig.add_subplot(gs[1, :2])
    labels = [str(mode) for mode in ARM_MODE_ORDER]
    x = np.arange(len(labels))
    width = 0.18
    for offset, mode_index in enumerate([1, 2, 3, 4]):
        ax_modes.bar(x + (offset - 1.5) * width, [results[label]["metrics"][f"mode_{mode_index}_amplitude"] for label in labels], width=width, label=f"m={mode_index}")
    ax_modes.set_xticks(x)
    ax_modes.set_xticklabels(labels)
    ax_modes.set_title("Mode amplitudes m=1..4")
    ax_modes.set_ylabel("amplitude")
    ax_modes.legend(loc="best")
    ax_modes.grid(True, alpha=0.2)

    ax_contrast = fig.add_subplot(gs[1, 2])
    ax_contrast.bar(labels, [results[label]["metrics"]["density_arm_contrast"] for label in labels], color="#f58518")
    ax_contrast.set_title("Density arm contrast")
    ax_contrast.set_ylabel("contrast")
    ax_contrast.grid(True, axis="y", alpha=0.2)

    ax_dom = fig.add_subplot(gs[1, 3])
    ax_dom.bar(labels, [results[label]["metrics"]["dominant_mode"] for label in labels], color="#54a24b")
    ax_dom.set_title("Dominant mode")
    ax_dom.set_ylabel("m")
    ax_dom.grid(True, axis="y", alpha=0.2)

    ax_target = fig.add_subplot(gs[2, :2])
    ax_target.plot(labels, [results[label]["metrics"]["target_mode_ratio"] for label in labels], marker="o", linewidth=2.0, color="#4c78a8")
    ax_target.set_title("Target mode ratio")
    ax_target.set_ylabel("ratio")
    ax_target.grid(True, alpha=0.2)

    ax_spiral = fig.add_subplot(gs[2, 2:])
    ax_spiral.plot(labels, [results[label]["metrics"]["spiral_order_parameter"] for label in labels], marker="s", linewidth=2.0, color="#e45756", label="spiral order")
    ax_spiral.plot(labels, [results[label]["metrics"]["initialization_vs_evolution_score"] for label in labels], marker="^", linewidth=1.8, color="#72b7b2", label="init vs evolution")
    ax_spiral.set_title("Aggregate morphology diagnostics")
    ax_spiral.legend(loc="best")
    ax_spiral.grid(True, alpha=0.2)

    fig.suptitle("Finite spiral-mode comparison for a TNE locality-driven galaxy proxy", fontsize=14)
    save_figure(fig, figure_path)
    plt.close(fig)

    report_lines = [
        "# Spiral Arm Mode Comparison",
        "",
        "This is a finite spiral-mode comparison for a TNE locality-driven galaxy proxy.",
        "It is a controlled arm-mode initialization study, not a full astrophysical simulation, not an empirical validation claim, and not a formal proof substitute.",
        "",
    ]
    for row in rows:
        report_lines.extend(
            [
                f"## arm_mode={row['arm_mode']}",
                f"- dominant mode: m{int(float(row['dominant_mode']))}",
                f"- spiral order parameter: {float(row['spiral_order_parameter']):.6f}",
                f"- target mode ratio: {float(row['target_mode_ratio']):.6f}",
                f"- initialization vs evolution score: {float(row['initialization_vs_evolution_score']):.6f}",
                f"- density arm contrast: {float(row['density_arm_contrast']):.6f}",
                "",
            ]
        )
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    return {"csv": csv_path, "json": json_path, "figure": figure_path, "report": report_path}


def run(
    output_dir: str | Path | None = None,
    seed: int = 2710,
    steps: int | None = None,
    quick: bool = False,
) -> dict[str, Path | bool]:
    root = Path(output_dir) if output_dir is not None else SCRIPT_DIR
    ensure_dir(root)
    default_params = _mode_params(2, quick, steps)
    default_result = simulate_locality_spiral(params=default_params, seed=seed)
    default_metrics = compute_spiral_metrics(
        default_result["history"],
        velocity_history=default_result["velocity_history"],
        masses=default_result["masses"],
        body_types=default_result["body_types"],
        tension_field=default_result["tension_history"][-1],
        arm_mode=2,
    )
    default_result["metrics"] = default_metrics

    figure_path = root / "figure6_locality_driven_spiral.png"
    data_path = root / "figure6_spiral_particles.npz"
    metrics_path = root / "figure6_spiral_metrics.csv"
    metadata_path = root / "figure6_metadata.json"
    locality_metrics_path = root / "locality_spiral_metrics.csv"
    locality_metadata_path = root / "locality_spiral_metadata.json"

    save_npz(
        data_path,
        history=default_result["history"],
        velocity_history=default_result["velocity_history"],
        density_history=default_result["density_history"],
        tension_history=default_result["tension_history"],
        entropy_history=default_result["entropy_history"],
        masses=default_result["masses"],
        body_types=default_result["body_types"],
        grid_axis=default_result["grid_axis"],
        arm_mode_assignment=default_result["arm_mode_assignment"],
        arm_phase_offsets=default_result["arm_phase_offsets"],
    )
    csv_row = {"section": "16.4", "figure": "6", "arm_mode": 2, **default_metrics, "claim_boundary": CLAIM_BOUNDARY}
    save_csv(metrics_path, [csv_row])
    save_csv(locality_metrics_path, [csv_row])
    fig = create_figure(default_result, default_metrics, title="Figure 6: finite locality-driven spiral proxy")
    save_figure(fig, figure_path)
    plt.close(fig)

    metadata_payload = {
        "section": "16.4",
        "figure": "6",
        "paper_caption_target": "Finite locality-driven spiral proxy with controlled two-arm perturbation; not a full astrophysical simulation.",
        "script": "equations.locality_driven_gravity.simulation.simulate_locality_driven_gravity",
        "equations_module": "equations.locality_driven_gravity.entropic_elastic_spiral",
        "parameters": default_result["metadata"]["parameter_set"],
        "random_seed": seed,
        "output_directory": _metadata_path(root),
        "metrics": default_metrics,
        "arm_mode": 2,
        "claim_boundary_detail": "Finite locality-driven spiral proxy with controlled two-arm perturbation; not a full astrophysical simulation, not an empirical validation claim, and not a formal proof substitute.",
    }
    write_metadata(metadata_path, metadata_payload)
    write_metadata(locality_metadata_path, metadata_payload)

    mode_root = ensure_dir(root / "arm_modes")
    comparison = compare_spiral_arm_modes(ARM_MODE_ORDER, seed=seed, quick=quick, params=_mode_params(2, quick, steps))
    for slug, result in comparison.items():
        result["metrics"] = compute_spiral_metrics(
            result["history"],
            velocity_history=result["velocity_history"],
            masses=result["masses"],
            body_types=result["body_types"],
            tension_field=result["tension_history"][-1],
            arm_mode=result["metadata"]["arm_mode"],
        )
        _save_mode_result(mode_root, slug, result)
    comparison_paths = _write_mode_comparison(mode_root, comparison)
    return {
        "figure": figure_path,
        "data": data_path,
        "metrics": metrics_path,
        "metadata": metadata_path,
        "locality_metrics": locality_metrics_path,
        "locality_metadata": locality_metadata_path,
        "mode_comparison_csv": comparison_paths["csv"],
        "mode_comparison_json": comparison_paths["json"],
        "mode_comparison_figure": comparison_paths["figure"],
        "mode_comparison_report": comparison_paths["report"],
        "passed_validation": default_metrics["nan_count"] == 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate locality-driven spiral simulation artifacts.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--seed", type=int, default=2710)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.output_dir, seed=args.seed, steps=args.steps, quick=args.quick)
    summary = {
        "figure_dir": _metadata_path(Path(result["figure"]).parent),
        "mode_comparison_report": _metadata_path(Path(result["mode_comparison_report"])),
        "scope": MODE_CLAIM_DETAIL,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
