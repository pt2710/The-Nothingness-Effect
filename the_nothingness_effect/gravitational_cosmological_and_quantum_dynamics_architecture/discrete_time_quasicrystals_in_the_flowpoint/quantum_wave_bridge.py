"""Flowpoint quantum-wave bridge for discrete-time quasicrystal evidence.

The legacy ``fields_of_physics_in_dev/quantum_mechanics`` scripts define real
Flowpoint sine/pi waves, two-mode interference, six quark parameter sets, and a
classical pair synchronizer called entanglement. This module keeps the source
parameters but upgrades the executable bridge to normalized complex wavefields,
a discrete quasiperiodic Floquet clock, and density-matrix entanglement metrics.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any, Callable, Mapping

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

QUARKS: tuple[dict[str, float | str], ...] = (
    {"name": "up", "mass_gev": 2.2e-3, "charge": 2.0 / 3.0, "frequency_factor": 1.0, "spin": 0.5},
    {"name": "down", "mass_gev": 4.7e-3, "charge": -1.0 / 3.0, "frequency_factor": 1.1, "spin": 0.5},
    {"name": "charm", "mass_gev": 1.28, "charge": 2.0 / 3.0, "frequency_factor": 1.2, "spin": 0.5},
    {"name": "strange", "mass_gev": 96e-3, "charge": -1.0 / 3.0, "frequency_factor": 1.3, "spin": 0.5},
    {"name": "top", "mass_gev": 173.0, "charge": 2.0 / 3.0, "frequency_factor": 1.4, "spin": 0.5},
    {"name": "bottom", "mass_gev": 4.18, "charge": -1.0 / 3.0, "frequency_factor": 1.5, "spin": 0.5},
)

SOURCE_SHA256 = {
    "fields_of_physics_in_dev/quantum_mechanics/wave_functionality/fp_sine_wave/fp_sine_wave.py": "02c7bb5a42c87a4605e05bcd31851f9f855495db47de223e5596a28492973107",
    "fields_of_physics_in_dev/quantum_mechanics/wave_functionality/fp_pi_wave/fp_pi_wave.py": "2e76ad10395694453d563ac2922e00b946c16840557d1ed60edff66c4de4b4d7",
    "fields_of_physics_in_dev/quantum_mechanics/wave_functionality/fp_wave_Interference/fp_wave_with_interference.py": "5b8956a6e6422f3a7dae55c75fef6eff10156b10a30cdae14a831f396b08a41c",
    "fields_of_physics_in_dev/quantum_mechanics/wave_functionality/fp_waves/fp_waves.py": "5ab658ef9baeadacd8888ac62604b1f7137ea8cb223243fa131cfd903cc73488",
    "fields_of_physics_in_dev/quantum_mechanics/fp_particle_models/fp_quarks.py": "4612a6a6a5b543764375c8dd64afbec2ad0d54cffacc05d15b602ece33369382",
    "fields_of_physics_in_dev/quantum_mechanics/fp_particle_models/particle_model.py": "0b4caf550cfd1f5231f431a532602c9f523137983ef2d3ea9f663717e1e62ce1",
    "fields_of_physics_in_dev/quantum_mechanics/entanglement/entanglement_model.py": "6d79a92e188bc6c42b4027e050200f145c9e271e44143b60a420a14e56c75637",
}

STATIC_FILES = (
    "dtqc_fp_wave_interference.png",
    "dtqc_fp_quark_modes.png",
    "dtqc_fp_floquet_spectrum.png",
)
ANIMATED_FILES = (
    "dtqc_fp_wavefunction_probability.gif",
    "dtqc_fp_wavefunction_phase.gif",
    "dtqc_fp_entanglement.gif",
)
DATA_FILES = (
    "dtqc_fp_quantum_state.npz",
    "dtqc_fp_quantum_metrics.csv",
    "dtqc_fp_quantum_source_removal.csv",
    "dtqc_fp_quantum_manifest.json",
)
ALL_FILES = (*STATIC_FILES, *ANIMATED_FILES, *DATA_FILES)


def normalized_quark_frequencies() -> np.ndarray:
    """Return bounded frequencies while preserving legacy mass-factor ordering."""
    raw = np.asarray(
        [float(q["mass_gev"]) * float(q["frequency_factor"]) for q in QUARKS],
        dtype=np.float64,
    )
    compressed = np.log1p(raw / max(float(np.min(raw)), 1e-12))
    span = max(float(np.ptp(compressed)), 1e-12)
    return 0.75 + 1.75 * (compressed - float(np.min(compressed))) / span


def quasiperiodic_clock(step: int, step_count: int) -> tuple[float, float, float]:
    """Return two irrational drive phases and the Flowpoint parity sector."""
    if step_count < 2:
        raise ValueError("step_count must be at least two")
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    theta_a = 2.0 * math.pi * step / phi
    theta_b = 2.0 * math.pi * step / math.sqrt(2.0)
    sector = 1.0 if step % 2 == 0 else -1.0
    return theta_a, theta_b, sector


def _normalize_wave(value: np.ndarray) -> np.ndarray:
    wave = np.asarray(value, dtype=np.complex128)
    norm = float(np.linalg.norm(wave.ravel()))
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError("complex Flowpoint wave is degenerate")
    return wave / norm


def _quark_axis_coefficients(axis_count: int) -> np.ndarray:
    frequencies = normalized_quark_frequencies()
    charges = np.asarray([float(q["charge"]) for q in QUARKS], dtype=float)
    indices = np.arange(axis_count, dtype=float) + 1.0
    rows = []
    for mode_index, (frequency, charge) in enumerate(
        zip(frequencies, charges, strict=True)
    ):
        raw = 0.25 + np.square(
            np.cos(
                math.pi * indices * (mode_index + 1.0) / (axis_count + 2.0)
                + charge * math.pi / 3.0
                + 0.15 * frequency
            )
        )
        rows.append(raw / float(np.linalg.norm(raw)))
    return np.asarray(rows, dtype=float)


def build_wave_frame(
    bundle: Mapping[str, Any],
    *,
    step: int,
    step_count: int,
    remove_wave_source: bool = False,
    remove_particle_source: bool = False,
) -> dict[str, np.ndarray | float]:
    """Construct six normalized complex particle modes and their interference field."""
    components = np.asarray(bundle["axis_components"], dtype=float)
    axis_gain = np.asarray(bundle["axis_elastic_pi"], dtype=float)
    if components.ndim != 3 or axis_gain.shape != components.shape:
        raise ValueError(
            "five-axis carrier and Elastic-pi channels must have equal (M,H,W) shape"
        )
    axis_count = components.shape[0]
    if axis_count < 2:
        raise ValueError("at least two intrinsic axes are required")

    theta_a, theta_b, sector = quasiperiodic_clock(step, step_count)
    frequencies = normalized_quark_frequencies()
    if remove_particle_source:
        frequencies = np.full_like(frequencies, float(np.mean(frequencies)))
    coefficients = _quark_axis_coefficients(axis_count)

    gain = axis_gain / np.mean(axis_gain, axis=(1, 2), keepdims=True)
    gain = np.clip(gain, 0.55, 1.45)
    envelope = np.sqrt(np.abs(components) + 0.08) * np.sqrt(gain)
    if remove_wave_source:
        envelope = np.ones_like(envelope)
        components = np.zeros_like(components)

    modes = []
    for mode_index, frequency in enumerate(frequencies):
        axis_waves = []
        charge = float(QUARKS[mode_index]["charge"])
        for axis_index in range(axis_count):
            spatial_phase = (
                frequency * components[axis_index]
                + (axis_index + 1.0) * theta_a / axis_count
                + charge * theta_b
            )
            axis_waves.append(
                envelope[axis_index] * np.exp(1j * spatial_phase)
            )
        mode = np.tensordot(
            coefficients[mode_index], np.asarray(axis_waves), axes=1
        )
        modes.append(_normalize_wave(mode))
    mode_stack = np.asarray(modes)

    # The legacy two-wave FP interference is retained as the primary pair and
    # generalized by the four remaining quark modes over the five-axis carrier.
    relative_phase = math.pi * step + 0.35 * math.sin(theta_b)
    primary = mode_stack[0] + np.exp(1j * relative_phase) * mode_stack[1]
    secondary = sum(
        np.exp(1j * (mode_index + 1) * theta_a / len(QUARKS))
        * mode_stack[mode_index]
        for mode_index in range(2, len(QUARKS))
    ) / math.sqrt(len(QUARKS) - 2)
    wave = _normalize_wave(primary + 0.42 * sector * secondary)
    probability = np.abs(wave) ** 2
    probability /= float(np.sum(probability))
    return {
        "modes": mode_stack,
        "wave": wave,
        "probability": probability,
        "phase": np.angle(wave),
        "theta_a": theta_a,
        "theta_b": theta_b,
        "sector": sector,
        "quark_frequencies": frequencies,
        "coefficients": coefficients,
    }


def entangled_pair_state(
    frame: Mapping[str, Any],
    *,
    remove_entanglement_source: bool = False,
) -> dict[str, Any]:
    """Lift FP-wave contrast into a normalized two-qubit pure state."""
    probability = np.asarray(frame["probability"], dtype=float)
    wave = np.asarray(frame["wave"], dtype=np.complex128)
    height, width = probability.shape
    left = float(np.sum(probability[:, : width // 2]))
    top = float(np.sum(probability[: height // 2, :]))
    contrast = min(
        1.0,
        abs(left - top) * 4.0
        + float(np.std(probability)) * probability.size * 0.25,
    )
    gamma = 0.0 if remove_entanglement_source else (0.24 + 0.48 * contrast)
    gamma = float(np.clip(gamma, 0.0, math.pi / 4.0))
    mirror = wave[:, width - width // 2 :]
    phase = float(
        np.angle(np.sum(wave[:, : width // 2] * np.conj(mirror)))
    )
    state = np.asarray(
        [
            math.cos(gamma),
            0.0j,
            0.0j,
            np.exp(1j * phase) * math.sin(gamma),
        ],
        dtype=np.complex128,
    )
    state /= np.linalg.norm(state)
    matrix = state.reshape(2, 2)
    rho_a = matrix @ matrix.conj().T
    eigenvalues = np.linalg.eigvalsh(rho_a).real
    positive = eigenvalues[eigenvalues > 1e-15]
    entropy = float(-np.sum(positive * np.log2(positive)))
    purity = float(np.real(np.trace(rho_a @ rho_a)))
    concurrence = float(
        2.0 * abs(state[0] * state[3] - state[1] * state[2])
    )
    bell = np.asarray([1.0, 0.0, 0.0, 1.0], dtype=np.complex128) / math.sqrt(2.0)
    bell_fidelity = float(abs(np.vdot(bell, state)) ** 2)
    return {
        "state": state,
        "rho_a": rho_a,
        "eigenvalues": eigenvalues,
        "entropy": entropy,
        "purity": purity,
        "concurrence": concurrence,
        "bell_fidelity": bell_fidelity,
        "gamma": gamma,
        "phase": phase,
    }


def simulate_quantum_bridge(
    bundle_factory: Callable[[float], Mapping[str, Any]],
    *,
    frame_count: int,
) -> dict[str, Any]:
    """Run the discrete quasiperiodic wave/particle/entanglement bridge."""
    frames = []
    entanglement = []
    for step in range(frame_count):
        phase = 2.0 * math.pi * step / frame_count
        frame = build_wave_frame(
            bundle_factory(phase),
            step=step,
            step_count=frame_count,
        )
        frames.append(frame)
        entanglement.append(entangled_pair_state(frame))
    probabilities = np.asarray([frame["probability"] for frame in frames])
    phases = np.asarray([frame["phase"] for frame in frames])
    wavefunctions = np.asarray([frame["wave"] for frame in frames])
    quark_modes = np.asarray([frame["modes"] for frame in frames])
    norms = np.sum(np.abs(wavefunctions) ** 2, axis=(1, 2))
    return {
        "frames": frames,
        "entanglement": entanglement,
        "probabilities": probabilities,
        "phases": phases,
        "wavefunctions": wavefunctions,
        "quark_modes": quark_modes,
        "norms": norms,
        "entanglement_entropy": np.asarray(
            [item["entropy"] for item in entanglement]
        ),
        "concurrence": np.asarray(
            [item["concurrence"] for item in entanglement]
        ),
        "purity": np.asarray([item["purity"] for item in entanglement]),
        "bell_fidelity": np.asarray(
            [item["bell_fidelity"] for item in entanglement]
        ),
        "rho_a": np.asarray([item["rho_a"] for item in entanglement]),
        "pair_states": np.asarray([item["state"] for item in entanglement]),
    }


def source_removal_metrics(
    bundle_factory: Callable[[float], Mapping[str, Any]],
    *,
    frame_count: int,
) -> list[dict[str, float | str | bool]]:
    baseline = simulate_quantum_bridge(bundle_factory, frame_count=frame_count)
    base_probability = baseline["probabilities"]
    base_modes = baseline["quark_modes"]
    base_entropy = baseline["entanglement_entropy"]

    no_wave_probability = []
    no_particle_modes = []
    no_entanglement_entropy = []
    for step in range(frame_count):
        phase = 2.0 * math.pi * step / frame_count
        bundle = bundle_factory(phase)
        wave_removed = build_wave_frame(
            bundle,
            step=step,
            step_count=frame_count,
            remove_wave_source=True,
        )
        particle_removed = build_wave_frame(
            bundle,
            step=step,
            step_count=frame_count,
            remove_particle_source=True,
        )
        no_wave_probability.append(wave_removed["probability"])
        no_particle_modes.append(particle_removed["modes"])
        no_entanglement_entropy.append(
            entangled_pair_state(
                baseline["frames"][step],
                remove_entanglement_source=True,
            )["entropy"]
        )
    removals = (
        ("fp_wave_functionality", base_probability, np.asarray(no_wave_probability)),
        ("fp_particle_and_quark_modes", base_modes, np.asarray(no_particle_modes)),
        (
            "fp_density_matrix_entanglement",
            base_entropy,
            np.asarray(no_entanglement_entropy),
        ),
    )
    rows = []
    for name, baseline_value, removed_value in removals:
        denominator = max(float(np.linalg.norm(baseline_value)), 1e-12)
        residual = float(
            np.linalg.norm(baseline_value - removed_value) / denominator
        )
        rows.append(
            {
                "source": name,
                "removal_residual": residual,
                "necessary": residual > 1e-4,
            }
        )
    return rows


def _figure_rgb(figure: plt.Figure) -> np.ndarray:
    figure.canvas.draw()
    width, height = figure.canvas.get_width_height()
    rgba = np.frombuffer(figure.canvas.buffer_rgba(), dtype=np.uint8).reshape(
        height,
        width,
        4,
    )
    return rgba[:, :, :3].copy()


def _save_gifs(output: Path, simulation: Mapping[str, Any]) -> None:
    probability_images = []
    phase_images = []
    entanglement_images = []
    entropy = np.asarray(simulation["entanglement_entropy"])
    concurrence = np.asarray(simulation["concurrence"])
    frame_count = len(simulation["frames"])
    for index, frame in enumerate(simulation["frames"]):
        figure, axis = plt.subplots(figsize=(5.5, 5.0), constrained_layout=True)
        image = axis.imshow(frame["probability"], origin="lower", cmap="magma")
        axis.set_title(
            f"FP-DTQC normalized |psi|^2 — step {index}/{frame_count - 1}"
        )
        axis.set_axis_off()
        figure.colorbar(image, ax=axis, shrink=0.74)
        probability_images.append(_figure_rgb(figure))
        plt.close(figure)

        figure, axis = plt.subplots(figsize=(5.5, 5.0), constrained_layout=True)
        image = axis.imshow(
            frame["phase"],
            origin="lower",
            cmap="twilight",
            vmin=-math.pi,
            vmax=math.pi,
        )
        axis.set_title(
            f"FP-DTQC wave phase — Flowpoint sector {int(frame['sector']):+d}"
        )
        axis.set_axis_off()
        figure.colorbar(image, ax=axis, shrink=0.74, label="phase [rad]")
        phase_images.append(_figure_rgb(figure))
        plt.close(figure)

        figure, axes = plt.subplots(
            1,
            2,
            figsize=(9.0, 4.2),
            constrained_layout=True,
        )
        axes[0].plot(np.arange(index + 1), entropy[: index + 1], label="entropy")
        axes[0].plot(
            np.arange(index + 1),
            concurrence[: index + 1],
            label="concurrence",
        )
        axes[0].set(
            xlim=(0, frame_count - 1),
            ylim=(0, 1.05),
            xlabel="discrete DTQC step",
            ylabel="normalized metric",
        )
        axes[0].legend()
        rho = np.abs(simulation["rho_a"][index])
        image = axes[1].imshow(rho, vmin=0.0, vmax=1.0, cmap="viridis")
        axes[1].set_title("|reduced density matrix rho_A|")
        axes[1].set_xticks([0, 1])
        axes[1].set_yticks([0, 1])
        figure.colorbar(image, ax=axes[1], shrink=0.75)
        figure.suptitle(
            "FP-DTQC bipartite entanglement (density-matrix closure)"
        )
        entanglement_images.append(_figure_rgb(figure))
        plt.close(figure)

    imageio.mimsave(
        output / ANIMATED_FILES[0],
        probability_images,
        duration=0.12,
        loop=0,
        subrectangles=True,
    )
    imageio.mimsave(
        output / ANIMATED_FILES[1],
        phase_images,
        duration=0.12,
        loop=0,
        subrectangles=True,
    )
    imageio.mimsave(
        output / ANIMATED_FILES[2],
        entanglement_images,
        duration=0.14,
        loop=0,
        subrectangles=True,
    )


def _save_static(output: Path, simulation: Mapping[str, Any]) -> None:
    frame0 = simulation["frames"][0]
    mode0 = np.asarray(frame0["modes"])
    figure, axes = plt.subplots(
        1,
        3,
        figsize=(13.0, 4.2),
        constrained_layout=True,
    )
    axes[0].imshow(np.real(frame0["wave"]), origin="lower", cmap="RdBu_r")
    axes[0].set_title("Re psi")
    axes[1].imshow(np.imag(frame0["wave"]), origin="lower", cmap="RdBu_r")
    axes[1].set_title("Im psi")
    axes[2].imshow(frame0["probability"], origin="lower", cmap="magma")
    axes[2].set_title("normalized |psi|^2")
    for axis in axes:
        axis.set_axis_off()
    figure.suptitle(
        "Source-faithful FP wave interference embedded in five-axis DTQC"
    )
    figure.savefig(output / STATIC_FILES[0], dpi=170)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(9.0, 5.0), constrained_layout=True)
    center = mode0.shape[-2] // 2
    coordinate = np.arange(mode0.shape[-1])
    for index, quark in enumerate(QUARKS):
        axis.plot(
            coordinate,
            np.real(mode0[index, center]),
            label=str(quark["name"]),
        )
    axis.set(
        title="Six FP quark modes on the DTQC carrier",
        xlabel="central-row sample",
        ylabel="Re normalized mode",
    )
    axis.legend(ncol=3)
    figure.savefig(output / STATIC_FILES[1], dpi=170)
    plt.close(figure)

    probability = np.asarray(simulation["probabilities"])
    trace = probability[:, probability.shape[1] // 2, probability.shape[2] // 2]
    centered = trace - float(np.mean(trace))
    spectrum = np.abs(np.fft.rfft(centered))
    frequencies = np.fft.rfftfreq(centered.size, d=1.0)
    figure, axes = plt.subplots(
        1,
        2,
        figsize=(10.5, 4.2),
        constrained_layout=True,
    )
    axes[0].plot(np.arange(trace.size), trace)
    axes[0].set(
        title="center probability over discrete time",
        xlabel="step",
        ylabel="probability",
    )
    axes[1].stem(frequencies[1:], spectrum[1:], basefmt=" ")
    axes[1].set(
        title="quasiperiodic/Floquet response spectrum",
        xlabel="cycles per step",
        ylabel="amplitude",
    )
    figure.savefig(output / STATIC_FILES[2], dpi=170)
    plt.close(figure)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def generate_fp_quantum_artifacts(
    output_dir: str | Path,
    bundle_factory: Callable[[float], Mapping[str, Any]],
    *,
    simulation: bool = True,
) -> dict[str, Path]:
    """Generate normalized FP-wave, quark-mode, Floquet, and entanglement evidence."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    frame_count = 18 if simulation else 10
    state = simulate_quantum_bridge(bundle_factory, frame_count=frame_count)
    removals = source_removal_metrics(bundle_factory, frame_count=frame_count)
    if not all(bool(row["necessary"]) for row in removals):
        raise RuntimeError(f"FP-DTQC quantum source removal failed: {removals}")
    norm_residual = float(np.max(np.abs(state["norms"] - 1.0)))
    if norm_residual > 1e-12:
        raise RuntimeError("FP-DTQC wavefunction norm drift exceeded tolerance")
    _save_static(output, state)
    _save_gifs(output, state)

    np.savez_compressed(
        output / DATA_FILES[0],
        probabilities=state["probabilities"],
        phases=state["phases"],
        wavefunctions=state["wavefunctions"],
        quark_modes=state["quark_modes"],
        pair_states=state["pair_states"],
        reduced_density_matrices=state["rho_a"],
        entanglement_entropy=state["entanglement_entropy"],
        concurrence=state["concurrence"],
        purity=state["purity"],
        bell_fidelity=state["bell_fidelity"],
        norms=state["norms"],
        quark_masses_gev=np.asarray(
            [float(quark["mass_gev"]) for quark in QUARKS]
        ),
        quark_charges=np.asarray(
            [float(quark["charge"]) for quark in QUARKS]
        ),
        quark_frequency_factors=np.asarray(
            [float(quark["frequency_factor"]) for quark in QUARKS]
        ),
        normalized_quark_frequencies=normalized_quark_frequencies(),
    )
    metrics = [
        {"metric": "frame_count", "value": frame_count},
        {"metric": "wave_norm_max_residual", "value": norm_residual},
        {
            "metric": "minimum_entanglement_entropy",
            "value": float(np.min(state["entanglement_entropy"])),
        },
        {
            "metric": "maximum_entanglement_entropy",
            "value": float(np.max(state["entanglement_entropy"])),
        },
        {
            "metric": "minimum_concurrence",
            "value": float(np.min(state["concurrence"])),
        },
        {
            "metric": "maximum_concurrence",
            "value": float(np.max(state["concurrence"])),
        },
        {"metric": "quark_mode_count", "value": len(QUARKS)},
        {
            "metric": "intrinsic_axis_count",
            "value": int(state["frames"][0]["coefficients"].shape[1]),
        },
    ]
    _write_csv(output / DATA_FILES[1], metrics)
    _write_csv(output / DATA_FILES[2], removals)
    manifest = {
        "schema_version": "1.0",
        "claim_boundary": (
            "finite normalized computational quantum-wave evidence; not an empirical "
            "quantum validation or formal proof substitute"
        ),
        "source_domains": {
            "wave_functionality": [
                "fp_sine_wave",
                "fp_pi_wave",
                "two-wave interference",
                "multi-axis fp waves",
            ],
            "particle_models": [
                "six quark masses",
                "charges",
                "frequency factors",
                "spin",
            ],
            "entanglement": (
                "legacy midpoint synchronizer upgraded to a normalized complex "
                "two-qubit state and reduced-density-matrix metrics"
            ),
        },
        "source_sha256": SOURCE_SHA256,
        "dtqc_binding": {
            "clock": (
                "two irrational discrete drive phases plus alternating Flowpoint sector"
            ),
            "carrier": (
                "five intrinsic DTQC axes with independently applied Elastic-pi channels"
            ),
            "wave": (
                "six normalized complex quark modes and source-faithful interference"
            ),
            "entanglement": (
                "Schmidt-form pair state with von Neumann entropy, purity, "
                "concurrence, and Bell fidelity"
            ),
        },
        "generated_files": list(ALL_FILES),
        "source_removal": {
            str(row["source"]): float(row["removal_residual"])
            for row in removals
        },
        "invariants": {
            "wave_norm_max_residual": norm_residual,
            "density_trace_max_residual": float(
                np.max(
                    np.abs(
                        np.trace(state["rho_a"], axis1=1, axis2=2) - 1.0
                    )
                )
            ),
            "minimum_entanglement_entropy": float(
                np.min(state["entanglement_entropy"])
            ),
            "minimum_concurrence": float(np.min(state["concurrence"])),
        },
    }
    (output / DATA_FILES[3]).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    missing = [name for name in ALL_FILES if not (output / name).is_file()]
    if missing:
        raise RuntimeError(f"missing FP-DTQC quantum artifacts: {missing}")
    return {name: output / name for name in ALL_FILES}
