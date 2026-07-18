"""Source-faithful pDFI C01 closure with normalized spatial defects."""

from __future__ import annotations

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
from the_nothingness_effect._runtime.theorem_complex_runtime.positive_spatial_functional import (
    involutive_permutation,
    positive_spatial_functional,
    positive_spatial_functional_reference,
)

from . import closure_contracts as _previous
from . import contracts as _base


ExactSpatialParityInput = _previous.ExactSpatialParityInput
ExactSpatialParityClosure = _previous.ExactSpatialParityClosure
SOURCE_IDS = _previous.SOURCE_IDS
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/fluctuation_and_elastic_dynamics/"
    "parity_adapted_dynamic_fluctuation_index/normalized_closure_contracts.py"
)


def spatial_parity_closure_operator(
    value: ExactSpatialParityInput | _base.ParityDFIInput,
) -> ExactSpatialParityClosure:
    source = _previous._exact_input(value)
    for name, scalar in (
        ("gradient_weight", source.gradient_weight),
        ("boundary_weight", source.boundary_weight),
        ("grid_spacing", source.grid_spacing),
    ):
        if not np.isfinite(scalar) or scalar <= 0.0:
            raise _previous.DomainViolationError(f"{name} must be finite and strictly positive")
    if not np.isfinite(source.tolerance) or source.tolerance < 0.0:
        raise _previous.DomainViolationError("tolerance must be finite and non-negative")

    fields_1b = _previous._matrix(source.source_energy_fields_1b, label="pDFI 1B")
    fields_2b = _previous._matrix(source.source_energy_fields_2b, label="pDFI 2B")
    if fields_1b.shape != fields_2b.shape:
        raise _previous.DomainViolationError("pDFI 1B and 2B fields must share one domain")
    weights_1b = _previous._weights(source.source_weights_1b, label="pDFI 1B")
    weights_2b = _previous._weights(source.source_weights_2b, label="pDFI 2B")
    reflection = involutive_permutation(
        source.spatial_reflection,
        fields_1b.shape[1],
        label="pDFI spatial_reflection",
    )
    exchange = involutive_permutation(
        source.source_exchange,
        len(SOURCE_IDS),
        label="pDFI source_exchange",
    )

    transformed_2b = fields_2b[exchange][:, reflection]
    transformed_weights_2b = weights_2b[exchange]
    twice = transformed_2b[exchange][:, reflection]
    involution = float(np.linalg.norm(twice - fields_2b))

    _, potential_1b, volume_1b, gradient_1b, boundary_1b, energy_1b = (
        positive_spatial_functional(
            fields_1b,
            weights_1b,
            spacing=source.grid_spacing,
            gradient_weight=source.gradient_weight,
            boundary_weight=source.boundary_weight,
        )
    )
    _, potential_2b, volume_2b, gradient_2b, boundary_2b, energy_2b = (
        positive_spatial_functional(
            transformed_2b,
            transformed_weights_2b,
            spacing=source.grid_spacing,
            gradient_weight=source.gradient_weight,
            boundary_weight=source.boundary_weight,
        )
    )
    joint = float(energy_1b + energy_2b + involution * involution)
    lower_1b = float(np.min(weights_1b) * source.grid_spacing * np.sum(fields_1b))
    lower_2b = float(
        np.min(transformed_weights_2b)
        * source.grid_spacing
        * np.sum(transformed_2b)
    )
    margin_1b = float(energy_1b - lower_1b)
    margin_2b = float(energy_2b - lower_2b)

    reference_1b = positive_spatial_functional_reference(
        fields_1b,
        weights_1b,
        spacing=source.grid_spacing,
        gradient_weight=source.gradient_weight,
        boundary_weight=source.boundary_weight,
    )
    reference_2b = positive_spatial_functional_reference(
        transformed_2b,
        transformed_weights_2b,
        spacing=source.grid_spacing,
        gradient_weight=source.gradient_weight,
        boundary_weight=source.boundary_weight,
    )
    reference_joint = reference_1b + reference_2b + involution * involution
    residual_1b = abs(energy_1b - reference_1b)
    residual_2b = abs(energy_2b - reference_2b)
    residual_joint = abs(joint - reference_joint)
    closed = max(
        joint,
        residual_1b,
        residual_2b,
        residual_joint,
        max(-margin_1b, 0.0),
        max(-margin_2b, 0.0),
    ) <= source.tolerance

    return ExactSpatialParityClosure(
        fields_1b,
        fields_2b,
        transformed_2b,
        potential_1b,
        potential_2b,
        volume_1b,
        gradient_1b,
        boundary_1b,
        energy_1b,
        volume_2b,
        gradient_2b,
        boundary_2b,
        energy_2b,
        involution,
        joint,
        lower_1b,
        lower_2b,
        margin_1b,
        margin_2b,
        residual_1b,
        residual_2b,
        residual_joint,
        "closed" if closed else "open",
    )


