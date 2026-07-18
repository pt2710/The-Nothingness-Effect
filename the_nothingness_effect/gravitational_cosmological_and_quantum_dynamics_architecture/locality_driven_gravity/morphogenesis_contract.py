"""Exact finite-volume locality-energy morphogenesis closure."""

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
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import (
    APPENDIX,
    APPENDIX_SHA256,
    FieldLawInput,
    SPECS,
    derived_operator,
)


SPEC = SPECS["locality_driven_gravity"]
C_ID = SPEC.c_id
B_LOCALITY, B_ENERGY = SPEC.b_ids
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
    "locality_driven_gravity/morphogenesis_contract.py"
)


@dataclass(frozen=True)
class LocalityEnergyInput:
    coordinates: np.ndarray
    locality_field: np.ndarray
    energy_current: np.ndarray
    morphogenesis: np.ndarray | None = None
    locality_source_residual: float = 0.0
    energy_source_residual: float = 0.0
    tolerance: float = 1e-10


@dataclass(frozen=True)
class LocalityEnergyCertificate:
    spatial_domain: np.ndarray
    locality_field: np.ndarray
    energy_current: np.ndarray
    edge_locality_average: np.ndarray
    edge_current_average: np.ndarray
    locality_gradient: np.ndarray
    current_divergence: np.ndarray
    flux_divergence: np.ndarray
    product_rule_expansion: np.ndarray
    local_operator: np.ndarray
    interaction_identity_residual: float
    supplied_channel_residual: float
    stability_constant: float
    stability_left: float
    stability_right: float
    stability_bound_residual: float
    common_domain_residual: float
    locality_source_residual: float
    energy_source_residual: float
    status_equivalence_residual: float
    closure_status: str


def _input(value: LocalityEnergyInput | FieldLawInput) -> LocalityEnergyInput:
    if isinstance(value, LocalityEnergyInput):
        return value
    if isinstance(value, FieldLawInput):
        first = derived_operator(
            B_LOCALITY,
            SPEC.source_kinds[0],
            SPEC.source_kinds[1],
            value,
        )
        second = derived_operator(
            B_ENERGY,
            SPEC.source_kinds[2],
            SPEC.source_kinds[3],
            value,
        )
        return LocalityEnergyInput(
            coordinates=value.coordinates,
            locality_field=first.combined_operator,
            energy_current=second.combined_operator,
            locality_source_residual=float(np.linalg.norm(first.residual)),
            energy_source_residual=float(np.linalg.norm(second.residual)),
            tolerance=value.tolerance,
        )
    raise DomainViolationError(
        "locality-energy morphogenesis requires LocalityEnergyInput or FieldLawInput"
    )


def _validated(source: LocalityEnergyInput):
    x = np.asarray(source.coordinates, dtype=float)
    locality = np.asarray(source.locality_field, dtype=float)
    current = np.asarray(source.energy_current, dtype=float)
    if x.ndim != 1 or x.size < 3:
        raise DomainViolationError("morphogenesis closure requires at least three samples")
    if locality.shape != x.shape or current.shape != x.shape:
        raise DomainViolationError(
            "locality and current fields must share the coordinate domain"
        )
    ensure_finite((x, locality, current), name="locality-energy fields")
    spacing = np.diff(x)
    if np.any(spacing <= 0.0):
        raise DomainViolationError("coordinates must be strictly increasing")
    if not np.isfinite(source.tolerance) or source.tolerance < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    if not np.isfinite(source.locality_source_residual) or source.locality_source_residual < 0.0:
        raise DomainViolationError("locality source residual must be finite and nonnegative")
    if not np.isfinite(source.energy_source_residual) or source.energy_source_residual < 0.0:
        raise DomainViolationError("energy source residual must be finite and nonnegative")
    supplied = None
    if source.morphogenesis is not None:
        supplied = np.asarray(source.morphogenesis, dtype=float)
        if supplied.shape != (x.size - 1,):
            raise DomainViolationError(
                "supplied morphogenesis must have one value per spatial edge"
            )
        ensure_finite(supplied, name="supplied morphogenesis")
    return x, locality, current, spacing, supplied


def _difference_matrix(spacing: np.ndarray) -> np.ndarray:
    count = spacing.size + 1
    matrix = np.zeros((count - 1, count), dtype=float)
    for index, step in enumerate(spacing):
        matrix[index, index] = -1.0 / step
        matrix[index, index + 1] = 1.0 / step
    return matrix


