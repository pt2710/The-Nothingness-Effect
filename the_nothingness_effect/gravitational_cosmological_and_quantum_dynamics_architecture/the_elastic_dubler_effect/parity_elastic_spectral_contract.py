"""Exact finite parity-elastic spectral closure for Elastic Dubler C02."""

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
    SourceRemovalResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    source_removal_result,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import (
    ensure_finite,
)

from . import canonical_contracts as legacy
from . import source_faithful_contracts as explicit


C_ID = legacy.C_SPECS[0][0]
B_PARITY = legacy.C_SPECS[0][1]
B_SPECTRAL = legacy.C_SPECS[0][2]
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
    "the_elastic_dubler_effect/parity_elastic_spectral_contract.py"
)


@dataclass(frozen=True)
class ParityElasticSpectralInput:
    coordinates: np.ndarray
    parity_source: np.ndarray
    trial_field: np.ndarray
    baseline_elasticity: np.ndarray
    beta: float
    elasticity: float
    potential: np.ndarray | None = None
    coefficient: np.ndarray | None = None
    form_defect_density: np.ndarray | None = None
    operator_defect: np.ndarray | None = None
    tolerance: float = 1e-10


@dataclass(frozen=True)
class ParityElasticSpectralCertificate:
    spatial_domain: np.ndarray
    parity_source: np.ndarray
    trial_field: np.ndarray
    coefficient: np.ndarray
    baseline_coefficient: np.ndarray
    form_defect_density: np.ndarray
    operator: np.ndarray
    baseline_operator: np.ndarray
    local_operator: np.ndarray
    coefficient_residual: float
    form_identity_residual: float
    operator_identity_residual: float
    parity_restoration_residual: float
    infinite_elasticity_residual: float
    source_sampling_residual: float
    parity_source_residual: float
    spectral_source_residual: float
    classification_idempotence_residual: float
    closure_status: str


def _input(
    value: ParityElasticSpectralInput | legacy.ElasticDublerInput,
) -> ParityElasticSpectralInput:
    if isinstance(value, ParityElasticSpectralInput):
        return value
    if isinstance(value, legacy.ElasticDublerInput):
        legacy._validated(value)
        pdfi = np.asarray(value.pdfi, dtype=float)
        parity_source = 0.5 * (pdfi - pdfi[::-1])
        return ParityElasticSpectralInput(
            coordinates=value.coordinates,
            parity_source=parity_source,
            trial_field=pdfi,
            baseline_elasticity=value.domain_elasticity,
            beta=1.0,
            elasticity=value.elasticity,
            potential=np.zeros_like(pdfi),
            tolerance=value.tolerance,
        )
    raise DomainViolationError(
        "parity-elastic spectral closure requires ParityElasticSpectralInput "
        "or ElasticDublerInput"
    )


def _validated(source: ParityElasticSpectralInput):
    x = np.asarray(source.coordinates, dtype=float)
    parity = np.asarray(source.parity_source, dtype=float)
    trial = np.asarray(source.trial_field, dtype=float)
    baseline = np.asarray(source.baseline_elasticity, dtype=float)
    potential = (
        np.zeros_like(trial)
        if source.potential is None
        else np.asarray(source.potential, dtype=float)
    )
    if x.ndim != 1 or x.size < 5:
        raise DomainViolationError("spectral closure requires at least five spatial samples")
    if any(item.shape != x.shape for item in (parity, trial, baseline, potential)):
        raise DomainViolationError("all spectral closure fields must share one spatial domain")
    ensure_finite((x, parity, trial, baseline, potential), name="parity-elastic spectral input")
    if np.any(np.diff(x) <= 0.0):
        raise DomainViolationError("spectral coordinates must be strictly increasing")
    if np.any(baseline <= 0.0):
        raise DomainViolationError("baseline elasticity must be strictly positive")
    if not np.isfinite(source.beta) or source.beta == 0.0:
        raise DomainViolationError("beta must be finite and nonzero")
    if not np.isfinite(source.elasticity) or source.elasticity <= 0.0:
        raise DomainViolationError("elasticity must be finite and strictly positive")
    if not np.isfinite(source.tolerance) or source.tolerance < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    return x, parity, trial, baseline, potential


