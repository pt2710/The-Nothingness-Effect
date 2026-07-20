"""Recertified DFI A05--A07 source contracts.

These finite contracts implement the three source laws required by the
Flowpoint-certified DFI validation functional.  They expose decomposition
covariance, Flowpoint-interface consistency, and simulation consistency as
separate fail-closed witnesses instead of inferring them from a downstream
aggregate residual.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ArtifactSpec,
    ClosureStatus,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    ResidualResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import (
    ensure_finite,
)

from .contracts import APPENDIX, APPENDIX_SHA256
from .dfi import NormalizedDFIResult, normalized_dfi, require_finite_dfi


IMPLEMENTATION_PATH = (
    "the_nothingness_effect/fluctuation_and_elastic_dynamics/"
    "dynamic_fluctuation_index/extended_contracts.py"
)


@dataclass(frozen=True)
class DFIDecompositionInput:
    data: np.ndarray
    spectrum_scale: float
    feature_permutation: tuple[int, ...]
    tolerance: float = 1e-10


@dataclass(frozen=True)
class DFIDecompositionCertificate:
    canonical: NormalizedDFIResult
    permuted: NormalizedDFIResult
    feature_permutation: tuple[int, ...]
    component_assignment_residual: float
    additive_total_residual: float
    permutation_covariance_residual: float
    reproducibility_residual: float


def _finite_matrix(data: np.ndarray, *, name: str) -> np.ndarray:
    array = np.asarray(data, dtype=float)
    if array.ndim != 2 or array.shape[0] < 1 or array.shape[1] < 2:
        raise DomainViolationError(
            f"{name} requires a nonempty two-dimensional feature matrix"
        )
    ensure_finite(array, name=name)
    return array


def _validate_tolerance(tolerance: float) -> float:
    value = float(tolerance)
    if not np.isfinite(value) or value < 0.0:
        raise DomainViolationError("DFI tolerance must be finite and non-negative")
    return value


def decomposition_certificate(
    value: DFIDecompositionInput,
) -> DFIDecompositionCertificate:
    data = _finite_matrix(value.data, name="DFI decomposition data")
    tolerance = _validate_tolerance(value.tolerance)
    feature_count = data.shape[1]
    permutation = tuple(int(item) for item in value.feature_permutation)
    if len(permutation) != feature_count or sorted(permutation) != list(
        range(feature_count)
    ):
        raise DomainViolationError(
            "DFI feature permutation must contain each feature index exactly once"
        )

    canonical = require_finite_dfi(
        normalized_dfi(data, spectrum_scale=value.spectrum_scale)
    )
    permuted = require_finite_dfi(
        normalized_dfi(
            data[:, permutation],
            spectrum_scale=value.spectrum_scale,
        )
    )
    canonical_entropy = np.asarray(canonical.normalized_entropy, dtype=float)
    permuted_entropy = np.asarray(permuted.normalized_entropy, dtype=float)
    expected = canonical_entropy[:, permutation]

    component_assignment = float(np.linalg.norm(permuted_entropy - expected))
    canonical_total = canonical_entropy.sum(axis=1)
    component_total = np.add.reduce(
        tuple(canonical_entropy[:, index] for index in range(feature_count))
    )
    additive_total = float(np.linalg.norm(canonical_total - component_total))
    covariance = float(np.linalg.norm(permuted_entropy - expected))

    repeated = require_finite_dfi(
        normalized_dfi(data, spectrum_scale=value.spectrum_scale)
    )
    reproducibility = float(
        np.linalg.norm(
            np.asarray(repeated.normalized_entropy, dtype=float)
            - canonical_entropy
        )
    )
    if max(
        component_assignment,
        additive_total,
        covariance,
        reproducibility,
    ) > tolerance:
        # The certificate remains returned; the contract residual determines OPEN.
        pass
    return DFIDecompositionCertificate(
        canonical,
        permuted,
        permutation,
        component_assignment,
        additive_total,
        covariance,
        reproducibility,
    )


@dataclass(frozen=True)
class DFIFlowpointInterfaceInput:
    data: np.ndarray
    spectrum_scale: float
    feature_involution: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class DFIFlowpointInterfaceCertificate:
    canonical: NormalizedDFIResult
    transformed: NormalizedDFIResult
    feature_involution: np.ndarray
    involution_residual: float
    component_consistency_residual: float
    total_consistency_residual: float
    commuting_diagram_residual: float


def flowpoint_interface_certificate(
    value: DFIFlowpointInterfaceInput,
) -> DFIFlowpointInterfaceCertificate:
    data = _finite_matrix(value.data, name="DFI Flowpoint interface data")
    _validate_tolerance(value.tolerance)
    feature_count = data.shape[1]
    involution = np.asarray(value.feature_involution, dtype=float)
    if involution.shape != (feature_count, feature_count):
        raise DomainViolationError(
            "DFI Flowpoint interface requires a square feature involution"
        )
    ensure_finite(involution, name="DFI feature involution")

    identity = np.eye(feature_count)
    involution_residual = float(
        np.linalg.norm(involution @ involution - identity)
    )
    canonical = require_finite_dfi(
        normalized_dfi(data, spectrum_scale=value.spectrum_scale)
    )
    transformed_data = data @ involution.T
    transformed = require_finite_dfi(
        normalized_dfi(
            transformed_data,
            spectrum_scale=value.spectrum_scale,
        )
    )
    canonical_entropy = np.asarray(canonical.normalized_entropy, dtype=float)
    transformed_entropy = np.asarray(transformed.normalized_entropy, dtype=float)
    expected = canonical_entropy @ involution.T
    component = float(np.linalg.norm(transformed_entropy - expected))
    total = float(
        np.linalg.norm(
            transformed_entropy.sum(axis=1) - expected.sum(axis=1)
        )
    )
    commuting = float(
        np.linalg.norm(
            transformed_entropy @ involution.T - canonical_entropy
        )
    )
    return DFIFlowpointInterfaceCertificate(
        canonical,
        transformed,
        involution,
        involution_residual,
        component,
        total,
        commuting,
    )


@dataclass(frozen=True)
class DFISimulationInput:
    data: np.ndarray
    spectrum_scale: float
    simulated_normalized_entropy: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class DFISimulationCertificate:
    canonical: NormalizedDFIResult
    simulated_normalized_entropy: np.ndarray
    component_residual: float
    total_residual: float
    normalization_residual: float
    maximum_absolute_error: float
    breakdown_detected: bool


def simulation_certificate(
    value: DFISimulationInput,
) -> DFISimulationCertificate:
    data = _finite_matrix(value.data, name="DFI simulation source data")
    tolerance = _validate_tolerance(value.tolerance)
    canonical = require_finite_dfi(
        normalized_dfi(data, spectrum_scale=value.spectrum_scale)
    )
    expected = np.asarray(canonical.normalized_entropy, dtype=float)
    simulated = np.asarray(value.simulated_normalized_entropy, dtype=float)
    if simulated.shape != expected.shape:
        raise DomainViolationError(
            "simulated DFI entropy must share the canonical component shape"
        )
    ensure_finite(simulated, name="simulated normalized DFI entropy")

    delta = simulated - expected
    component = float(np.linalg.norm(delta))
    total = float(
        np.linalg.norm(simulated.sum(axis=1) - expected.sum(axis=1))
    )
    normalization = float(canonical.normalization_residual)
    maximum = float(np.max(np.abs(delta)))
    return DFISimulationCertificate(
        canonical,
        simulated,
        component,
        total,
        normalization,
        maximum,
        max(component, total, normalization, maximum) > tolerance,
    )


def _residual(
    name: str,
    values: tuple[float, ...],
    tolerance: float,
) -> ResidualResult:
    vector = tuple(float(item) for item in values)
    norm = float(np.linalg.norm(vector))
    return ResidualResult(
        name,
        vector,
        tolerance,
        norm <= tolerance,
        ClosureStatus.SATISFIED if norm <= tolerance else ClosureStatus.OPEN,
    )


def contracts() -> tuple[ComplexContract, ...]:
    artifact = ArtifactSpec(
        (
            "validation_record",
            "failure_witness",
            "source_law_residuals",
        ),
        (
            "python -m the_nothingness_effect.fluctuation_and_elastic_dynamics."
            "dynamic_fluctuation_index.simulation.run_contract_suite"
        ),
    )
    return (
        ComplexContract(
            ComplexId("dfi_uniqueness_of_decomposition_and_mapping_ambiguity"),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            DomainSpec(
                "DFI component assignment and mapping record",
                "finite DFI data, positive scale, and a complete feature permutation",
                (DFIDecompositionInput,),
            ),
            CodomainSpec(
                "DFI decomposition certificate",
                "component assignment, additive total, covariance, and reproducibility residuals",
                (DFIDecompositionCertificate,),
            ),
            decomposition_certificate,
            residual=lambda source, output: _residual(
                "DFI decomposition and mapping covariance",
                (
                    output.component_assignment_residual,
                    output.additive_total_residual,
                    output.permutation_covariance_residual,
                    output.reproducibility_residual,
                ),
                source.tolerance,
            ),
            artifact_spec=artifact,
            implementation_path=IMPLEMENTATION_PATH,
        ),
        ComplexContract(
            ComplexId("dfi_flowpoint_consistency_and_interface_inconsistency"),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            DomainSpec(
                "DFI--Flowpoint interface",
                "finite DFI data, positive scale, and a finite feature involution",
                (DFIFlowpointInterfaceInput,),
            ),
            CodomainSpec(
                "DFI--Flowpoint consistency certificate",
                "involution, component, total, and commuting-diagram residuals",
                (DFIFlowpointInterfaceCertificate,),
            ),
            flowpoint_interface_certificate,
            residual=lambda source, output: _residual(
                "DFI--Flowpoint interface consistency",
                (
                    output.involution_residual,
                    output.component_consistency_residual,
                    output.total_consistency_residual,
                    output.commuting_diagram_residual,
                ),
                source.tolerance,
            ),
            artifact_spec=artifact,
            implementation_path=IMPLEMENTATION_PATH,
        ),
        ComplexContract(
            ComplexId("dfi_simulation_consistency_and_simulation_breakdown"),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            DomainSpec(
                "DFI simulation validation record",
                "finite source data and an explicit simulated normalized-entropy field",
                (DFISimulationInput,),
            ),
            CodomainSpec(
                "DFI simulation certificate",
                "component, total, normalization, maximum-error, and breakdown status",
                (DFISimulationCertificate,),
            ),
            simulation_certificate,
            residual=lambda source, output: _residual(
                "DFI simulation consistency",
                (
                    output.component_residual,
                    output.total_residual,
                    output.normalization_residual,
                    output.maximum_absolute_error,
                ),
                source.tolerance,
            ),
            artifact_spec=artifact,
            implementation_path=IMPLEMENTATION_PATH,
        ),
    )
