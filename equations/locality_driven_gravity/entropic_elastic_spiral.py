"""Finite TNE locality-driven galaxy proxy with mass-field feedback.

This module implements a deterministic entropic-elastic spacetime-continuum toy
model in which mass-bearing bodies deform a locality field and the resulting
gravity-plus-elastic tension field feeds back into body motion. It is not a
full astrophysical simulation, not an empirical validation claim, and not a
formal proof substitute.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np

from equations.elastic_pi_ripples.wave_adapters import radial_wave_interference


class BodyType(str, Enum):
    CENTRAL_MASS = "central_mass"
    STAR_SYSTEM = "star_system"
    GAS_CLOUD = "gas_cloud"
    CLUSTER = "cluster"
    OPTIONAL_SMALL_BODY = "optional_small_body"


@dataclass(frozen=True)
class LocalityGravityParams:
    n_particles: int = 240
    steps: int = 180
    dt: float = 0.032
    G_eff: float = 0.28
    sigma: float = 2.8
    eps: float = 0.16
    shear: float = 0.18
    damping: float = 0.995
    radial_scale: float = 3.1
    central_mass: float = 220.0
    star_mass_scale: float = 1.0
    gas_mass_scale: float = 0.72
    cluster_mass_scale: float = 2.4
    grid_size: int = 52
    density_sigma: float = 0.34
    entropic_alpha: float = 0.95
    elastic_beta: float = 0.55
    shear_gamma: float = 0.48
    relax: float = 0.86
    elastic_kappa: float = 0.5
    bar_strength: float = 0.22
    asymmetry_seed: float = 0.075
    vertical_scale: float = 0.22


@dataclass(frozen=True)
class SpiralBody:
    body_type: BodyType
    mass: float
    radius: float
    position: tuple[float, float]
    velocity: tuple[float, float]
    spin: float
    luminosity: float
    entropic_coupling: float
    elastic_coupling: float


def locality_kernel(r: np.ndarray, sigma: float) -> np.ndarray:
    if sigma <= 0:
        raise ValueError("sigma must be positive.")
    radius = np.asarray(r, dtype=float)
    return np.exp(-(radius**2) / (2.0 * sigma**2))


def _body_mix_counts(n_particles: int) -> tuple[int, int, int, int]:
    stars = max(48, int(round(0.58 * n_particles)))
    gas = max(36, int(round(0.28 * n_particles)))
    clusters = max(12, int(round(0.10 * n_particles)))
    optional = max(4, n_particles - stars - gas - clusters)
    total = stars + gas + clusters + optional
    if total > n_particles:
        optional -= total - n_particles
    elif total < n_particles:
        stars += n_particles - total
    return stars, gas, clusters, max(optional, 0)


def initialize_spiral_bodies(
    params: LocalityGravityParams,
    seed: int = 2710,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    stars, gas, clusters, optional = _body_mix_counts(params.n_particles)
    total = 1 + stars + gas + clusters + optional

    body_types: list[BodyType] = [BodyType.CENTRAL_MASS]
    body_types.extend([BodyType.STAR_SYSTEM] * stars)
    body_types.extend([BodyType.GAS_CLOUD] * gas)
    body_types.extend([BodyType.CLUSTER] * clusters)
    body_types.extend([BodyType.OPTIONAL_SMALL_BODY] * optional)

    masses = np.empty(total, dtype=float)
    softening = np.empty(total, dtype=float)
    entropic_coupling = np.empty(total, dtype=float)
    elastic_coupling = np.empty(total, dtype=float)
    luminosity = np.empty(total, dtype=float)
    spin = np.empty(total, dtype=float)
    positions = np.zeros((total, 2), dtype=float)
    velocities = np.zeros((total, 2), dtype=float)
    body_radius = np.zeros(total, dtype=float)

    masses[0] = params.central_mass
    softening[0] = 0.32
    entropic_coupling[0] = 1.4
    elastic_coupling[0] = 1.2
    luminosity[0] = 1.3
    spin[0] = 0.08
    body_radius[0] = 0.2

    disk_types = body_types[1:]
    disk_count = len(disk_types)
    base_u = rng.uniform(0.02, 1.0, disk_count)
    radii = params.radial_scale * np.sqrt(base_u)
    base_theta = rng.uniform(0.0, 2.0 * np.pi, disk_count)
    bar_phase = params.bar_strength * np.sin(2.0 * base_theta)
    wave_seed = params.asymmetry_seed * radial_wave_interference(
        radii,
        time=0.15,
        amplitude_1=1.0,
        frequency_1=1.25,
        amplitude_2=0.55,
        frequency_2=2.1,
    )
    arm_selector = rng.integers(0, 2, disk_count) * np.pi
    theta = base_theta + arm_selector + 1.9 * (radii / max(params.radial_scale, 1e-12)) + bar_phase + wave_seed
    theta += rng.normal(0.0, 0.06, disk_count)
    positions[1:, 0] = radii * np.cos(theta)
    positions[1:, 1] = radii * np.sin(theta)

    radii_safe = np.maximum(radii, 0.18)
    enclosed_mass = params.central_mass * (1.0 - np.exp(-radii_safe / max(params.radial_scale, 1e-12)))
    circular_speed = np.sqrt(params.G_eff * (params.central_mass + enclosed_mass) / (radii_safe + params.eps))
    differential_factor = 0.75 + 0.28 * np.exp(-radii_safe / max(params.radial_scale, 1e-12))
    tangential = circular_speed * differential_factor
    tangent_hat = np.column_stack([-np.sin(theta), np.cos(theta)])
    radial_hat = np.column_stack([np.cos(theta), np.sin(theta)])
    velocities[1:] = tangent_hat * tangential[:, None]
    velocities[1:] += radial_hat * (0.025 * wave_seed[:, None])
    velocities[1:] += rng.normal(0.0, 0.012, size=(disk_count, 2))

    index = 1
    for body_type in disk_types:
        if body_type == BodyType.STAR_SYSTEM:
            masses[index] = params.star_mass_scale * rng.uniform(0.8, 1.35)
            softening[index] = 0.12
            entropic_coupling[index] = 0.78
            elastic_coupling[index] = 0.68
            luminosity[index] = rng.uniform(0.8, 1.2)
            spin[index] = rng.uniform(-0.05, 0.05)
            body_radius[index] = 0.05
        elif body_type == BodyType.GAS_CLOUD:
            masses[index] = params.gas_mass_scale * rng.uniform(0.55, 1.15)
            softening[index] = 0.18
            entropic_coupling[index] = 1.12
            elastic_coupling[index] = 1.08
            luminosity[index] = rng.uniform(0.45, 0.75)
            spin[index] = rng.uniform(-0.03, 0.03)
            body_radius[index] = 0.08
        elif body_type == BodyType.CLUSTER:
            masses[index] = params.cluster_mass_scale * rng.uniform(1.0, 1.6)
            softening[index] = 0.16
            entropic_coupling[index] = 1.0
            elastic_coupling[index] = 0.92
            luminosity[index] = rng.uniform(1.05, 1.45)
            spin[index] = rng.uniform(-0.06, 0.06)
            body_radius[index] = 0.09
        else:
            masses[index] = 0.45 * rng.uniform(0.7, 1.1)
            softening[index] = 0.1
            entropic_coupling[index] = 0.62
            elastic_coupling[index] = 0.55
            luminosity[index] = rng.uniform(0.3, 0.6)
            spin[index] = rng.uniform(-0.04, 0.04)
            body_radius[index] = 0.035
        index += 1

    bodies = [
        SpiralBody(
            body_type=body_types[idx],
            mass=float(masses[idx]),
            radius=float(body_radius[idx]),
            position=(float(positions[idx, 0]), float(positions[idx, 1])),
            velocity=(float(velocities[idx, 0]), float(velocities[idx, 1])),
            spin=float(spin[idx]),
            luminosity=float(luminosity[idx]),
            entropic_coupling=float(entropic_coupling[idx]),
            elastic_coupling=float(elastic_coupling[idx]),
        )
        for idx in range(total)
    ]
    return {
        "bodies": bodies,
        "body_types": np.asarray([body_type.value for body_type in body_types], dtype=object),
        "masses": masses,
        "softening": softening,
        "entropic_coupling": entropic_coupling,
        "elastic_coupling": elastic_coupling,
        "luminosity": luminosity,
        "spin": spin,
        "positions": positions,
        "velocities": velocities,
    }


def _grid_coordinates(params: LocalityGravityParams) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    bound = float(params.radial_scale * 1.45)
    axis = np.linspace(-bound, bound, params.grid_size)
    dx = float(axis[1] - axis[0]) if len(axis) > 1 else 1.0
    xx, yy = np.meshgrid(axis, axis)
    return axis, np.stack([xx, yy], axis=-1), np.array([dx, dx], dtype=float)


def density_field(
    positions: np.ndarray,
    masses: np.ndarray,
    params: LocalityGravityParams,
) -> dict[str, np.ndarray]:
    axis, grid, spacing = _grid_coordinates(params)
    dx = grid[..., 0][..., None] - np.asarray(positions, dtype=float)[:, 0]
    dy = grid[..., 1][..., None] - np.asarray(positions, dtype=float)[:, 1]
    sigma = max(params.density_sigma, 0.12)
    weights = np.exp(-(dx**2 + dy**2) / (2.0 * sigma**2))
    density = np.sum(weights * np.asarray(masses, dtype=float)[None, None, :], axis=2)
    density /= 2.0 * np.pi * sigma**2
    return {
        "axis": axis,
        "grid": grid,
        "spacing": spacing,
        "density": density,
    }


def _angular_velocity_field(
    positions: np.ndarray,
    velocities: np.ndarray,
    masses: np.ndarray,
    grid: np.ndarray,
    sigma: float,
) -> np.ndarray:
    pos = np.asarray(positions, dtype=float)
    vel = np.asarray(velocities, dtype=float)
    mass = np.asarray(masses, dtype=float)
    radii = np.linalg.norm(pos, axis=1) + 1e-12
    tangential = (pos[:, 0] * vel[:, 1] - pos[:, 1] * vel[:, 0]) / radii
    omega = tangential / radii
    dx = grid[..., 0][..., None] - pos[:, 0]
    dy = grid[..., 1][..., None] - pos[:, 1]
    weights = np.exp(-(dx**2 + dy**2) / (2.0 * sigma**2)) * mass[None, None, :]
    numerator = np.sum(weights * omega[None, None, :], axis=2)
    denominator = np.sum(weights, axis=2) + 1e-12
    return numerator / denominator


def entropic_elastic_field(
    positions: np.ndarray,
    velocities: np.ndarray,
    masses: np.ndarray,
    previous_tension: np.ndarray | None,
    params: LocalityGravityParams,
) -> dict[str, np.ndarray]:
    density_bundle = density_field(positions, masses, params)
    density = density_bundle["density"]
    grid = density_bundle["grid"]
    axis = density_bundle["axis"]
    density_norm = density / (np.max(density) + 1e-12)
    grad_y, grad_x = np.gradient(density_norm, axis, axis, edge_order=1)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    omega_field = _angular_velocity_field(positions, velocities, masses, grid, max(params.density_sigma, 0.12) * 1.4)
    shear_y, shear_x = np.gradient(omega_field, axis, axis, edge_order=1)
    shear_mag = np.sqrt(shear_x**2 + shear_y**2)
    radius_grid = np.sqrt(grid[..., 0] ** 2 + grid[..., 1] ** 2)
    wave_seed = radial_wave_interference(radius_grid, time=0.18, amplitude_1=0.8, frequency_1=1.0, amplitude_2=0.32, frequency_2=2.0)
    wave_seed = (wave_seed - np.min(wave_seed)) / (np.ptp(wave_seed) + 1e-12)
    previous = np.zeros_like(density_norm) if previous_tension is None else np.asarray(previous_tension, dtype=float)
    entropy = 0.64 * density_norm + 0.24 * grad_mag + 0.12 * wave_seed
    tension = (
        params.relax * previous
        + params.entropic_alpha * density_norm
        + params.elastic_beta * grad_mag
        + params.shear_gamma * shear_mag
        + 0.18 * wave_seed
    )
    tension /= np.max(tension) + 1e-12
    strain_xx = np.gradient(tension, axis, axis=1, edge_order=1)
    strain_yy = np.gradient(tension, axis, axis=0, edge_order=1)
    strain_xy = 0.5 * (np.gradient(tension, axis, axis=0, edge_order=1) + np.gradient(tension, axis, axis=1, edge_order=1))
    return {
        **density_bundle,
        "entropy": entropy,
        "tension": tension,
        "shear": shear_mag,
        "omega": omega_field,
        "strain_xx": strain_xx,
        "strain_yy": strain_yy,
        "strain_xy": strain_xy,
    }


def gravity_acceleration(
    positions: np.ndarray,
    masses: np.ndarray,
    softening: np.ndarray,
    G_eff: float,
    eps: float,
) -> np.ndarray:
    pos = np.asarray(positions, dtype=float)
    mass = np.asarray(masses, dtype=float)
    soften = np.asarray(softening, dtype=float)
    diff = pos[None, :, :] - pos[:, None, :]
    dist2 = np.sum(diff**2, axis=2) + (eps + soften[:, None] + soften[None, :]) ** 2
    np.fill_diagonal(dist2, np.inf)
    inv_dist3 = 1.0 / (dist2 * np.sqrt(dist2))
    weighted = diff * (mass[None, :, None] * inv_dist3[:, :, None])
    return G_eff * np.sum(weighted, axis=1)


def _sample_grid_vector(
    positions: np.ndarray,
    axis: np.ndarray,
    grad_x: np.ndarray,
    grad_y: np.ndarray,
) -> np.ndarray:
    pos = np.asarray(positions, dtype=float)
    x_idx = np.clip(np.searchsorted(axis, pos[:, 0]) - 1, 0, len(axis) - 2)
    y_idx = np.clip(np.searchsorted(axis, pos[:, 1]) - 1, 0, len(axis) - 2)
    x0 = axis[x_idx]
    x1 = axis[x_idx + 1]
    y0 = axis[y_idx]
    y1 = axis[y_idx + 1]
    tx = (pos[:, 0] - x0) / (x1 - x0 + 1e-12)
    ty = (pos[:, 1] - y0) / (y1 - y0 + 1e-12)

    def bilinear(field: np.ndarray) -> np.ndarray:
        f00 = field[y_idx, x_idx]
        f10 = field[y_idx, x_idx + 1]
        f01 = field[y_idx + 1, x_idx]
        f11 = field[y_idx + 1, x_idx + 1]
        return (1.0 - tx) * (1.0 - ty) * f00 + tx * (1.0 - ty) * f10 + (1.0 - tx) * ty * f01 + tx * ty * f11

    sampled_x = bilinear(grad_x)
    sampled_y = bilinear(grad_y)
    return np.column_stack([sampled_x, sampled_y])


def locality_force(
    positions: np.ndarray,
    masses: np.ndarray | None = None,
    G_eff: float = 0.25,
    sigma: float = 2.2,
    eps: float = 0.08,
    shear: float = 0.0,
    softening: np.ndarray | None = None,
) -> np.ndarray:
    pos = np.asarray(positions, dtype=float)
    if masses is None:
        masses = np.ones(pos.shape[0], dtype=float)
    if softening is None:
        softening = np.full(pos.shape[0], eps, dtype=float)
    central_gravity = gravity_acceleration(pos, np.asarray(masses, dtype=float), np.asarray(softening, dtype=float), G_eff, eps)
    r = np.linalg.norm(pos, axis=1) + eps
    kernel = locality_kernel(r, sigma)
    tangent = np.column_stack([-pos[:, 1], pos[:, 0]])
    tangent_norm = np.linalg.norm(tangent, axis=1) + eps
    shear_force = shear * kernel[:, None] * tangent / tangent_norm[:, None]
    return central_gravity + shear_force


def _elastic_acceleration(
    positions: np.ndarray,
    field: dict[str, np.ndarray],
    entropic_coupling: np.ndarray,
    elastic_coupling: np.ndarray,
    params: LocalityGravityParams,
) -> np.ndarray:
    axis = np.asarray(field["axis"], dtype=float)
    tension = np.asarray(field["tension"], dtype=float)
    grad_y, grad_x = np.gradient(tension, axis, axis, edge_order=1)
    sampled = _sample_grid_vector(positions, axis, grad_x, grad_y)
    coupling = (0.55 * np.asarray(entropic_coupling, dtype=float) + 0.45 * np.asarray(elastic_coupling, dtype=float))[:, None]
    return -params.elastic_kappa * coupling * sampled


def step_locality_gravity(
    state: dict[str, np.ndarray],
    dt: float,
    params: LocalityGravityParams,
) -> dict[str, np.ndarray]:
    field = entropic_elastic_field(
        state["positions"],
        state["velocities"],
        state["masses"],
        state.get("tension"),
        params,
    )
    grav = gravity_acceleration(state["positions"], state["masses"], state["softening"], params.G_eff, params.eps)
    local = locality_force(
        state["positions"],
        masses=state["masses"],
        G_eff=0.12 * params.G_eff,
        sigma=params.sigma,
        eps=params.eps,
        shear=params.shear,
        softening=state["softening"],
    )
    elastic = _elastic_acceleration(
        state["positions"],
        field,
        state["entropic_coupling"],
        state["elastic_coupling"],
        params,
    )
    acceleration = grav + local + elastic
    velocities = (state["velocities"] + dt * acceleration) * params.damping
    positions = state["positions"] + dt * velocities
    positions[0] = 0.0
    velocities[0] = 0.0
    return {
        **state,
        "positions": positions,
        "velocities": velocities,
        "acceleration": acceleration,
        "density": field["density"],
        "entropy": field["entropy"],
        "tension": field["tension"],
        "shear_field": field["shear"],
        "omega_field": field["omega"],
        "strain_xx": field["strain_xx"],
        "strain_yy": field["strain_yy"],
        "strain_xy": field["strain_xy"],
        "grid_axis": field["axis"],
    }


def _initial_state(params: LocalityGravityParams, seed: int) -> dict[str, np.ndarray]:
    initialized = initialize_spiral_bodies(params, seed=seed)
    state = {
        "positions": np.asarray(initialized["positions"], dtype=float),
        "velocities": np.asarray(initialized["velocities"], dtype=float),
        "masses": np.asarray(initialized["masses"], dtype=float),
        "softening": np.asarray(initialized["softening"], dtype=float),
        "entropic_coupling": np.asarray(initialized["entropic_coupling"], dtype=float),
        "elastic_coupling": np.asarray(initialized["elastic_coupling"], dtype=float),
        "luminosity": np.asarray(initialized["luminosity"], dtype=float),
        "spin": np.asarray(initialized["spin"], dtype=float),
        "body_types": np.asarray(initialized["body_types"], dtype=object),
    }
    field = entropic_elastic_field(state["positions"], state["velocities"], state["masses"], None, params)
    state.update(
        {
            "density": field["density"],
            "entropy": field["entropy"],
            "tension": field["tension"],
            "shear_field": field["shear"],
            "omega_field": field["omega"],
            "strain_xx": field["strain_xx"],
            "strain_yy": field["strain_yy"],
            "strain_xy": field["strain_xy"],
            "grid_axis": field["axis"],
            "bodies": initialized["bodies"],
        }
    )
    return state


def simulate_locality_spiral(
    params: LocalityGravityParams | None = None,
    steps: int | None = None,
    seed: int = 2710,
) -> dict[str, Any]:
    sim_params = params or LocalityGravityParams()
    step_count = sim_params.steps if steps is None else steps
    state = _initial_state(sim_params, seed)
    n_bodies = state["positions"].shape[0]
    grid_size = sim_params.grid_size

    history = np.empty((step_count + 1, n_bodies, 2), dtype=np.float32)
    velocity_history = np.empty((step_count + 1, n_bodies, 2), dtype=np.float32)
    density_history = np.empty((step_count + 1, grid_size, grid_size), dtype=np.float32)
    tension_history = np.empty((step_count + 1, grid_size, grid_size), dtype=np.float32)
    entropy_history = np.empty((step_count + 1, grid_size, grid_size), dtype=np.float32)

    history[0] = state["positions"]
    velocity_history[0] = state["velocities"]
    density_history[0] = state["density"]
    tension_history[0] = state["tension"]
    entropy_history[0] = state["entropy"]
    for index in range(1, step_count + 1):
        state = step_locality_gravity(state, sim_params.dt, sim_params)
        history[index] = state["positions"]
        velocity_history[index] = state["velocities"]
        density_history[index] = state["density"]
        tension_history[index] = state["tension"]
        entropy_history[index] = state["entropy"]

    metrics = compute_spiral_metrics(
        history=history,
        velocity_history=velocity_history,
        masses=state["masses"],
        body_types=state["body_types"],
        tension_field=state["tension"],
    )
    return {
        "history": history,
        "velocity_history": velocity_history,
        "density_history": density_history,
        "tension_history": tension_history,
        "entropy_history": entropy_history,
        "positions": np.asarray(state["positions"], dtype=float),
        "velocities": np.asarray(state["velocities"], dtype=float),
        "masses": np.asarray(state["masses"], dtype=float),
        "softening": np.asarray(state["softening"], dtype=float),
        "body_types": np.asarray(state["body_types"], dtype=object),
        "luminosity": np.asarray(state["luminosity"], dtype=float),
        "spin": np.asarray(state["spin"], dtype=float),
        "grid_axis": np.asarray(state["grid_axis"], dtype=float),
        "metrics": metrics,
        "bodies": state["bodies"],
    }


def radial_velocity_profile(
    positions: np.ndarray,
    velocities: np.ndarray,
    masses: np.ndarray | None = None,
    *,
    n_bins: int = 10,
) -> dict[str, np.ndarray]:
    pos = np.asarray(positions, dtype=float)
    vel = np.asarray(velocities, dtype=float)
    mass = np.ones(pos.shape[0], dtype=float) if masses is None else np.asarray(masses, dtype=float)
    radii = np.linalg.norm(pos, axis=1)
    tangent = np.column_stack([-pos[:, 1], pos[:, 0]])
    tangent /= np.linalg.norm(tangent, axis=1, keepdims=True) + 1e-12
    tangential_velocity = np.sum(vel * tangent, axis=1)
    radial_hat = pos / (radii[:, None] + 1e-12)
    radial_velocity = np.sum(vel * radial_hat, axis=1)
    bins = np.linspace(max(1e-6, float(radii.min())), float(radii.max()), n_bins + 1)
    centers: list[float] = []
    mean_velocity: list[float] = []
    median_velocity: list[float] = []
    std_velocity: list[float] = []
    density_profile_values: list[float] = []
    mean_radial_velocity: list[float] = []
    counts: list[int] = []
    for index in range(len(bins) - 1):
        right_mask = radii <= bins[index + 1] if index == len(bins) - 2 else radii < bins[index + 1]
        mask = (radii >= bins[index]) & right_mask
        if np.count_nonzero(mask) < 3:
            continue
        shell_mass = float(np.sum(mass[mask]))
        shell_width = max(bins[index + 1] - bins[index], 1e-12)
        tangential = tangential_velocity[mask]
        centers.append(float(np.mean(radii[mask])))
        mean_velocity.append(float(np.average(np.abs(tangential), weights=mass[mask])))
        median_velocity.append(float(np.median(np.abs(tangential))))
        std_velocity.append(float(np.std(tangential)))
        density_profile_values.append(shell_mass / shell_width)
        mean_radial_velocity.append(float(np.average(radial_velocity[mask], weights=mass[mask])))
        counts.append(int(np.count_nonzero(mask)))
    return {
        "radial_centers": np.asarray(centers, dtype=float),
        "mean_tangential_velocity": np.asarray(mean_velocity, dtype=float),
        "median_tangential_velocity": np.asarray(median_velocity, dtype=float),
        "mean_radial_velocity": np.asarray(mean_radial_velocity, dtype=float),
        "tangential_velocity_std": np.asarray(std_velocity, dtype=float),
        "density_profile": np.asarray(density_profile_values, dtype=float),
        "counts": np.asarray(counts, dtype=int),
    }


def spiral_pitch_proxy(positions: np.ndarray, masses: np.ndarray | None = None) -> float:
    pos = np.asarray(positions, dtype=float)
    mass = np.ones(pos.shape[0], dtype=float) if masses is None else np.asarray(masses, dtype=float)
    radii = np.linalg.norm(pos, axis=1)
    mask = radii > np.quantile(radii[radii > 1e-6], 0.35) if np.any(radii > 1e-6) else np.zeros_like(radii, dtype=bool)
    if np.count_nonzero(mask) < 6:
        return float("nan")
    theta = np.unwrap(np.arctan2(pos[mask, 1], pos[mask, 0]))
    log_radius = np.log(radii[mask] + 1e-12)
    weights = mass[mask] / (np.max(mass[mask]) + 1e-12)
    coeffs = np.polyfit(log_radius, theta, deg=1, w=weights)
    slope = coeffs[0]
    return float(np.arctan2(1.0, slope))


def _mode_amplitude(positions: np.ndarray, masses: np.ndarray, mode: int) -> float:
    theta = np.arctan2(positions[:, 1], positions[:, 0])
    weights = np.asarray(masses, dtype=float)
    return float(np.abs(np.sum(weights * np.exp(1j * mode * theta))) / (np.sum(weights) + 1e-12))


def _density_arm_contrast(positions: np.ndarray, masses: np.ndarray, bins_azimuth: int = 24) -> float:
    radii = np.linalg.norm(positions, axis=1)
    mask = (radii > np.quantile(radii, 0.25)) & (radii < np.quantile(radii, 0.8))
    if np.count_nonzero(mask) < 8:
        return float("nan")
    theta = np.mod(np.arctan2(positions[mask, 1], positions[mask, 0]), 2.0 * np.pi)
    hist, _ = np.histogram(theta, bins=bins_azimuth, range=(0.0, 2.0 * np.pi), weights=masses[mask])
    return float((np.max(hist) + 1e-12) / (np.mean(hist) + 1e-12))


def _arm_asymmetry_index(positions: np.ndarray, masses: np.ndarray) -> float:
    theta = np.mod(np.arctan2(positions[:, 1], positions[:, 0]), 2.0 * np.pi)
    left = np.sum(masses[(theta >= 0.0) & (theta < np.pi)])
    right = np.sum(masses[(theta >= np.pi) & (theta < 2.0 * np.pi)])
    return float(abs(left - right) / (left + right + 1e-12))


def _angular_momentum_z(positions: np.ndarray, velocities: np.ndarray, masses: np.ndarray) -> float:
    return float(np.sum(masses * (positions[:, 0] * velocities[:, 1] - positions[:, 1] * velocities[:, 0])))


def compute_spiral_metrics(
    history: np.ndarray,
    velocity_history: np.ndarray | None = None,
    masses: np.ndarray | None = None,
    body_types: np.ndarray | None = None,
    tension_field: np.ndarray | None = None,
) -> dict[str, float]:
    positions = np.asarray(history, dtype=float)
    final = positions[-1]
    initial = positions[0]
    mass = np.ones(final.shape[0], dtype=float) if masses is None else np.asarray(masses, dtype=float)
    vel_hist = np.zeros_like(positions) if velocity_history is None else np.asarray(velocity_history, dtype=float)
    final_vel = vel_hist[-1]
    initial_vel = vel_hist[0]
    radius_initial = np.linalg.norm(initial, axis=1)
    radius_final = np.linalg.norm(final, axis=1)
    m2 = _mode_amplitude(final, mass, 2)
    m3 = _mode_amplitude(final, mass, 3)
    spiral_order = float(max(m2, 0.85 * m3))
    tension = np.zeros((8, 8), dtype=float) if tension_field is None else np.asarray(tension_field, dtype=float)
    energy_proxy = float(0.5 * np.sum(mass[:, None] * final_vel**2))
    total_mass = float(np.sum(mass))
    ang_initial = _angular_momentum_z(initial, initial_vel, mass)
    ang_final = _angular_momentum_z(final, final_vel, mass)
    profile = radial_velocity_profile(final, final_vel, mass, n_bins=12)
    density_contrast = _density_arm_contrast(final, mass)
    metrics = {
        "initial_mean_radius": float(np.average(radius_initial, weights=mass)),
        "final_mean_radius": float(np.average(radius_final, weights=mass)),
        "radial_concentration": float(np.average(radius_initial, weights=mass) - np.average(radius_final, weights=mass)),
        "spiral_order_parameter": spiral_order,
        "mode_2_amplitude": m2,
        "mode_3_amplitude": m3,
        "pitch_angle_proxy": spiral_pitch_proxy(final, mass),
        "density_arm_contrast": density_contrast,
        "angular_momentum_initial": ang_initial,
        "angular_momentum_final": ang_final,
        "angular_momentum_drift": float((ang_final - ang_initial) / (abs(ang_initial) + 1e-12)),
        "total_mass": total_mass,
        "energy_proxy": energy_proxy,
        "elastic_tension_mean": float(np.mean(tension)),
        "elastic_tension_max": float(np.max(tension)),
        "arm_asymmetry_index": _arm_asymmetry_index(final, mass),
        "peak_rotation_velocity": float(np.max(profile["mean_tangential_velocity"])) if len(profile["mean_tangential_velocity"]) else float("nan"),
        "nan_count": int(np.isnan(positions).sum() + np.isnan(vel_hist).sum() + np.isnan(tension).sum()),
    }
    if body_types is not None:
        body_array = np.asarray(body_types, dtype=object)
        metrics["central_mass_count"] = float(np.count_nonzero(body_array == BodyType.CENTRAL_MASS.value))
        metrics["star_system_count"] = float(np.count_nonzero(body_array == BodyType.STAR_SYSTEM.value))
        metrics["gas_cloud_count"] = float(np.count_nonzero(body_array == BodyType.GAS_CLOUD.value))
        metrics["cluster_count"] = float(np.count_nonzero(body_array == BodyType.CLUSTER.value))
    return metrics