def _residual(
    value: ExactSpatialParityInput | _base.ParityDFIInput,
    output: ExactSpatialParityClosure,
) -> ResidualResult:
    source = _previous._exact_input(value)
    vector = (
        output.reference_residual_1b,
        output.reference_residual_2b,
        output.reference_residual_joint,
        max(-output.coercivity_margin_1b, 0.0),
        max(-output.coercivity_margin_2b, 0.0),
        output.exchange_involution_residual,
    )
    passed = max(vector) <= source.tolerance
    return ResidualResult(
        "pDFI C01 normalized-potential formula and coercivity residual",
        vector,
        source.tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
    )


def _predicate(output: ExactSpatialParityClosure, residual: ResidualResult | None) -> bool:
    return bool(
        residual is not None
        and residual.passed
        and output.closure_status == "closed"
        and output.joint_energy <= residual.tolerance
    )


def _source_removal(source_id: str, source_index: int):
    def check(value: ExactSpatialParityInput | _base.ParityDFIInput) -> SourceRemovalResult:
        _previous._exact_input(value)
        fields = np.zeros((len(SOURCE_IDS), 3), dtype=float)
        fields[source_index, 1] = 1.0
        complete_weights = np.ones(len(SOURCE_IDS), dtype=float)
        removed_weights = complete_weights.copy()
        removed_weights[source_index] = 0.0
        _, _, _, _, _, complete = positive_spatial_functional(
            fields,
            complete_weights,
            spacing=1.0,
            gradient_weight=1.0,
            boundary_weight=1.0,
        )
        _, _, _, _, _, removed = positive_spatial_functional(
            fields,
            removed_weights,
            spacing=1.0,
            gradient_weight=1.0,
            boundary_weight=1.0,
        )
        return source_removal_result(
            ComplexId(source_id),
            np.array([complete]),
            np.array([removed]),
            tolerance=1e-12,
        )

    return check


def _replacement_contract() -> ComplexContract:
    return ComplexContract(
        complex_id=_base.C_ID,
        appendix=_base.APPENDIX,
        appendix_source_sha256=_base.APPENDIX_SHA256,
        level=ComplexLevel.C,
        source_ids=_base.B_IDS,
        domain=DomainSpec(
            "complete spatial pDFI defect fields",
            "nonnegative B energies, normalized defect potential, positive weights, and involutive exchange",
            (ExactSpatialParityInput, _base.ParityDFIInput),
        ),
        codomain=CodomainSpec(
            "coercive spatial parity-elastic closure",
            "raw-energy volume, normalized-defect gradient, boundary leakage, coercivity, exchange, and reference certificate",
            (ExactSpatialParityClosure,),
        ),
        operator=spatial_parity_closure_operator,
        residual=_residual,
        closure_predicate=_predicate,
        source_removal_checks=tuple(
            _source_removal(source_id, index)
            for index, source_id in enumerate(SOURCE_IDS)
        ),
        artifact_spec=ArtifactSpec(
            ("transition_csv", "parity_plot", "coercivity_table"),
            "python -m the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.simulation.run_contract_suite",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION_PATH,
    )


def contracts() -> tuple[ComplexContract, ...]:
    replacement = _replacement_contract()
    return tuple(
        replacement if contract.complex_id == replacement.complex_id else contract
        for contract in _previous.contracts()
    )
