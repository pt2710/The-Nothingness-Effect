"""Finite black-hole dynamics proxies for Section 18 artifacts.

The model builds radial Elastic-pi, entropic-horizon, Hawking-like radiation,
observer-horizon, and memory traces. It is a toy numerical support model, not a
full GR/QFT solver.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.elastic_pi import ElasticPi


@dataclass(frozen=True)
class BlackHoleParams:
    grid_size: int = 256
    steps: int = 120
    r_min: float = 0.2
    r_max: float = 12.0
    mass_proxy: float = 4.0
    entropy_scale: float = 2.0
    width: float = 1.5
    K_D: float = 2.0
    threshold: float = 0.36
    memory_decay: float = 0.92


def entropy_profile_radial(
    r: np.ndarray,
    mass_proxy: float,
    entropy_scale: float,
    width: float,
) -> np.ndarray:
    radius = np.asarray(r, dtype=float)
    core = entropy_scale * mass_proxy / (radius + width)
    shoulder = 0.35 * entropy_scale * np.exp(-((radius - mass_proxy) ** 2) / (2.0 * width**2))
    return core + shoulder


def elastic_pi_profile(entropy: np.ndarray, K_D: float) -> np.ndarray:
    if K_D <= 0:
        raise ValueError("K_D must be positive.")
    _, pi_e, _ = ElasticPi(K_D).compute_piE_and_laplacian(np.asarray(entropy, dtype=float), K_D=K_D)
    return pi_e / np.pi


def detect_threshold_crossing(
    r: np.ndarray,
    field: np.ndarray,
    threshold: float,
) -> float:
    radius = np.asarray(r, dtype=float)
    values = np.asarray(field, dtype=float)
    crossing = np.where((values[:-1] < threshold) & (threshold <= values[1:]))[0]
    if crossing.size == 0:
        return float("nan")
    idx = int(crossing[0])
    left_r = float(radius[idx])
    right_r = float(radius[idx + 1])
    left_v = float(values[idx])
    right_v = float(values[idx + 1])
    if right_v == left_v:
        return left_r
    weight = (threshold - left_v) / (right_v - left_v)
    return left_r + weight * (right_r - left_r)


def horizon_indicator(r: np.ndarray, pi_E: np.ndarray, threshold: float) -> float:
    return detect_threshold_crossing(r, pi_E, threshold)


def surface_gradient(r: np.ndarray, field: np.ndarray) -> np.ndarray:
    return np.gradient(np.asarray(field, dtype=float), np.asarray(r, dtype=float), edge_order=2)


def hawking_like_temperature(surface_grad: np.ndarray, K_D: float) -> np.ndarray:
    if K_D <= 0:
        raise ValueError("K_D must be positive.")
    return np.abs(np.asarray(surface_grad, dtype=float)) / K_D


def hawking_like_flux(temperature: np.ndarray) -> np.ndarray:
    temp = np.maximum(np.asarray(temperature, dtype=float), 0.0)
    return temp**4


def interpolate_profile_value(r: np.ndarray, profile: np.ndarray, radius: float) -> float:
    coordinates = np.asarray(r, dtype=float)
    values = np.asarray(profile, dtype=float)
    if not np.isfinite(radius):
        return float("nan")
    return float(np.interp(radius, coordinates, values, left=values[0], right=values[-1]))


def black_hole_snapshot(
    mass_proxy: float,
    params: BlackHoleParams | None = None,
) -> dict[str, np.ndarray | float]:
    sim_params = params or BlackHoleParams()
    r = np.linspace(sim_params.r_min, sim_params.r_max, sim_params.grid_size)
    entropy = entropy_profile_radial(
        r,
        mass_proxy=mass_proxy,
        entropy_scale=sim_params.entropy_scale,
        width=sim_params.width,
    )
    pi_E = elastic_pi_profile(entropy, sim_params.K_D)
    gradient = surface_gradient(r, pi_E)
    temperature_profile = hawking_like_temperature(gradient, sim_params.K_D)
    flux_profile = hawking_like_flux(temperature_profile)
    horizon_radius = horizon_indicator(r, pi_E, sim_params.threshold)
    threshold_contour_radius = detect_threshold_crossing(r, pi_E, sim_params.threshold * 0.85)
    return {
        "r": r,
        "entropy": entropy,
        "pi_E": pi_E,
        "surface_gradient": gradient,
        "temperature_profile": temperature_profile,
        "flux_profile": flux_profile,
        "horizon_radius": horizon_radius,
        "threshold_contour_radius": threshold_contour_radius,
        "temperature_at_horizon": interpolate_profile_value(r, temperature_profile, horizon_radius),
        "flux_at_horizon": interpolate_profile_value(r, flux_profile, horizon_radius),
        "integrated_flux_proxy": float(np.trapezoid(flux_profile, r)),
        "central_depression_proxy": float(np.min(pi_E)),
        "ring_contrast_proxy": float(np.max(pi_E) - np.min(pi_E)),
    }


def observer_horizon_trace(
    r_grid: np.ndarray,
    pi_E_time: np.ndarray,
    observer_path: np.ndarray,
    threshold: float = 0.36,
) -> np.ndarray:
    horizons = np.array([horizon_indicator(r_grid, profile, threshold) for profile in pi_E_time])
    return np.abs(np.asarray(observer_path, dtype=float) - horizons)


def gravitational_memory_kernel(signal: np.ndarray, decay: float) -> np.ndarray:
    if not 0.0 < decay < 1.0:
        raise ValueError("decay must be between 0 and 1.")
    memory = np.zeros_like(np.asarray(signal, dtype=float))
    for index, value in enumerate(signal):
        previous = 0.0 if index == 0 else memory[index - 1]
        memory[index] = decay * previous + (1.0 - decay) * value
    return memory


def simulate_black_hole_dynamics(
    params: BlackHoleParams | None = None,
) -> dict[str, np.ndarray | dict[str, float]]:
    sim_params = params or BlackHoleParams()
    r = np.linspace(sim_params.r_min, sim_params.r_max, sim_params.grid_size)
    time = np.linspace(0.0, 1.0, sim_params.steps)
    mass_history = sim_params.mass_proxy * (1.0 - 0.08 * time)
    entropy_time = []
    pi_time = []
    horizon_radius = []
    temperature_proxy = []
    flux_proxy = []

    for mass_t in mass_history:
        snapshot = black_hole_snapshot(float(mass_t), sim_params)
        entropy_time.append(snapshot["entropy"])
        pi_time.append(snapshot["pi_E"])
        horizon_radius.append(snapshot["horizon_radius"])
        temperature_proxy.append(snapshot["temperature_at_horizon"])
        flux_proxy.append(snapshot["integrated_flux_proxy"])

    entropy_arr = np.asarray(entropy_time)
    pi_arr = np.asarray(pi_time)
    horizon_arr = np.asarray(horizon_radius)
    temperature_arr = np.asarray(temperature_proxy)
    flux_arr = np.asarray(flux_proxy)
    observer_path = np.linspace(sim_params.r_max * 0.85, sim_params.r_max * 0.62, sim_params.steps)
    observer_distance = observer_horizon_trace(r, pi_arr, observer_path, sim_params.threshold)
    memory = gravitational_memory_kernel(flux_arr, sim_params.memory_decay)
    metrics = {
        "grid_size": sim_params.grid_size,
        "steps": sim_params.steps,
        "stable": bool(np.all(np.isfinite(pi_arr)) and np.all(np.isfinite(memory))),
        "max_temperature_proxy": float(np.max(temperature_arr)),
        "max_flux_proxy": float(np.max(flux_arr)),
        "final_memory": float(memory[-1]),
        "horizon_radius_initial": float(horizon_arr[0]),
        "horizon_radius_final": float(horizon_arr[-1]),
    }
    return {
        "r": r,
        "time": time,
        "mass_history": mass_history,
        "entropy_time": entropy_arr,
        "pi_E_time": pi_arr,
        "horizon_radius": horizon_arr,
        "temperature_proxy": temperature_arr,
        "flux_proxy": flux_arr,
        "observer_path": observer_path,
        "observer_distance": observer_distance,
        "memory": memory,
        "metrics": metrics,
    }
