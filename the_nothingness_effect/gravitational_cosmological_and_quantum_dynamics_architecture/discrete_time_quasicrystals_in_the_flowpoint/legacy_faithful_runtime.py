"""Deterministic legacy-faithful DTQC visualization runtime.

This module is deliberately separate from the trainable Fibonacci/Pisot DTQC
operator.  It reconstructs the visual chain used by the legacy TNE models:

    decagonal carrier -> centered 2-D diffraction -> radial multi-axis DFI
    -> canonical Elastic-pi -> Flowpoint alternation -> 2-D/3-D/5-D views.

The output is finite computational evidence.  It is not a thermodynamic-limit
existence proof, proof-assistant certificate, or empirical material validation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates


CLAIM_BOUNDARY = (
    "finite deterministic legacy-faithful DTQC visualization evidence; "
    "not a formal proof, thermodynamic-limit existence result, or empirical validation"
)


@dataclass(frozen=True)
class LegacyFaithfulConfig:
    grid_size: int = 72
    extent: float = 4.0 * math.pi
    wave_number: float = 2.4
    wave_count: int = 10
    radial_channels: int = 5
    time_steps: int = 10
    entropy_scale: float = 1.75
    point_count: int = 1200
    seed: int = 0

    def validate(self) -> None:
        if not isinstance(self.grid_size, int) or self.grid_size < 32:
            raise ValueError("grid_size must be an integer >= 32")
        if self.grid_size % 2:
            raise ValueError("grid_size must be even for centered FFT geometry")
        if not math.isfinite(self.extent) or self.extent <= 0.0:
            raise ValueError("extent must be finite and positive")
        if not math.isfinite(self.wave_number) or self.wave_number <= 0.0:
            raise ValueError("wave_number must be finite and positive")
        if self.wave_count != 10:
            raise ValueError("legacy-faithful carrier requires ten decagonal directions")
        if not isinstance(self.radial_channels, int) or self.radial_channels < 3:
            raise ValueError("radial_channels must be an integer >= 3")
        if not isinstance(self.time_steps, int) or self.time_steps < 4:
            raise ValueError("time_steps must be an integer >= 4")
        if not math.isfinite(self.entropy_scale) or self.entropy_scale <= 0.0:
            raise ValueError("entropy_scale K_D must be finite and strictly positive")
        if not isinstance(self.point_count, int) or self.point_count < 200:
            raise ValueError("point_count must be an integer >= 200")


@dataclass(frozen=True)
class LegacyFaithfulState:
    x: np.ndarray
    y: np.ndarray
    carrier: np.ndarray
    diffraction: np.ndarray
    dfi_channels: np.ndarray
    dfi: np.ndarray
    entropy: np.ndarray
    elastic_pi: np.ndarray
    flowpoint_sector: np.ndarray
    flowpoint_frames: np.ndarray
    projection_5d: np.ndarray
    projection_3d: np.ndarray
    sphere_points: np.ndarray
    half_sphere_points: np.ndarray
    wavelet_ridges: np.ndarray
    source_removal: dict[str, float]
    config: LegacyFaithfulConfig
    claim_boundary: str = CLAIM_BOUNDARY


def _normalize(value: np.ndarray) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    minimum = float(np.min(array))
    maximum = float(np.max(array))
    span = maximum - minimum
    if not math.isfinite(span) or span <= np.finfo(np.float64).eps:
        return np.zeros_like(array)
    return (array - minimum) / span


def _decagonal_carrier(config: LegacyFaithfulConfig) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    axis = np.linspace(-config.extent / 2.0, config.extent / 2.0, config.grid_size)
    x, y = np.meshgrid(axis, axis, indexing="xy")
    field = np.zeros_like(x)
    for index in range(config.wave_count):
        angle = 2.0 * math.pi * index / config.wave_count
        phase = math.pi * (index % 2) / config.wave_count
        field += np.cos(
            config.wave_number * (math.cos(angle) * x + math.sin(angle) * y) + phase
        )
    field /= float(config.wave_count)
    envelope = np.exp(-0.0125 * (x * x + y * y))
    carrier = _normalize(field * (0.78 + 0.22 * envelope))
    return x, y, carrier


def _centered_diffraction(carrier: np.ndarray) -> np.ndarray:
    centered = carrier - float(np.mean(carrier))
    spectrum = np.fft.fftshift(np.fft.fft2(centered, norm="ortho"))
    return _normalize(np.abs(spectrum) ** 2)


def _radial_multi_axis_dfi(
    x: np.ndarray,
    y: np.ndarray,
    carrier: np.ndarray,
    channels: int,
) -> tuple[np.ndarray, np.ndarray]:
    dx = float(x[0, 1] - x[0, 0])
    dy = float(y[1, 0] - y[0, 0])
    grad_y, grad_x = np.gradient(carrier, dy, dx)
    radius = np.sqrt(x * x + y * y)
    safe_radius = np.where(radius > np.finfo(float).eps, radius, 1.0)
    radial = (x * grad_x + y * grad_y) / safe_radius
    tangential = (-y * grad_x + x * grad_y) / safe_radius
    angular = np.arctan2(y, x)
    outputs: list[np.ndarray] = []
    for index in range(channels):
        theta = math.pi * index / channels
        directional = math.cos(theta) * grad_x + math.sin(theta) * grad_y
        angular_lock = np.cos(channels * angular - 2.0 * theta)
        channel = np.abs(directional) + 0.45 * np.abs(radial) + 0.25 * np.abs(tangential * angular_lock)
        outputs.append(_normalize(channel))
    stack = np.stack(outputs, axis=0)
    weights = np.linspace(1.0, 1.6, channels, dtype=np.float64)
    combined = np.tensordot(weights / weights.sum(), stack, axes=(0, 0))
    return stack, _normalize(combined)


def _entropy_field(carrier: np.ndarray, diffraction: np.ndarray, dfi: np.ndarray) -> np.ndarray:
    eps = np.finfo(np.float64).eps
    probability = np.clip(carrier, eps, 1.0 - eps)
    binary_entropy = -(probability * np.log(probability) + (1.0 - probability) * np.log(1.0 - probability))
    spectral_term = np.log1p(4.0 * diffraction)
    fluctuation_term = np.log1p(3.0 * dfi)
    return _normalize(binary_entropy + 0.55 * spectral_term + 0.75 * fluctuation_term)


def _elastic_pi(entropy: np.ndarray, entropy_scale: float) -> np.ndarray:
    return math.pi * np.exp(-entropy / entropy_scale)


def _flowpoint_frames(elastic_pi: np.ndarray, carrier: np.ndarray, time_steps: int) -> tuple[np.ndarray, np.ndarray]:
    sectors = np.where(np.arange(time_steps) % 2 == 0, 1.0, -1.0)
    centered = carrier - float(np.mean(carrier))
    base = elastic_pi * centered
    frames = sectors[:, None, None] * base[None, :, :]
    return sectors, frames


def _sample_indices(carrier: np.ndarray, point_count: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    flat = carrier.ravel()
    weights = flat - flat.min() + 1e-9
    weights = weights / weights.sum()
    count = min(point_count, flat.size)
    return np.sort(rng.choice(flat.size, size=count, replace=False, p=weights))


def _five_dimensional_projection(
    x: np.ndarray,
    y: np.ndarray,
    carrier: np.ndarray,
    diffraction: np.ndarray,
    dfi: np.ndarray,
    elastic_pi: np.ndarray,
    point_count: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    indices = _sample_indices(carrier, point_count, seed)
    features = np.column_stack(
        (
            _normalize(x).ravel()[indices],
            _normalize(y).ravel()[indices],
            carrier.ravel()[indices],
            diffraction.ravel()[indices],
            _normalize(dfi * elastic_pi).ravel()[indices],
        )
    )
    centered = features - features.mean(axis=0, keepdims=True)
    scale = np.std(centered, axis=0, keepdims=True)
    normalized = centered / np.where(scale > 1e-12, scale, 1.0)
    rng = np.random.default_rng(seed + 101)
    basis, _ = np.linalg.qr(rng.normal(size=(5, 5)))
    projected = normalized @ basis[:, :3]
    return normalized, projected


def _sphere_embeddings(
    elastic_pi: np.ndarray,
    carrier: np.ndarray,
    point_count: int,
) -> tuple[np.ndarray, np.ndarray]:
    side = int(math.ceil(math.sqrt(point_count)))
    theta = np.linspace(0.0, 2.0 * math.pi, side, endpoint=False)
    phi = np.linspace(0.0, math.pi, side)
    theta_grid, phi_grid = np.meshgrid(theta, phi, indexing="xy")
    row = phi_grid / math.pi * (elastic_pi.shape[0] - 1)
    col = theta_grid / (2.0 * math.pi) * (elastic_pi.shape[1] - 1)
    sampled_pi = map_coordinates(elastic_pi, (row, col), order=1, mode="wrap")
    sampled_carrier = map_coordinates(carrier, (row, col), order=1, mode="wrap")
    radius = 0.88 + 0.22 * _normalize(sampled_pi) + 0.08 * (sampled_carrier - 0.5)
    sphere = np.column_stack(
        (
            (radius * np.sin(phi_grid) * np.cos(theta_grid)).ravel(),
            (radius * np.sin(phi_grid) * np.sin(theta_grid)).ravel(),
            (radius * np.cos(phi_grid)).ravel(),
        )
    )
    cut = (theta_grid <= math.pi).ravel()
    return sphere, sphere[cut]


def _multiscale_ridges(carrier: np.ndarray) -> np.ndarray:
    scales = (0.8, 1.4, 2.2, 3.4, 5.0)
    responses: list[np.ndarray] = []
    for sigma in scales:
        fine = gaussian_filter(carrier, sigma=sigma)
        coarse = gaussian_filter(carrier, sigma=sigma * 1.65)
        responses.append(np.abs(fine - coarse))
    stack = np.stack(responses, axis=0)
    ridge_strength = stack.max(axis=0)
    ridge_scale = np.argmax(stack, axis=0) / max(1, len(scales) - 1)
    return np.stack((_normalize(ridge_strength), ridge_scale), axis=0)


def generate_legacy_faithful_state(
    config: LegacyFaithfulConfig | None = None,
) -> LegacyFaithfulState:
    cfg = config or LegacyFaithfulConfig()
    cfg.validate()
    x, y, carrier = _decagonal_carrier(cfg)
    diffraction = _centered_diffraction(carrier)
    dfi_channels, dfi = _radial_multi_axis_dfi(x, y, carrier, cfg.radial_channels)
    entropy = _entropy_field(carrier, diffraction, dfi)
    elastic_pi = _elastic_pi(entropy, cfg.entropy_scale)
    sectors, frames = _flowpoint_frames(elastic_pi, carrier, cfg.time_steps)
    projection_5d, projection_3d = _five_dimensional_projection(
        x,
        y,
        carrier,
        diffraction,
        dfi,
        elastic_pi,
        cfg.point_count,
        cfg.seed,
    )
    sphere, half_sphere = _sphere_embeddings(elastic_pi, carrier, cfg.point_count)
    ridges = _multiscale_ridges(carrier)

    no_dfi_entropy = _entropy_field(carrier, diffraction, np.zeros_like(dfi))
    no_dfi_elastic_pi = _elastic_pi(no_dfi_entropy, cfg.entropy_scale)
    no_flowpoint_frames = np.broadcast_to(frames[0], frames.shape)
    no_elastic_frames = sectors[:, None, None] * (carrier - carrier.mean())[None, :, :]
    source_removal = {
        "dfi": float(np.linalg.norm(elastic_pi - no_dfi_elastic_pi)),
        "elastic_pi": float(np.linalg.norm(frames - no_elastic_frames)),
        "flowpoint": float(np.linalg.norm(frames - no_flowpoint_frames)),
    }

    arrays = (
        x,
        y,
        carrier,
        diffraction,
        dfi_channels,
        dfi,
        entropy,
        elastic_pi,
        sectors,
        frames,
        projection_5d,
        projection_3d,
        sphere,
        half_sphere,
        ridges,
    )
    if not all(np.isfinite(value).all() for value in arrays):
        raise FloatingPointError("legacy-faithful DTQC state contains NaN or infinity")
    if float(np.std(carrier)) <= 1e-6 or float(np.std(diffraction)) <= 1e-6:
        raise RuntimeError("legacy-faithful DTQC carrier or diffraction is degenerate")
    if any(value <= 0.0 for value in source_removal.values()):
        raise RuntimeError("legacy-faithful DTQC source-removal witness is degenerate")

    return LegacyFaithfulState(
        x=x,
        y=y,
        carrier=carrier,
        diffraction=diffraction,
        dfi_channels=dfi_channels,
        dfi=dfi,
        entropy=entropy,
        elastic_pi=elastic_pi,
        flowpoint_sector=sectors,
        flowpoint_frames=frames,
        projection_5d=projection_5d,
        projection_3d=projection_3d,
        sphere_points=sphere,
        half_sphere_points=half_sphere,
        wavelet_ridges=ridges,
        source_removal=source_removal,
        config=cfg,
    )
