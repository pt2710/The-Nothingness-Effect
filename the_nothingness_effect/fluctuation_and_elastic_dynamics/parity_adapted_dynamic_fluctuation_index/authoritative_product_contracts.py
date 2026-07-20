"""Byte-faithful pDFI C01 product-field contract."""

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
    "parity_adapted_dynamic_fluctuation_index/authoritative_product_contracts.py"
)


def _pair(valid: bool, state: np.ndarray, diagnostics: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    state_vector = np.asarray(state, dtype=float).ravel()
    diagnostic_vector = np.asarray(diagnostics, dtype=float).ravel()
    first = np.concatenate((np.array([float(valid)]), state_vector, diagnostic_vector))
    second = np.concatenate((np.array([float(not valid)]), state_vector, diagnostic_vector))
    return first, second


def _product_input(value: ExactProductInput | _base.ParityDFIInput) -> ExactProductInput:
    if isinstance(value, ExactProductInput):
        return value

    transport = _base.transport_operator(value)
    predictive = _base.predictability_observation_operator(value)
    calibration = _base.elastic_completeness_operator(value)

    transport_residual = float(np.linalg.norm(transport.commutator_residual))
    prediction_residual = float(np.linalg.norm(predictive.tracking_residual))
    calibration_residual = float(abs(calibration.calibration_residual))

    first_1, second_1 = _pair(
        transport_residual <= value.tolerance,
        transport.transport_operator,
        np.array([transport_residual, transport.interaction_energy]),
    )
    first_2, second_2 = _pair(
        prediction_residual <= value.tolerance,
        predictive.coupling_operator,
        np.array([prediction_residual, predictive.interaction_energy]),
    )
    first_3, second_3 = _pair(
        calibration_residual <= value.tolerance,
        calibration.functional,
        np.array([calibration_residual, calibration.interaction_energy]),
    )

    return ExactProductInput(
        first_states={
            SOURCE_IDS[0]: first_1,
            SOURCE_IDS[1]: first_2,
            SOURCE_IDS[2]: first_3,
        },
        second_states={
            SOURCE_IDS[0]: second_1,
            SOURCE_IDS[1]: second_2,
            SOURCE_IDS[2]: second_3,
        },
        first_residuals={source_id: 0.0 for source_id in SOURCE_IDS},
        second_residuals={source_id: 0.0 for source_id in SOURCE_IDS},
        tolerance=value.tolerance,
    )


def product_operator(value: ExactProductInput | _base.ParityDFIInput) -> ExactProductResult:
    return evaluate_exact_product(_product_input(value), source_ids=SOURCE_IDS)


def _residual(value, output):
    return exact_product_residual(
        _product_input(value),
        output,
        name="pDFI C01 product projections and pointwise involution",
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


def _replacement_contract() -> ComplexContract:
    return ComplexContract(
        complex_id=_base.C_ID,
        appendix=_base.APPENDIX,
        appendix_source_sha256=_base.APPENDIX_SHA256,
        level=ComplexLevel.C,
        source_ids=_base.B_IDS,
        domain=DomainSpec(
            "pDFI C01 authoritative spatial product carrier",
            "paired B-level source states with exact coordinate projections and pointwise exchange",
            (ExactProductInput, _base.ParityDFIInput),
        ),
        codomain=CodomainSpec(
            "pDFI C01 spatial product realization",
            "source theorem recovery, localized max residual, and coordinatewise involution",
            (ExactProductResult,),
        ),
        operator=product_operator,
        residual=_residual,
        closure_predicate=exact_product_predicate,
        source_removal_checks=tuple(
            _removal(source_id, index)
            for index, source_id in enumerate(SOURCE_IDS)
        ),
        artifact_spec=ArtifactSpec(
            ("projection_table", "parity_source_table", "exchange_square_record"),
            "python -m the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.simulation.run_contract_suite",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION_PATH,
    )


def contracts() -> tuple[ComplexContract, ...]:
    replacement = _replacement_contract()
    return tuple(
        replacement if contract.complex_id == replacement.complex_id else contract
        for contract in _base.contracts()
    )
