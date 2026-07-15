"""Finite Noether-structure validation helpers for Section 23.

The routines provide deterministic numerical validation metrics for the stated
phase-shift and fp-Gauss identity artifacts. They are numerical support checks,
not formal proof substitutes.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class NoetherParams:
    n_phase: int = 256
    time_steps: int = 120
    alpha: float = 0.37
    grid_size: int = 128
    dx: float = 1.0
    dy: float = 1.0


def fp_phase(theta: np.ndarray, alpha: float) -> np.ndarray:
    return np.asarray(theta, dtype=float) + alpha


def kd_flux(theta: np.ndarray, pi_E: np.ndarray, dx: float) -> float:
    gradient = np.gradient(np.asarray(theta, dtype=float), dx, edge_order=2)
    return float(np.trapezoid(np.asarray(pi_E, dtype=float) * gradient, dx=dx))


def simulate_kd_flux_under_phase_shift(
    params: NoetherParams | None = None,
) -> dict[str, np.ndarray | dict[str, float]]:
    sim_params = params or NoetherParams()
    x = np.linspace(0.0, 1.0, sim_params.n_phase)
    dx = float(x[1] - x[0])
    theta_base = 2.0 * x + 0.1
    pi_E = np.ones_like(theta_base)
    time = np.linspace(0.0, 1.0, sim_params.time_steps)
    flux = np.array(
        [kd_flux(fp_phase(theta_base, sim_params.alpha * np.sin(2 * np.pi * t)), pi_E, dx) for t in time]
    )
    metrics = {
        "rx_initial": float(flux[0]),
        "rx_max_deviation": float(np.max(np.abs(flux - flux[0]))),
        "rx_tolerance": 1e-8,
        "rx_passed": bool(np.max(np.abs(flux - flux[0])) < 1e-8),
    }
    return {"x": x, "time": time, "theta": theta_base, "pi_E": pi_E, "rx": flux, "metrics": metrics}


def gradient_2d(field: np.ndarray, dx: float, dy: float) -> tuple[np.ndarray, np.ndarray]:
    grad_y, grad_x = np.gradient(np.asarray(field, dtype=float), dy, dx, edge_order=2)
    return grad_x, grad_y


def divergence_2d(jx: np.ndarray, jy: np.ndarray, dx: float, dy: float) -> np.ndarray:
    d_jx_dx = np.gradient(np.asarray(jx, dtype=float), dx, axis=1, edge_order=2)
    d_jy_dy = np.gradient(np.asarray(jy, dtype=float), dy, axis=0, edge_order=2)
    return d_jx_dx + d_jy_dy


def fp_gauss_residual(theta: np.ndarray, pi_E: np.ndarray, dx: float, dy: float) -> np.ndarray:
    grad_x, grad_y = gradient_2d(theta, dx, dy)
    return divergence_2d(pi_E * grad_x, pi_E * grad_y, dx, dy)


def simulate_fp_gauss_identity(
    grid_size: int = 128,
    params: NoetherParams | None = None,
) -> dict[str, np.ndarray | dict[str, float]]:
    sim_params = params or NoetherParams(grid_size=grid_size)
    x = np.arange(grid_size, dtype=float) * sim_params.dx
    y = np.arange(grid_size, dtype=float) * sim_params.dy
    xx, yy = np.meshgrid(x, y)
    theta = 0.25 * xx - 0.15 * yy
    pi_E = np.ones_like(theta)
    residual = fp_gauss_residual(theta, pi_E, sim_params.dx, sim_params.dy)
    residual_norm = float(np.max(np.abs(residual)))
    metrics = {
        "grid_size": grid_size,
        "gauss_residual_inf_norm": residual_norm,
        "gauss_tolerance": 1e-6,
        "gauss_passed": bool(residual_norm < 1e-6),
    }
    return {
        "x": x,
        "y": y,
        "theta": theta,
        "pi_E": pi_E,
        "residual": residual,
        "metrics": metrics,
    }


def noether_validation_metrics(
    flux_metrics: dict[str, float],
    gauss_metrics: dict[str, float],
) -> list[dict[str, object]]:
    return [
        {
            "metric": "Rx stability",
            "result": flux_metrics["rx_max_deviation"],
            "tolerance": flux_metrics["rx_tolerance"],
            "passed": bool(flux_metrics["rx_passed"]),
        },
        {
            "metric": "Entropic Gauss law",
            "result": gauss_metrics["gauss_residual_inf_norm"],
            "tolerance": gauss_metrics["gauss_tolerance"],
            "passed": bool(gauss_metrics["gauss_passed"]),
        },
    ]
