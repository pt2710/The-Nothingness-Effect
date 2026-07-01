"""Damped Elastic-pi ripple toy model for manuscript Figure 7."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


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