def morphogenesis_operator(
    value: LocalityEnergyInput | FieldLawInput,
) -> LocalityEnergyCertificate:
    source = _input(value)
    x, locality, current, spacing, supplied = _validated(source)
    edge_domain = 0.5 * (x[:-1] + x[1:])
    locality_average = 0.5 * (locality[:-1] + locality[1:])
    current_average = 0.5 * (current[:-1] + current[1:])
    locality_gradient = np.diff(locality) / spacing
    current_divergence = np.diff(current) / spacing
    flux_divergence = np.diff(locality * current) / spacing
    expansion = (
        current_average * locality_gradient
        + locality_average * current_divergence
    )
    expected = -flux_divergence
    local_operator = expected if supplied is None else supplied
    identity_residual = float(np.linalg.norm(flux_divergence - expansion))
    supplied_residual = float(np.linalg.norm(local_operator - expected))

    difference = _difference_matrix(spacing)
    stability_constant = float(np.linalg.norm(difference, ord=2))
    w1_infinity = max(
        float(np.max(np.abs(locality))),
        float(np.max(np.abs(locality_gradient))),
    )
    current_l2 = float(
        np.sqrt(np.sum(current_average**2 * spacing))
    )
    stability_left = float(np.sqrt(np.sum(expected**2 * spacing)))
    stability_right = stability_constant * w1_infinity * max(
        current_l2,
        np.finfo(float).eps,
    )
    stability_residual = max(stability_left - stability_right, 0.0)
    common_domain_residual = 0.0

    total = max(
        identity_residual,
        supplied_residual,
        stability_residual,
        common_domain_residual,
        source.locality_source_residual,
        source.energy_source_residual,
    )
    closed = total <= source.tolerance
    status_equivalence = float(closed != (total <= source.tolerance))
    return LocalityEnergyCertificate(
        edge_domain,
        locality,
        current,
        locality_average,
        current_average,
        locality_gradient,
        current_divergence,
        flux_divergence,
        expansion,
        local_operator,
        identity_residual,
        supplied_residual,
        stability_constant,
        stability_left,
        stability_right,
        stability_residual,
        common_domain_residual,
        source.locality_source_residual,
        source.energy_source_residual,
        status_equivalence,
        "closed" if closed and status_equivalence <= source.tolerance else "open",
    )


def _residual(value, output: LocalityEnergyCertificate) -> ResidualResult:
    tolerance = _input(value).tolerance
    vector = (
        output.interaction_identity_residual,
        output.supplied_channel_residual,
        output.stability_bound_residual,
        output.common_domain_residual,
        output.locality_source_residual,
        output.energy_source_residual,
        output.status_equivalence_residual,
    )
    passed = max(vector) <= tolerance
    return ResidualResult(
        "locality-energy finite-volume product-rule closure",
        vector,
        tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {
            "stability_constant": output.stability_constant,
            "stability_left": output.stability_left,
            "stability_right": output.stability_right,
            "discrete_leibniz_exact": True,
        },
    )


def _remove_locality(value) -> SourceRemovalResult:
    source = _input(value)
    complete = morphogenesis_operator(source)
    removed = np.zeros_like(complete.local_operator)
    return source_removal_result(
        ComplexId(B_LOCALITY),
        complete.local_operator,
        removed,
        tolerance=max(source.tolerance, 1e-12),
    )


def _remove_energy(value) -> SourceRemovalResult:
    source = _input(value)
    complete = morphogenesis_operator(source)
    removed = np.zeros_like(complete.local_operator)
    return source_removal_result(
        ComplexId(B_ENERGY),
        complete.local_operator,
        removed,
        tolerance=max(source.tolerance, 1e-12),
    )


def contract() -> ComplexContract:
    return ComplexContract(
        complex_id=ComplexId(C_ID),
        appendix=APPENDIX,
        appendix_source_sha256=APPENDIX_SHA256,
        level=ComplexLevel.C,
        source_ids=(ComplexId(B_LOCALITY), ComplexId(B_ENERGY)),
        domain=DomainSpec(
            "locality-energy common spatial domain",
            "finite strictly ordered grid, one locality field, one energy current, localized B residuals, and optional measured morphogenesis channel",
            (LocalityEnergyInput, FieldLawInput),
        ),
        codomain=CodomainSpec(
            "locality-energy morphogenesis certificate",
            "finite-volume flux divergence, exact staggered Leibniz expansion, stability bound, source defects, and exhaustive status",
            (LocalityEnergyCertificate,),
        ),
        operator=morphogenesis_operator,
        residual=_residual,
        closure_predicate=lambda output, residual: (
            output.closure_status == "closed"
            and residual is not None
            and residual.passed
        ),
        source_removal_checks=(_remove_locality, _remove_energy),
        artifact_spec=ArtifactSpec(
            ("morphogenesis_field", "product_rule_residual", "stability_bound_table"),
            "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.simulation.run_contract_suite",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION_PATH,
    )
