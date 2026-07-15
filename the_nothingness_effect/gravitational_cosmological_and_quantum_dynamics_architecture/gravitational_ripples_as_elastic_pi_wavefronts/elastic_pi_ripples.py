"""Damped Elastic-pi ripple toy model for manuscript Figure 7."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts.wave_adapters import radial_wave_interference


@dataclass(frozen=True)
class RippleParams:
    n: int = 320
    steps: int = 260
    length: float = 20.0
    dt: float = 0.02
    c_E: float = 1.0
    gamma: float = 0.08
    xi: float = -0.08
    center: float = 0.0
    width: float = 0.9
    amplitude: float = 0.8


def initialize_ringdown_wave(
    x: np.ndarray,
    center: float,
    width: float,
    amplitude: float,
) -> np.ndarray:
    return amplitude * np.exp(-((np.asarray(x) - center) ** 2) / (2.0 * width**2))


def laplacian_1d(u: np.ndarray, dx: float) -> np.ndarray:
    values = np.asarray(u, dtype=float)
    lap = np.zeros_like(values)
    lap[1:-1] = (values[2:] - 2.0 * values[1:-1] + values[:-2]) / (dx**2)
    return lap


def elastic_pi_wave_step(
    u_prev: np.ndarray,
    u: np.ndarray,
    dt: float,
    dx: float,
    c_E: float,
    gamma: float,
    xi: float,
) -> np.ndarray:
    velocity = (u - u_prev) / dt
    lap = laplacian_1d(u, dx)
    acceleration = c_E**2 * lap - gamma * velocity + xi * u**3
    u_next = 2.0 * u - u_prev + dt**2 * acceleration
    u_next[0] = 0.0
    u_next[-1] = 0.0
    return np.clip(u_next, -5.0, 5.0)


def simulate_elastic_pi_ripple(
    params: RippleParams | None = None,
) -> dict[str, np.ndarray | dict[str, float]]:
    sim_params = params or RippleParams()
    x = np.linspace(-sim_params.length / 2.0, sim_params.length / 2.0, sim_params.n)
    dx = float(x[1] - x[0])
    initial = initialize_ringdown_wave(
        x, sim_params.center, sim_params.width, sim_params.amplitude
    )
    u_prev = initial.copy()
    u = initial.copy()
    history = np.empty((sim_params.steps + 1, sim_params.n), dtype=float)
    history[0] = u
    for index in range(1, sim_params.steps + 1):
        u_next = elastic_pi_wave_step(
            u_prev, u, sim_params.dt, dx, sim_params.c_E, sim_params.gamma, sim_params.xi
        )
        history[index] = u_next
        u_prev, u = u, u_next
    metrics = compute_ripple_metrics(history, dx)
    return {
        "x": x,
        "time": np.arange(sim_params.steps + 1) * sim_params.dt,
        "history": history,
        "metrics": metrics,
    }


def compute_ripple_metrics(history: np.ndarray, dx: float = 1.0) -> dict[str, float]:
    values = np.asarray(history, dtype=float)
    amplitude = np.max(np.abs(values), axis=1)
    gradient = np.gradient(values, dx, axis=1)
    energy = np.trapezoid(values**2 + gradient**2, dx=dx, axis=1)
    skew_proxy = np.mean((values - values.mean(axis=1, keepdims=True)) ** 3, axis=1)
    late = values[-1]
    early = values[max(1, len(values) // 10)]
    distortion = float(np.linalg.norm(late - early) / (np.linalg.norm(early) + 1e-12))
    return {
        "initial_amplitude": float(amplitude[0]),
        "final_amplitude": float(amplitude[-1]),
        "initial_energy": float(energy[0]),
        "final_energy": float(energy[-1]),
        "max_abs_skew_proxy": float(np.max(np.abs(skew_proxy))),
        "late_time_distortion_proxy": distortion,
        "nan_count": int(np.isnan(values).sum()),
    }


def _normalize_series(values: np.ndarray) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    centered = data - float(np.mean(data))
    scale = float(np.max(np.abs(centered))) + 1e-12
    return centered / scale


def dominant_mode_projection(
    history: np.ndarray,
    x: np.ndarray,
    *,
    mode_number: int = 1,
) -> np.ndarray:
    values = np.asarray(history, dtype=float)
    coordinates = np.asarray(x, dtype=float)
    span = float(coordinates.max() - coordinates.min())
    basis = np.sin(mode_number * np.pi * (coordinates - coordinates.min()) / max(span, 1e-12))
    projection = values @ basis / (float(np.dot(basis, basis)) + 1e-12)
    return np.asarray(projection, dtype=float)


def energy_envelope(history: np.ndarray, x: np.ndarray) -> np.ndarray:
    values = np.asarray(history, dtype=float)
    coordinates = np.asarray(x, dtype=float)
    gradients = np.gradient(values, coordinates, axis=1)
    energy = np.trapezoid(values**2 + 0.25 * gradients**2, coordinates, axis=1)
    return np.sqrt(np.maximum(energy, 0.0))


def interference_mode_projection(history: np.ndarray, x: np.ndarray) -> np.ndarray:
    basis = radial_wave_interference(x, time=0.0)
    values = np.asarray(history, dtype=float)
    projection = values @ basis / (float(np.dot(basis, basis)) + 1e-12)
    return np.asarray(projection, dtype=float)


def prepare_tne_ringdown_projection(
    params: RippleParams | None = None,
) -> dict[str, np.ndarray | dict[str, float]]:
    result = simulate_elastic_pi_ripple(params)
    x = np.asarray(result["x"], dtype=float)
    history = np.asarray(result["history"], dtype=float)
    centerline = history[:, len(x) // 2]
    mode_1 = dominant_mode_projection(history, x, mode_number=1)
    mode_2 = dominant_mode_projection(history, x, mode_number=2)
    energy = energy_envelope(history, x)
    interference = interference_mode_projection(history, x)
    composite = (
        0.45 * _normalize_series(centerline)
        + 0.25 * _normalize_series(mode_1)
        + 0.15 * _normalize_series(mode_2)
        + 0.15 * _normalize_series(interference)
    )
    return {
        "time": np.asarray(result["time"], dtype=float),
        "x": x,
        "centerline": np.asarray(centerline, dtype=float),
        "dominant_mode_1": np.asarray(mode_1, dtype=float),
        "dominant_mode_2": np.asarray(mode_2, dtype=float),
        "energy_envelope": np.asarray(energy, dtype=float),
        "interference_projection": np.asarray(interference, dtype=float),
        "composite_projection": np.asarray(composite, dtype=float),
        "metrics": result["metrics"],
        "params": params.__dict__ if params is not None else RippleParams().__dict__,
    }
