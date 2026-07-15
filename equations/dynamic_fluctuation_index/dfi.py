"""Typed, fail-closed Dynamic Fluctuation Index implementation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np

from equations.spectrum_of_infinities.spectrum_of_infinities import SpectrumOfInfinities
from tne_runtime.theorem_complex_runtime.types import DomainViolationError, SingularEvaluationError
from tne_runtime.theorem_complex_runtime.validation import ensure_finite


class DFIStatus(str, Enum):
    FINITE = "finite"
    SINGULAR = "singular"
    DIVERGENT = "divergent"


class DFISingularityError(SingularEvaluationError):
    """Raised when the canonical DFI denominator vanishes."""


@dataclass(frozen=True)
class DivergenceWitness:
    status: DFIStatus
    coordinates: tuple[tuple[int, int], ...]
    minimum_absolute_denominator: float
    detail: str


@dataclass(frozen=True)
class NormalizedDFIResult:
    feature_names: tuple[Any, ...]
    normalized_entropy: np.ndarray | None
    entropic_weight: np.ndarray | None
    relative_volume: np.ndarray | None
    base_volume: float
    spectrum_scale: float
    normalization_residual: float
    status: DFIStatus
    divergence_witness: DivergenceWitness
    approximation_metadata: dict[str, Any]

    @property
    def finite(self) -> bool:
        return self.status is DFIStatus.FINITE


def _matrix(data: Any) -> tuple[np.ndarray, tuple[Any, ...]]:
    if hasattr(data, "columns"):
        array = np.asarray(data.values, dtype=float)
        names = tuple(data.columns)
    else:
        array = np.asarray(data, dtype=float)
        if array.ndim != 2:
            raise DomainViolationError("DFI data must be a two-dimensional array")
        names = tuple(range(array.shape[1]))
    if array.ndim != 2 or array.shape[0] == 0 or array.shape[1] < 2:
        raise DomainViolationError("DFI requires at least one sample and two features")
    ensure_finite(array, name="DFI data")
    return array, names


def unnormalized_divergence_witness(data: Any) -> DivergenceWitness:
    array, _ = _matrix(data)
    feature_count = array.shape[1]
    total = array.sum(axis=1, keepdims=True)
    remainder = total - array
    denominator = remainder * feature_count
    coordinates = tuple(tuple(int(item) for item in coordinate) for coordinate in np.argwhere(denominator == 0))
    minimum = float(np.min(np.abs(denominator)))
    return DivergenceWitness(
        DFIStatus.SINGULAR if coordinates else DFIStatus.FINITE,
        coordinates,
        minimum,
        "zero remainder denominator" if coordinates else "finite denominator on declared sample",
    )


def normalized_dfi(data: Any, *, spectrum_scale: float) -> NormalizedDFIResult:
    array, names = _matrix(data)
    if not np.isfinite(spectrum_scale) or spectrum_scale <= 0:
        raise DomainViolationError("spectrum_scale must be finite and strictly positive")
    witness = unnormalized_divergence_witness(array)
    feature_count = array.shape[1]
    base_volume = float(spectrum_scale / feature_count)
    if witness.status is DFIStatus.SINGULAR:
        return NormalizedDFIResult(
            names,
            None,
            None,
            None,
            base_volume,
            float(spectrum_scale),
            0.0,
            DFIStatus.SINGULAR,
            witness,
            {"masked_nonfinite_values": 0, "canonical_values_available": False},
        )
    total = array.sum(axis=1, keepdims=True)
    remainder = total - array
    weight = (total * (feature_count - 1)) / (remainder * feature_count)
    relative_volume = base_volume * weight
    normalized_entropy = (relative_volume - base_volume) / spectrum_scale
    ensure_finite((weight, relative_volume, normalized_entropy), name="canonical DFI result")
    reconstructed = spectrum_scale * normalized_entropy + base_volume
    normalization_residual = float(np.linalg.norm(reconstructed - relative_volume))
    return NormalizedDFIResult(
        names,
        normalized_entropy,
        weight,
        relative_volume,
        base_volume,
        float(spectrum_scale),
        normalization_residual,
        DFIStatus.FINITE,
        witness,
        {"masked_nonfinite_values": 0, "canonical_values_available": True},
    )


def require_finite_dfi(result: NormalizedDFIResult) -> NormalizedDFIResult:
    if not result.finite:
        raise DFISingularityError(
            f"DFI is {result.status.value}: {result.divergence_witness.detail}; "
            f"coordinates={result.divergence_witness.coordinates[:8]}"
        )
    return result


def dfi_rescaling_residual(data: Any, first_scale: float, second_scale: float) -> float:
    first = require_finite_dfi(normalized_dfi(data, spectrum_scale=first_scale))
    second = require_finite_dfi(normalized_dfi(data, spectrum_scale=second_scale))
    return float(np.linalg.norm(first.normalized_entropy - second.normalized_entropy))


def spatial_localization_residual(result: NormalizedDFIResult) -> tuple[float, float]:
    finite = require_finite_dfi(result)
    entropy = np.asarray(finite.normalized_entropy)
    if entropy.shape[0] < 2:
        return 0.0, 0.0
    local_exchange = float(np.linalg.norm(np.diff(entropy, axis=0)))
    boundary_trace = float(np.linalg.norm(entropy[0]) + np.linalg.norm(entropy[-1]))
    return local_exchange, boundary_trace


class DynamicFluctuationIndex:
    """Compatibility facade over the canonical normalized DFI result."""

    def __init__(self, soi_params=None, *, compatibility_mode: bool = False):
        self.soi_params = soi_params.copy() if soi_params else {}
        self.compatibility_mode = bool(compatibility_mode)

    def _soi_value(self, soi=None, **soi_kwargs) -> float:
        if isinstance(soi, SpectrumOfInfinities):
            for key, value in soi_kwargs.items():
                setattr(soi, key, value)
            return float(soi.soi())
        if soi is None:
            params = dict(self.soi_params)
            params.update(soi_kwargs)
            return float(SpectrumOfInfinities(**params).soi())
        return float(soi)

    def compute(self, data, soi=None, **soi_kwargs) -> NormalizedDFIResult:
        return normalized_dfi(data, spectrum_scale=self._soi_value(soi, **soi_kwargs))

    def dfi(self, data, soi=None, **soi_kwargs):
        result = self.compute(data, soi=soi, **soi_kwargs)
        if not result.finite:
            if not self.compatibility_mode:
                return result
            # Explicit legacy mode only: expose old neutral coercion and record it.
            array, names = _matrix(data)
            feature_count = array.shape[1]
            total = array.sum(axis=1, keepdims=True)
            remainder = total - array
            with np.errstate(divide="ignore", invalid="ignore"):
                weight = (total * (feature_count - 1)) / (remainder * feature_count)
            weight = np.where(np.isfinite(weight), weight, 1.0)
            volume = result.base_volume * weight
            entropy = volume - result.base_volume
            return {
                name: {
                    "Relative_Entropy": entropy[:, index],
                    "Entropic_Weight": weight[:, index],
                    "Relative_Volume": volume[:, index],
                    "Compatibility_Mode": True,
                }
                for index, name in enumerate(names)
            }
        entropy = result.spectrum_scale * result.normalized_entropy
        return {
            name: {
                "Relative_Entropy": entropy[:, index],
                "Entropic_Weight": result.entropic_weight[:, index],
                "Relative_Volume": result.relative_volume[:, index],
                "Normalization_Residual": result.normalization_residual,
                "Status": result.status.value,
            }
            for index, name in enumerate(result.feature_names)
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compute Dynamic Fluctuation Index on a dataset")
    parser.add_argument("--soi", type=float, default=None)
    parser.add_argument("--normalize_to", type=float, default=100)
    parser.add_argument("--adv_mode", action="store_true")
    parser.add_argument("--type", choices=["symmetric", "dualistic"])
    parser.parse_args()
