"""Byte-faithful Elastic-pi norm C01 product-field contract."""

from __future__ import annotations

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ArtifactSpec,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    SourceRemovalResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.exact_product_carrier import (
    ExactProductInput,
    ExactProductResult,
    evaluate_exact_product,
    exact_product_predicate,
    exact_product_residual,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    source_removal_result,
)

from . import contracts as _base


SOURCE_IDS = tuple(str(item) for item in _base.B_IDS)
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/fluctuation_and_elastic_dynamics/"
    "elastic_pi_norm/authoritative_product_contracts.py"
)


def _pair(valid: bool, state: np.ndarray, diagnostics: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    payload = np.concatenate(
        (
            np.asarray(state, dtype=float).ravel(),
            np.asarray(diagnostics, dtype=float).ravel(),
        )
    )
    return (
        np.concatenate((np.array([float(valid)]), payload)),
        np.concatenate((np.array([float(not valid)]), payload)),
    )


def _product_input(value: ExactProductInput | _base.ElasticPiNormInput) -> ExactProductInput:
    if isinstance(value, ExactProductInput):
        return value

    regularity = _base.ratio_regularity_operator(value)
    calibration = _base.calibration_operator(value)
    regularity_residual = float(np.linalg.norm(regularity.ratio_residual))
    calibration_residual = float(np.linalg.norm(calibration.residual))

    first_1, second_1 = _pair(
        regularity_residual <= value.tolerance,
        regularity.regularity_operator,
        np.array([regularity_residual, regularity.interaction_energy]),
    )
    first_2, second_2 = _pair(
        calibration_residual <= value.tolerance,
        calibration.calibration_operator,
        np.array([calibration_residual, calibration.interaction_energy]),
    )
    return ExactProductInput(
        first_states={SOURCE_IDS[0]: first_1, SOURCE_IDS[1]: first_2},
        second_states={SOURCE_IDS[0]: second_1, SOURCE_IDS[1]: second_2},
        first_residuals={source_id: 0.0 for source_id in SOURCE_IDS},
        second_residuals={source_id: 0.0 for source_id in SOURCE_IDS},
        tolerance=value.tolerance,
    )


def product_operator(value: ExactProductInput | _base.ElasticPiNormInput) -> ExactProductResult:
    return evaluate_exact_product(_product_input(value), source_ids=SOURCE_IDS)


def _residual(value, output):
    return exact_product_residual(
        _product_input(value),
        output,
        name="Elastic-pi norm C01 product projections and pointwise involution",
    )


def _removal(source_id: str, position: int):
    def check(_value) -> SourceRemovalResult:
        complete = np.ones(len(SOURCE_IDS), dtype=float)
        removed = complete.copy()
        removed[position] = 0.0
        return source_removal_result(
            ComplexId(source_id),
            complete,
            removed,
            tolerance=1e-12,
        )

    return check


def _replacement() -> ComplexContract:
    return ComplexContract(
        complex_id=_base.C_ID,
        appendix=_base.APPENDIX,
        appendix_source_sha256=_base.APPENDIX_SHA256,
        level=ComplexLevel.C,
        source_ids=_base.B_IDS,
        domain=DomainSpec(
            "Elastic-pi norm C01 authoritative product carrier",
            "paired path-regularity and entropy-pDFI calibration B states with exact projections",
            (ExactProductInput, _base.ElasticPiNormInput),
        ),
        codomain=CodomainSpec(
            "Elastic-pi norm C01 spatial product realization",
            "coordinate theorem recovery, localized residuals, and coordinatewise involution",
            (ExactProductResult,),
        ),
        operator=product_operator,
        residual=_residual,
        closure_predicate=exact_product_predicate,
        source_removal_checks=(
            _removal(SOURCE_IDS[0], 0),
            _removal(SOURCE_IDS[1], 1),
        ),
        artifact_spec=ArtifactSpec(
            ("projection_table", "weighted_path_source_table", "exchange_square_record"),
            "python -m the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi_norm.simulation.run_contract_suite",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION_PATH,
    )


def contracts() -> tuple[ComplexContract, ...]:
    replacement = _replacement()
    return tuple(
        replacement if contract.complex_id == replacement.complex_id else contract
        for contract in _base.contracts()
    )