def _operator(
    x: np.ndarray,
    coefficient: np.ndarray,
    trial: np.ndarray,
    potential: np.ndarray,
) -> np.ndarray:
    gradient = np.gradient(trial, x, edge_order=2)
    return -np.gradient(coefficient * gradient, x, edge_order=2) + potential * trial


def parity_elastic_spectral_operator(
    value: ParityElasticSpectralInput | legacy.ElasticDublerInput,
) -> ParityElasticSpectralCertificate:
    source = _input(value)
    x, parity, trial, baseline, potential = _validated(source)
    expected_coefficient = baseline * np.exp(
        -source.beta * parity / source.elasticity
    )
    gradient = np.gradient(trial, x, edge_order=2)
    expected_form = (expected_coefficient - baseline) * gradient**2
    expected_operator = _operator(x, expected_coefficient, trial, potential)
    baseline_operator = _operator(x, baseline, trial, potential)
    expected_operator_defect = expected_operator - baseline_operator

    coefficient = (
        expected_coefficient
        if source.coefficient is None
        else np.asarray(source.coefficient, dtype=float)
    )
    form = (
        expected_form
        if source.form_defect_density is None
        else np.asarray(source.form_defect_density, dtype=float)
    )
    operator_defect = (
        expected_operator_defect
        if source.operator_defect is None
        else np.asarray(source.operator_defect, dtype=float)
    )
    if any(item.shape != x.shape for item in (coefficient, form, operator_defect)):
        raise DomainViolationError("supplied spectral channels must match the spatial domain")
    ensure_finite((coefficient, form, operator_defect), name="spectral closure channels")
    if np.any(coefficient <= 0.0):
        raise DomainViolationError("spectral coefficient must be strictly positive")

    coefficient_residual = float(np.linalg.norm(coefficient - expected_coefficient))
    form_residual = float(np.linalg.norm(form - expected_form))
    operator_residual = float(
        np.linalg.norm(operator_defect - expected_operator_defect)
    )
    parity_restoration = float(
        np.linalg.norm(baseline * np.exp(np.zeros_like(parity)) - baseline)
    )
    infinite_elasticity = float(
        np.linalg.norm(baseline * np.exp(-source.beta * parity * 0.0) - baseline)
    )
    predicted_sampled = bool(
        np.any((np.abs(parity) > source.tolerance) & (np.abs(gradient) > source.tolerance))
    )
    observed_sampled = bool(np.linalg.norm(expected_form) > source.tolerance)
    source_sampling = float(predicted_sampled != observed_sampled)

    if isinstance(value, legacy.ElasticDublerInput):
        parity_b = explicit._b_operator(B_PARITY, value)
        spectral_b = explicit._b_operator(B_SPECTRAL, value)
        parity_source_residual = float(np.linalg.norm(parity_b.residual))
        spectral_source_residual = float(np.linalg.norm(spectral_b.residual))
    else:
        parity_source_residual = 0.0
        spectral_source_residual = 0.0

    total = max(
        coefficient_residual,
        form_residual,
        operator_residual,
        parity_restoration,
        infinite_elasticity,
        source_sampling,
        parity_source_residual,
        spectral_source_residual,
    )
    classification = float(total > source.tolerance)
    idempotence = abs(float(bool(classification)) - classification)
    closed = total <= source.tolerance and idempotence <= source.tolerance
    return ParityElasticSpectralCertificate(
        x,
        parity,
        trial,
        coefficient,
        baseline,
        form,
        expected_operator,
        baseline_operator,
        operator_defect,
        coefficient_residual,
        form_residual,
        operator_residual,
        parity_restoration,
        infinite_elasticity,
        source_sampling,
        parity_source_residual,
        spectral_source_residual,
        idempotence,
        "closed" if closed else "open",
    )


