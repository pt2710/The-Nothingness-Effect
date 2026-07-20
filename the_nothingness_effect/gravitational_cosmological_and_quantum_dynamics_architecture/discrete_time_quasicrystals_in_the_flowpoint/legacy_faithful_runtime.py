"""Source-faithful DTQC visualization runtime reconstructed from LEGACY_models.

The visual path follows ``flowpoint_elastic_pi/simulate_elastic_pi_quasi_crystals.py``:

    ten-wave decagonal carrier -> log-magnitude centered FFT -> sixty radial
    profiles -> legacy DFI transform -> legacy Elastic-pi visual profile ->
    Flowpoint flicker, intrinsically oscillating 5-D cloud, and breathing
    spherical embeddings.

The legacy visual Elastic-pi convention uses ``exp(+S/K_D)``.  The canonical
Dubler convention, ``exp(-Delta S/K_D)``, is retained separately in
``canonical_elastic_pi`` so visual fidelity never silently rewrites the
canonical source law.

The outputs are finite deterministic visualizations.  They are not a formal
proof, a thermodynamic-limit existence result, or empirical validation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.ndimage import map_coordinates
from scipy.signal import fftconvolve

from .spatial_elastic_pi import backproject_directional_profiles, require_true_2d


CLAIM_BOUNDARY = (
    "finite deterministic source-faithful DTQC visualization evidence; "
    "not a formal proof, thermodynamic-limit existence result, or empirical validation"
)
LEGACY_VISUAL_SOURCE = "tne_concepts/flowpoint_elastic_pi/simulate_elastic_pi_quasi_crystals.py"
CANONICAL_DUBLER_SOURCE = "equations/elastic_dubler_effect/elastic_dubler_effect.py"


@dataclass(frozen=True)
class LegacyFaithfulConfig:
    grid_size: int = 240
    extent: float = 5.0
    wave_count: int = 10
    radial_channels: int = 60
    time_steps: int = 48
    legacy_frame_stride: int = 4
    entropy_scale: float = math.pi
    point_count: int = 8000
    sphere_resolution: int = 64
    seed: int = 1

    def validate(self) -> None:
        if not isinstance(self.grid_size, int) or self.grid_size < 48:
            raise ValueError("grid_size must be an integer >= 48")
        if self.grid_size % 2:
            raise ValueError("grid_size must be even for centered FFT geometry")
        if not math.isfinite(self.extent) or self.extent <= 0.0:
            raise ValueError("extent must be finite and positive")
        if self.wave_count != 10:
            raise ValueError("the legacy carrier requires ten decagonal directions")
        if self.radial_channels != 60:
            raise ValueError("the legacy diffraction/DFI path requires sixty radial axes")
        if not isinstance(self.time_steps, int) or self.time_steps < 8:
            raise ValueError("time_steps must be an integer >= 8")
        if not isinstance(self.legacy_frame_stride, int) or self.legacy_frame_stride < 1:
            raise ValueError("legacy_frame_stride must be a positive integer")
        if not math.isfinite(self.entropy_scale) or self.entropy_scale <= 0.0:
            raise ValueError("entropy_scale K_D must be finite and strictly positive")
        if not isinstance(self.point_count, int) or self.point_count < 400:
            raise ValueError("point_count must be an integer >= 400")
        if not isinstance(self.sphere_resolution, int) or self.sphere_resolution < 48:
            raise ValueError("sphere_resolution must be an integer >= 48")


@dataclass(frozen=True)
class LegacyFaithfulState:
    x: np.ndarray
    y: np.ndarray
    carrier: np.ndarray
    carrier_diffraction: np.ndarray
    radial_profiles: np.ndarray
    dfi_volume_profiles: np.ndarray
    entropy_profiles: np.ndarray
    dfi_surface: np.ndarray
    entropy: np.ndarray
    elastic_pi: np.ndarray
    canonical_elastic_pi: np.ndarray
    static_pattern: np.ndarray
    diffraction: np.ndarray
    wavelet_ridges: np.ndarray
    legacy_frame_index: np.ndarray
    flowpoint_sector: np.ndarray
    flowpoint_frames: np.ndarray
    scatter_reference_4d: np.ndarray
    scatter_trajectory_4d: np.ndarray
    projection_3d: np.ndarray
    sphere_texture: np.ndarray
    source_removal: dict[str, float]
    config: LegacyFaithfulConfig
    claim_boundary: str = CLAIM_BOUNDARY


def _safe_ptp(value: np.ndarray) -> float:
    span = float(np.ptp(np.asarray(value, dtype=np.float64)))
    if not math.isfinite(span) or span <= np.finfo(np.float64).eps:
        raise ValueError("expected a non-degenerate finite field")
    return span


def _decagonal_carrier(config: LegacyFaithfulConfig) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    axis = np.linspace(-config.extent, config.extent, config.grid_size, dtype=np.float64)
    x, y = np.meshgrid(axis, axis, indexing="xy")
    indices = np.arange(config.wave_count, dtype=np.float64)
    angles = 2.0 * math.pi * indices / config.wave_count
    carrier = np.sum(
        np.cos(
            2.0
            * math.pi
            * (
                np.cos(angles)[:, None, None] * x[None, :, :]
                + np.sin(angles)[:, None, None] * y[None, :, :]
            )
        ),
        axis=0,
    )
    carrier /= _safe_ptp(carrier)
    return x, y, carrier


def _log_fft(field: np.ndarray) -> np.ndarray:
    return np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(field))))


def _radial_profiles(diffraction: np.ndarray, channels: int) -> np.ndarray:
    size = diffraction.shape[0]
    center = np.array([size // 2, size // 2], dtype=np.float64)
    radius = np.linspace(-size / 2.0, size / 2.0, size, dtype=np.float64)
    angles = np.linspace(0.0, 2.0 * math.pi, channels, endpoint=False)
    profiles = []
    for angle in angles:
        coordinates = np.vstack(
            (
                center[0] + radius * math.cos(float(angle)),
                center[1] + radius * math.sin(float(angle)),
            )
        )
        profiles.append(map_coordinates(diffraction, coordinates, order=1, mode="reflect"))
    return np.asarray(profiles, dtype=np.float64)


def _legacy_dfi(profiles: np.ndarray, soi: float = 100.0) -> tuple[np.ndarray, np.ndarray]:
    channel_count = profiles.shape[0]
    base_volume = soi / channel_count
    total = profiles.sum(axis=0)
    denominator = (total[None, :] - profiles) * channel_count + 1e-14
    sigma = (total[None, :] * (channel_count - 1)) / denominator
    volume = base_volume * sigma
    entropy = volume - base_volume
    return volume, entropy


def _legacy_and_canonical_elastic_pi(
    entropy_profiles: np.ndarray,
    entropy_scale: float,
    grid_size: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    entropy = backproject_directional_profiles(entropy_profiles, grid_size=grid_size)
    legacy = math.pi * np.exp(np.clip(entropy / entropy_scale, -100.0, math.log(100.0)))
    canonical = math.pi * np.exp(np.clip(-entropy / entropy_scale, -100.0, math.log(100.0)))
    require_true_2d(entropy, label="legacy DTQC entropy backprojection")
    require_true_2d(legacy, label="legacy visual Elastic-pi field")
    require_true_2d(canonical, label="canonical Dubler Elastic-pi field")
    return entropy, legacy, canonical


def _morlet_ridges(field: np.ndarray, scale_count: int = 96) -> np.ndarray:
    row = _log_fft(field)[field.shape[0] // 2]
    responses: list[np.ndarray] = []
    for scale in np.linspace(1.0, min(192.0, field.shape[0] / 2.0), scale_count):
        half_width = max(8, int(math.ceil(5.0 * scale)))
        t = np.arange(-half_width, half_width + 1, dtype=np.float64)
        wavelet = np.exp(1j * 5.0 * t / scale) * np.exp(-0.5 * (t / scale) ** 2)
        wavelet /= math.sqrt(scale)
        responses.append(np.abs(fftconvolve(row, np.conjugate(wavelet[::-1]), mode="same")))
    return np.asarray(responses, dtype=np.float64)


def _flowpoint_flicker(
    x: np.ndarray,
    y: np.ndarray,
    config: LegacyFaithfulConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    indices = np.arange(config.time_steps, dtype=np.int64) * config.legacy_frame_stride
    sectors = np.where(np.arange(config.time_steps) % 2 == 0, 1.0, -1.0)
    k10 = np.arange(config.wave_count, dtype=np.float64)
    cosines = np.cos(2.0 * math.pi * k10 / config.wave_count)
    sines = np.sin(2.0 * math.pi * k10 / config.wave_count)
    frames: list[np.ndarray] = []
    for frame_number, sector in zip(indices, sectors, strict=True):
        shift = float(frame_number) / 90.0
        pattern = np.sum(
            np.cos(
                2.0
                * math.pi
                * (
                    (cosines + shift)[:, None, None] * x[None, :, :]
                    + (sines + shift)[:, None, None] * y[None, :, :]
                )
            ),
            axis=0,
        ) / config.wave_count
        frames.append(sector * pattern)
    return indices, sectors, np.asarray(frames, dtype=np.float32)


def _rotation(axis: np.ndarray, angle: float) -> np.ndarray:
    axis = axis / np.linalg.norm(axis)
    ux, uy, uz = axis
    cosine, sine = math.cos(angle), math.sin(angle)
    return np.array(
        [
            [cosine + ux * ux * (1.0 - cosine), ux * uy * (1.0 - cosine) - uz * sine, ux * uz * (1.0 - cosine) + uy * sine],
            [uy * ux * (1.0 - cosine) + uz * sine, cosine + uy * uy * (1.0 - cosine), uy * uz * (1.0 - cosine) - ux * sine],
            [uz * ux * (1.0 - cosine) - uy * sine, uz * uy * (1.0 - cosine) + ux * sine, cosine + uz * uz * (1.0 - cosine)],
        ],
        dtype=np.float64,
    )


def _scatter_trajectory(config: LegacyFaithfulConfig) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # RandomState deliberately reproduces the legacy np.random.seed / randint / randn sequence.
    rng = np.random.RandomState(config.seed)
    points_5d = rng.randint(-4, 5, (config.point_count, 5))
    projection_45 = rng.randn(4, 5)
    reference_4d = points_5d @ projection_45.T

    camera = rng.randn(3)
    camera /= np.linalg.norm(camera)
    rotation = np.eye(3)
    trajectory_4d: list[np.ndarray] = []
    projected_3d: list[np.ndarray] = []
    capture = set((np.arange(config.time_steps) * config.legacy_frame_stride).tolist())
    final_legacy_frame = int(max(capture))
    for legacy_frame in range(final_legacy_frame + 1):
        camera += -0.03 * camera + 0.05 * rng.randn(3)
        camera /= np.linalg.norm(camera)
        rotation = _rotation(camera, 0.015) @ rotation
        if legacy_frame not in capture:
            continue
        phase = 2.0 * math.pi * legacy_frame / 96.0
        scale = 1.0 + 0.35 * np.sin(phase + np.arange(4) * math.pi / 2.0)
        oscillated = reference_4d * scale
        trajectory_4d.append(oscillated.astype(np.float32))
        projected_3d.append((oscillated[:, :3] @ rotation.T).astype(np.float32))
    return (
        reference_4d.astype(np.float32),
        np.asarray(trajectory_4d, dtype=np.float32),
        np.asarray(projected_3d, dtype=np.float32),
    )


def _sphere_texture(pattern: np.ndarray, resolution: int) -> np.ndarray:
    theta = np.linspace(0.0, math.pi, resolution)
    phi = np.linspace(0.0, 2.0 * math.pi, resolution)
    theta_grid, phi_grid = np.meshgrid(theta, phi, indexing="xy")
    rows = (theta_grid / math.pi) * (pattern.shape[0] - 1)
    columns = (phi_grid / (2.0 * math.pi)) * (pattern.shape[1] - 1)
    coordinates = np.vstack((rows.ravel(), columns.ravel()))
    return map_coordinates(pattern, coordinates, order=1, mode="wrap").reshape(resolution, resolution)


def generate_legacy_faithful_state(
    config: LegacyFaithfulConfig | None = None,
) -> LegacyFaithfulState:
    cfg = config or LegacyFaithfulConfig()
    cfg.validate()

    x, y, carrier = _decagonal_carrier(cfg)
    carrier_diffraction = _log_fft(carrier)
    profiles = _radial_profiles(carrier_diffraction, cfg.radial_channels)
    volume_profiles, entropy_profiles = _legacy_dfi(profiles)
    entropy, elastic_pi, canonical_elastic_pi = _legacy_and_canonical_elastic_pi(
        entropy_profiles, cfg.entropy_scale, cfg.grid_size
    )
    static_pattern = carrier * elastic_pi
    diffraction = _log_fft(static_pattern)
    first_volume = volume_profiles[0]
    first_entropy = entropy_profiles[0]
    dfi_surface = np.outer(first_volume, first_entropy)
    wavelet_ridges = _morlet_ridges(static_pattern)
    frame_index, sectors, flicker_frames = _flowpoint_flicker(x, y, cfg)
    scatter_reference, scatter_trajectory, projection_3d = _scatter_trajectory(cfg)
    sphere_texture = _sphere_texture(static_pattern, cfg.sphere_resolution)

    positive_sector = np.abs(flicker_frames)
    static_signed = sectors[:, None, None] * flicker_frames[0][None, :, :]
    source_removal = {
        "dfi": float(np.linalg.norm(elastic_pi - math.pi)),
        "elastic_pi": float(np.linalg.norm(static_pattern - carrier)),
        "flowpoint": float(np.linalg.norm(flicker_frames - positive_sector)),
        "temporal_evolution": float(np.linalg.norm(flicker_frames - static_signed)),
        "scatter_oscillation": float(np.linalg.norm(scatter_trajectory[1:] - scatter_trajectory[:-1])),
    }

    arrays = (
        x,
        y,
        carrier,
        carrier_diffraction,
        profiles,
        volume_profiles,
        entropy_profiles,
        dfi_surface,
        entropy,
        elastic_pi,
        canonical_elastic_pi,
        static_pattern,
        diffraction,
        wavelet_ridges,
        frame_index,
        sectors,
        flicker_frames,
        scatter_reference,
        scatter_trajectory,
        projection_3d,
        sphere_texture,
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
        carrier_diffraction=carrier_diffraction,
        radial_profiles=profiles,
        dfi_volume_profiles=volume_profiles,
        entropy_profiles=entropy_profiles,
        dfi_surface=dfi_surface,
        entropy=entropy,
        elastic_pi=elastic_pi,
        canonical_elastic_pi=canonical_elastic_pi,
        static_pattern=static_pattern,
        diffraction=diffraction,
        wavelet_ridges=wavelet_ridges,
        legacy_frame_index=frame_index,
        flowpoint_sector=sectors,
        flowpoint_frames=flicker_frames,
        scatter_reference_4d=scatter_reference,
        scatter_trajectory_4d=scatter_trajectory,
        projection_3d=projection_3d,
        sphere_texture=sphere_texture,
        source_removal=source_removal,
        config=cfg,
    )
