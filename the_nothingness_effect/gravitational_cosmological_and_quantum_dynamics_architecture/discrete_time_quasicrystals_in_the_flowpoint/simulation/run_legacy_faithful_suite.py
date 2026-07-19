"""Materialize deterministic legacy-faithful DTQC visual and data artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from ..legacy_faithful_runtime import (
    CLAIM_BOUNDARY,
    LegacyFaithfulConfig,
    LegacyFaithfulState,
    generate_legacy_faithful_state,
)


STATIC_FILES = (
    "dtqc_legacy_summary.png",
    "dtqc_legacy_quasicrystal_contour.png",
    "dtqc_legacy_diffraction_fft.png",
    "dtqc_legacy_dfi_surface.png",
    "dtqc_legacy_elastic_pi_surface.png",
    "dtqc_legacy_wavelet_ridges.png",
)
ANIMATED_FILES = (
    "dtqc_legacy_flowpoint_flicker.gif",
    "dtqc_legacy_5d_scatter.gif",
    "dtqc_legacy_elastic_pi_sphere.gif",
    "dtqc_legacy_elastic_pi_half_sphere.gif",
)
DATA_FILES = (
    "dtqc_legacy_metrics.csv",
    "dtqc_legacy_state.npz",
    "dtqc_legacy_source_removal.csv",
)
CHECKSUM_FILE = "dtqc_legacy_checksums.json"
MANIFEST_FILE = "dtqc_legacy_manifest.json"
EXPECTED_INVENTORY = (*STATIC_FILES, *ANIMATED_FILES, *DATA_FILES, CHECKSUM_FILE, MANIFEST_FILE)


def _png_bytes(figure: plt.Figure) -> np.ndarray:
    figure.canvas.draw()
    width, height = figure.canvas.get_width_height()
    rgba = np.frombuffer(figure.canvas.buffer_rgba(), dtype=np.uint8).reshape(height, width, 4)
    return rgba[:, :, :3].copy()


def _save_summary(path: Path, state: LegacyFaithfulState) -> None:
    figure, axes = plt.subplots(2, 3, figsize=(12.2, 7.6), constrained_layout=True)
    panels = (
        (state.carrier, "decagonal quasicrystal carrier", "viridis"),
        (np.log1p(12.0 * state.diffraction), "centered 2-D FFT diffraction", "magma"),
        (state.dfi, "radial multi-axis DFI", "plasma"),
        (state.entropy, "entropy field S", "cividis"),
        (state.elastic_pi, "Elastic-pi = pi exp(-S/K_D)", "viridis"),
        (state.flowpoint_frames[1], "Flowpoint sector sigma_1 = -1", "coolwarm"),
    )
    for axis, (value, title, cmap) in zip(axes.flat, panels, strict=True):
        image = axis.imshow(value, origin="lower", cmap=cmap)
        axis.set_title(title)
        axis.axis("off")
        figure.colorbar(image, ax=axis, shrink=0.76)
    figure.savefig(path, dpi=155)
    plt.close(figure)


def _save_contour(path: Path, state: LegacyFaithfulState) -> None:
    figure, axis = plt.subplots(figsize=(7.0, 6.0), constrained_layout=True)
    contour = axis.contourf(state.x, state.y, state.carrier, levels=30, cmap="viridis")
    axis.contour(state.x, state.y, state.carrier, levels=12, linewidths=0.35)
    axis.set(title="Legacy-faithful decagonal DTQC carrier", xlabel="x", ylabel="y", aspect="equal")
    figure.colorbar(contour, ax=axis, label="carrier amplitude")
    figure.savefig(path, dpi=170)
    plt.close(figure)


def _save_image(path: Path, value: np.ndarray, title: str, cmap: str, label: str) -> None:
    figure, axis = plt.subplots(figsize=(7.0, 5.8), constrained_layout=True)
    image = axis.imshow(value, origin="lower", cmap=cmap)
    axis.set_title(title)
    axis.set(xlabel="grid x", ylabel="grid y")
    figure.colorbar(image, ax=axis, label=label)
    figure.savefig(path, dpi=170)
    plt.close(figure)


def _save_surface(path: Path, state: LegacyFaithfulState, value: np.ndarray, title: str) -> None:
    stride = max(1, state.config.grid_size // 36)
    figure = plt.figure(figsize=(8.3, 6.2), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    surface = axis.plot_surface(
        state.x[::stride, ::stride],
        state.y[::stride, ::stride],
        value[::stride, ::stride],
        cmap="viridis",
        linewidth=0,
        antialiased=True,
    )
    axis.set(title=title, xlabel="x", ylabel="y", zlabel="response")
    figure.colorbar(surface, ax=axis, shrink=0.65, pad=0.08)
    figure.savefig(path, dpi=160)
    plt.close(figure)


def _flowpoint_animation(path: Path, state: LegacyFaithfulState) -> None:
    images: list[np.ndarray] = []
    bound = float(np.max(np.abs(state.flowpoint_frames)))
    for index, frame in enumerate(state.flowpoint_frames):
        figure, axis = plt.subplots(figsize=(5.6, 5.0), constrained_layout=True)
        image = axis.imshow(frame, origin="lower", cmap="coolwarm", vmin=-bound, vmax=bound)
        axis.set_title(f"Flowpoint DTQC flicker — n={index}, sigma={int(state.flowpoint_sector[index]):+d}")
        axis.axis("off")
        figure.colorbar(image, ax=axis, shrink=0.78)
        images.append(_png_bytes(figure))
        plt.close(figure)
    imageio.mimsave(path, images, duration=0.22, loop=0)


def _scatter_animation(path: Path, state: LegacyFaithfulState) -> None:
    values = state.projection_5d[:, 4]
    images: list[np.ndarray] = []
    for angle in np.linspace(15.0, 345.0, 16):
        figure = plt.figure(figsize=(6.0, 5.5), constrained_layout=True)
        axis = figure.add_subplot(111, projection="3d")
        scatter = axis.scatter(
            state.projection_3d[:, 0],
            state.projection_3d[:, 1],
            state.projection_3d[:, 2],
            c=values,
            cmap="viridis",
            s=7,
            alpha=0.72,
        )
        axis.view_init(elev=24.0, azim=float(angle))
        axis.set(title="Deterministic projection of the 5-D DTQC state", xlabel="P1", ylabel="P2", zlabel="P3")
        figure.colorbar(scatter, ax=axis, shrink=0.66, label="5th normalized coordinate")
        images.append(_png_bytes(figure))
        plt.close(figure)
    imageio.mimsave(path, images, duration=0.12, loop=0)


def _sphere_animation(path: Path, points: np.ndarray, title: str) -> None:
    values = points[:, 2]
    images: list[np.ndarray] = []
    for angle in np.linspace(0.0, 330.0, 12):
        figure = plt.figure(figsize=(5.8, 5.4), constrained_layout=True)
        axis = figure.add_subplot(111, projection="3d")
        scatter = axis.scatter(points[:, 0], points[:, 1], points[:, 2], c=values, cmap="plasma", s=5, alpha=0.72)
        axis.view_init(elev=20.0, azim=float(angle))
        axis.set(title=title, xlabel="X", ylabel="Y", zlabel="Z")
        axis.set_box_aspect((1, 1, 1))
        figure.colorbar(scatter, ax=axis, shrink=0.64, label="Elastic-pi radial coordinate")
        images.append(_png_bytes(figure))
        plt.close(figure)
    imageio.mimsave(path, images, duration=0.14, loop=0)


def _write_metrics(path: Path, state: LegacyFaithfulState) -> None:
    rows = (
        ("carrier_std", float(np.std(state.carrier))),
        ("diffraction_peak", float(np.max(state.diffraction))),
        ("dfi_mean", float(np.mean(state.dfi))),
        ("entropy_mean", float(np.mean(state.entropy))),
        ("elastic_pi_min", float(np.min(state.elastic_pi))),
        ("elastic_pi_max", float(np.max(state.elastic_pi))),
        ("flowpoint_two_step_residual", float(np.linalg.norm(state.flowpoint_frames[2:] - state.flowpoint_frames[:-2]))),
        ("projection_5d_rank", float(np.linalg.matrix_rank(state.projection_5d))),
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("metric", "value"))
        writer.writerows(rows)


def _write_source_removal(path: Path, state: LegacyFaithfulState) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("source", "necessity_residual", "necessary"))
        for source, residual in sorted(state.source_removal.items()):
            writer.writerow((source, f"{residual:.17g}", residual > 0.0))


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_legacy_faithful_suite(
    output_dir: str | Path,
    *,
    seed: int = 0,
    grid_size: int = 72,
) -> dict[str, object]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    config = LegacyFaithfulConfig(seed=seed, grid_size=grid_size)
    state = generate_legacy_faithful_state(config)

    _save_summary(output / STATIC_FILES[0], state)
    _save_contour(output / STATIC_FILES[1], state)
    _save_image(
        output / STATIC_FILES[2],
        np.log1p(12.0 * state.diffraction),
        "Centered 2-D FFT diffraction",
        "magma",
        "log diffraction intensity",
    )
    _save_surface(output / STATIC_FILES[3], state, state.dfi, "Radial multi-axis DFI surface")
    _save_surface(output / STATIC_FILES[4], state, state.elastic_pi, "Canonical Elastic-pi surface")
    _save_image(
        output / STATIC_FILES[5],
        state.wavelet_ridges[0],
        "Multiscale wavelet-ridge proxy",
        "cividis",
        "ridge strength",
    )

    _flowpoint_animation(output / ANIMATED_FILES[0], state)
    _scatter_animation(output / ANIMATED_FILES[1], state)
    _sphere_animation(output / ANIMATED_FILES[2], state.sphere_points, "Elastic-pi spherical embedding")
    _sphere_animation(
        output / ANIMATED_FILES[3],
        state.half_sphere_points,
        "Elastic-pi half-sphere cutaway",
    )

    _write_metrics(output / DATA_FILES[0], state)
    np.savez_compressed(
        output / DATA_FILES[1],
        x=state.x,
        y=state.y,
        carrier=state.carrier,
        diffraction=state.diffraction,
        dfi_channels=state.dfi_channels,
        dfi=state.dfi,
        entropy=state.entropy,
        elastic_pi=state.elastic_pi,
        flowpoint_sector=state.flowpoint_sector,
        flowpoint_frames=state.flowpoint_frames,
        projection_5d=state.projection_5d,
        projection_3d=state.projection_3d,
        sphere_points=state.sphere_points,
        half_sphere_points=state.half_sphere_points,
        wavelet_ridges=state.wavelet_ridges,
    )
    _write_source_removal(output / DATA_FILES[2], state)

    manifest = {
        "schema_version": "1.0",
        "suite": "dtqc_legacy_faithful",
        "seed": seed,
        "grid_size": grid_size,
        "entropy_scale": state.config.entropy_scale,
        "mathematical_bindings": {
            "carrier": "ten-direction decagonal plane-wave superposition",
            "diffraction": "centered 2-D FFT intensity",
            "dfi": "radial multi-axis finite fluctuation decomposition",
            "elastic_pi": "pi*exp(-S/K_D)",
            "flowpoint": "sigma_n=(-1)^n",
        },
        "source_removal": state.source_removal,
        "generated_files": [*STATIC_FILES, *ANIMATED_FILES, *DATA_FILES, CHECKSUM_FILE],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    manifest_path = output / MANIFEST_FILE
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checksummed = (*STATIC_FILES, *ANIMATED_FILES, *DATA_FILES, MANIFEST_FILE)
    checksums = {
        "schema_version": "1.0",
        "algorithm": "sha256",
        "files": {name: _digest(output / name) for name in checksummed},
    }
    (output / CHECKSUM_FILE).write_text(
        json.dumps(checksums, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    actual_inventory = tuple(sorted(path.name for path in output.iterdir() if path.is_file()))
    if actual_inventory != tuple(sorted(EXPECTED_INVENTORY)):
        raise RuntimeError(f"unexpected legacy-faithful artifact inventory: {actual_inventory}")
    for name in ANIMATED_FILES:
        with Image.open(output / name) as movie:
            if not movie.is_animated or movie.n_frames < 8:
                raise RuntimeError(f"legacy-faithful animation is not valid: {name}")

    return {
        "output_dir": output,
        "manifest": manifest_path,
        "checksums": output / CHECKSUM_FILE,
        "files": tuple(output / name for name in EXPECTED_INVENTORY),
        "source_removal": state.source_removal,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "artifacts" / "legacy_faithful")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--grid-size", type=int, default=72)
    args = parser.parse_args()
    result = run_legacy_faithful_suite(args.output, seed=args.seed, grid_size=args.grid_size)
    print(result["manifest"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