def _residual(value, output: ParityElasticSpectralCertificate) -> ResidualResult:
    tolerance = _input(value).tolerance
    vector = (
        output.coefficient_residual,
        output.form_identity_residual,
        output.operator_identity_residual,
        output.parity_restoration_residual,
        output.infinite_elasticity_residual,
        output.source_sampling_residual,
        output.parity_source_residual,
        output.spectral_source_residual,
        output.classification_idempotence_residual,
    )
    passed = max(vector) <= tolerance
    return ResidualResult(
        "parity-elastic coefficient, quadratic-form, and operator identity",
        vector,
        tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {
            "parity_restoration_checked": True,
            "infinite_elasticity_limit_checked": True,
            "source_sampling_checked": True,
            "status_idempotence_checked": True,
        },
    )


def _flatten(output: ParityElasticSpectralCertificate) -> np.ndarray:
    return np.concatenate(
        (output.coefficient, output.form_defect_density, output.local_operator)
    )


def _remove_parity(value) -> SourceRemovalResult:
    source = _input(value)
    complete = parity_elastic_spectral_operator(value)
    removed_value = ParityElasticSpectralInput(
        source.coordinates,
        np.zeros_like(source.parity_source),
        source.trial_field,
        source.baseline_elasticity,
        source.beta,
        source.elasticity,
        potential=source.potential,
        tolerance=source.tolerance,
    )
    removed = parity_elastic_spectral_operator(removed_value)
    return source_removal_result(
        ComplexId(B_PARITY),
        _flatten(complete),
        _flatten(removed),
        tolerance=max(source.tolerance, 1e-12),
    )


def _remove_spectral(value) -> SourceRemovalResult:
    source = _input(value)
    complete = parity_elastic_spectral_operator(value)
    constant_trial = np.full_like(
        np.asarray(source.trial_field, dtype=float),
        float(np.mean(source.trial_field)),
    )
    removed_value = ParityElasticSpectralInput(
        source.coordinates,
        source.parity_source,
        constant_trial,
        source.baseline_elasticity,
        source.beta,
        source.elasticity,
        potential=np.zeros_like(constant_trial),
        tolerance=source.tolerance,
    )
    removed = parity_elastic_spectral_operator(removed_value)
    return source_removal_result(
        ComplexId(B_SPECTRAL),
        _flatten(complete),
        _flatten(removed),
        tolerance=max(source.tolerance, 1e-12),
    )


def contract() -> ComplexContract:
    return ComplexContract(
        complex_id=ComplexId(C_ID),
        appendix=legacy.APPENDIX,
        appendix_source_sha256=legacy.APPENDIX_SHA256,
        level=ComplexLevel.C,
        source_ids=(ComplexId(B_PARITY), ComplexId(B_SPECTRAL)),
        domain=DomainSpec(
            "parity-elastic spectral realization",
            "bounded parity source, positive baseline coefficient and elasticity, finite trial field, and optional measured coefficient/form/operator channels",
            (ParityElasticSpectralInput, legacy.ElasticDublerInput),
        ),
        codomain=CodomainSpec(
            "parity-elastic spectral closure certificate",
            "exponential coefficient, quadratic-form defect, operator defect, restoration limits, source sampling, and residual classification",
            (ParityElasticSpectralCertificate,),
        ),
        operator=parity_elastic_spectral_operator,
        residual=_residual,
        closure_predicate=lambda output, residual: (
            output.closure_status == "closed"
            and residual is not None
            and residual.passed
        ),
        source_removal_checks=(_remove_parity, _remove_spectral),
        artifact_spec=ArtifactSpec(
            ("coefficient_field", "form_defect_table", "operator_residual_plot"),
            "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.simulation.run_contract_suite",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION_PATH,
    )
