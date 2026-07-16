"""Typed Discrete-Time Quasicrystal contracts and optional neural operator."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from .recertified_contracts import (
    AutocorrelationInput,
    DFITailInput,
    DriftInput,
    ElasticSupportInput,
    FigureClosureInput,
    FloquetRobustnessInput,
    MeyerInput,
    OUScatterInput,
    ReconstructionInput,
    WaveletRidgeInput,
    evaluate_autocorrelation_completeness,
    evaluate_dfi_compatible_tail_control,
    evaluate_drift_boundedness,
    evaluate_elastic_invariance_of_support,
    evaluate_floquet_free_robustness,
    evaluate_meyer_cut_and_project_structure,
    evaluate_ou_noise_5d_scatter,
    evaluate_reconstruction_equivalence,
    evaluate_wavelet_ridge_locking,
    evaluate_z2x2_sign_symmetry,
)
from .figure_provenance import evaluate_figure_backed_closure


_LAZY_EXPORTS = {
    "DTQC_COMPLEX_IDS": (".neural_operator", "DTQC_COMPLEX_IDS"),
    "DTQCInflationLayer": (".neural_operator", "DTQCInflationLayer"),
    "DTQCNeuralState": (".neural_operator", "DTQCNeuralState"),
    "fibonacci_word": (".neural_operator", "fibonacci_word"),
}

__all__ = [
    *[
        name
        for name in globals()
        if name.startswith("evaluate_") or name.endswith("Input")
    ],
    *_LAZY_EXPORTS,
]


def __getattr__(name: str) -> Any:
    try:
        module_name, attribute = _LAZY_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    value = getattr(import_module(module_name, __name__), attribute)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted((*globals(), *__all__))
