"""Finite locality-driven gravity toy model for manuscript Figure 6.

This module provides a deterministic particle simulation that illustrates how a
locality-weighted attraction plus weak shear can form spiral-like structure.
It is not a full galaxy or general-relativistic simulation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LocalityGravityParams:
    n_particles: int = 240
    steps: int = 180
    dt: float = 0.035
    G_eff: float = 0.25
    sigma: float = 2.2
    eps: float = 0.08
    shear: float = 0.12
    damping: float = 0.992
    radial_scale: float = 3.0


def locality_kernel(r: np.ndarray, sigma: float) -> np.ndarray:
    if sigma <= 0:
        raise ValueError("sigma must be positive.")
    radius = np.asarray(r, dtype=float)
    return np.exp(-(radius**2) / (2.0 * sigma**2))


def locality_force(
    positions: np.ndarray,
    G_eff: float,
    sigma: float,
    eps: float,
    shear: float = 0.0,
) -> np.ndarray:
    """Return locality-weighted central attraction plus weak tangential shear."""

    pos = np.asarray(positions, dtype=float)
    r = np.linalg.norm(pos, axis=1) + eps
    kernel = locality_kernel(r, sigma)
    central = -G_eff * kernel[:, None] * pos / (r[:, None] ** 2)
    tangent = np.column_stack([-pos[:, 1], pos[:, 0]])
    tangent_norm = np.linalg.norm(tangent, axis=1) + eps
    shear_force = shear * kernel[:, None] * tangent / tangent_norm[:, None]
    return central + shear_force


def initialize_spiral_particles(
    n: int,
    seed: int,
    radial_scale: float,
) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    angles = rng.uniform(0.0, 2.0 * np.pi, n)
    radii = radial_scale * np.sqrt(rng.uniform(0.05, 1.0, n))
    positions = np.column_stack([radii * np.cos(angles), radii * np.sin(angles)])
    tangent = np.column_stack([-np.sin(angles), np.cos(angles)])
    velocities = 0.08 * tangent + rng.normal(0.0, 0.015, size=(n, 2))
    return {"positions": positions, "velocities": velocities}


def step_locality_gravity(
    state: dict[str, np.ndarray],
    dt: float,
    params: LocalityGravityParams,
) -> dict[str, np.ndarray]:
    force = locality_force(
        state["positions"],
        G_eff=params.G_eff,
        sigma=params.sigma,
        eps=params.eps,
        shear=params.shear,
    )
    velocities = (state["velocities"] + dt * force) * params.damping
    positions = state["positions"] + dt * velocities
    return {"positions": positions, "velocities": velocities}


def simulate_locality_spiral(
    params: LocalityGravityParams | None = None,
    steps: int | None = None,
    seed: int = 2710,
) -> dict[str, np.ndarray]:
    sim_params = params or LocalityGravityParams()
    step_count = sim_params.steps if steps is None else steps
    state = initialize_spiral_particles(sim_params.n_particles, seed, sim_params.radial_scale)
    history = np.empty((step_count + 1, sim_params.n_particles, 2), dtype=float)
    history[0] = state["positions"]
    for index in range(1, step_count + 1):
        state = step_locality_gravity(state, sim_params.dt, sim_params)
        history[index] = state["positions"]
    return {
        "history": history,
        "positions": state["positions"],
        "velocities": state["velocities"],
    }


def compute_spiral_metrics(history: np.ndarray) -> dict[str, float]:
    positions = np.asarray(history, dtype=float)
    final = positions[-1]
    initial = positions[0]
    radius_initial = np.linalg.norm(initial, axis=1)
    radius_final = np.linalg.norm(final, axis=1)
    theta = np.arctan2(final[:, 1], final[:, 0])
    radial_rank = np.argsort(np.argsort(radius_final)) / max(1, len(radius_final) - 1)
    spiral_phase = theta - 3.0 * radial_rank
    coherence = np.abs(np.mean(np.exp(1j * spiral_phase)))
    finite_energy_proxy = float(np.mean(np.sum(np.diff(positions, axis=0) ** 2, axis=2)))
    return {
        "initial_mean_radius": float(np.mean(radius_initial)),
        "final_mean_radius": float(np.mean(radius_final)),
        "radial_concentration": float(np.mean(radius_initial) - np.mean(radius_final)),
        "spiral_order_parameter": float(coherence),
        "finite_energy_proxy": finite_energy_proxy,
        "max_abs_position": float(np.max(np.abs(positions))),
        "nan_count": int(np.isnan(positions).sum()),
    }
