"""Typed Discrete-Time Quasicrystal contracts and neural operator."""

from .neural_operator import DTQC_COMPLEX_IDS, DTQCInflationLayer, DTQCNeuralState, fibonacci_word
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
    evaluate_figure_backed_closure,
    evaluate_floquet_free_robustness,
    evaluate_meyer_cut_and_project_structure,
    evaluate_ou_noise_5d_scatter,
    evaluate_reconstruction_equivalence,
    evaluate_wavelet_ridge_locking,
    evaluate_z2x2_sign_symmetry,
)

__all__ = [name for name in globals() if name.startswith("evaluate_") or name.endswith("Input") or name in {"DTQC_COMPLEX_IDS", "DTQCInflationLayer", "DTQCNeuralState", "fibonacci_word"}]
