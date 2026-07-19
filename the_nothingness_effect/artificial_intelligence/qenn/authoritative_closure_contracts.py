"""Byte-faithful QENN A/B/C closure contracts.

The A complexes contain a positive theorem branch and an explicit failure-dual
branch.  Their finite runtime obligation is a total, exclusive classification
of the concrete source-law defect.  The appendix defines B01--B06 and C01--C03
as direct products with coordinate projections, conjunction bookkeeping, and
coordinatewise involution; those structural laws are implemented exactly here.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import partial

import numpy as np
import torch

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

from . import contracts as base
from . import source_contracts as extended


APPENDIX = base.APPENDIX
APPENDIX_SHA256 = base.APPENDIX_SHA256
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/artificial_intelligence/qenn/"
    "authoritative_closure_contracts.py"
)
A_IDS = tuple(str(item) for item in (*base.A_IDS, *extended.SOURCE_IDS))
B_IDS = (
    str(base.B_IDS[0]),
    str(base.B_IDS[1]),
    "parity_resolved_autocorrelation_operator",
    "support_transport_drift_certificate",
    "epoch_support_commutator_closure",
    "entropic_hyperparameter_stability_margin",
)
C_IDS = (
    str(base.C_IDS[0]),
    "parity_support_memory_field_closure",
    "optimizer_stability_wedge_spatial_closure",
)
B_SOURCE_PAIRS = tuple(
    (A_IDS[2 * index], A_IDS[2 * index + 1]) for index in range(6)
)
C_SOURCE_PAIRS = (
    (B_IDS[0], B_IDS[1]),
    (B_IDS[2], B_IDS[3]),
    (B_IDS[4], B_IDS[5]),
)


@dataclass(frozen=True)
class QENNDualBranchCertificate:
    law_name: str
    response: torch.Tensor
    defect_field: torch.Tensor
    defect_norm: float
    positive_branch: bool
    failure_dual_branch: bool
    branch_name: str
    failure_condition: str
    exhaustiveness_residual: float
    exclusivity_residual: float
    threshold_classification_residual: float


def _source_law(index: int, value: base.QENNContractInput) -> base.QENNSourceLaw:
    if index < len(base.A_IDS):
        return base.source_operator(index, value)
    return extended.source_operator(index - len(base.A_IDS), value)


def source_operator(index: int, value: base.QENNContractInput) -> QENNDualBranchCertificate:
    law = _source_law(index, value)
    positive = law.invariant_residual <= value.tolerance
    failure = not positive
    exhaustiveness = abs(float(positive) + float(failure) - 1.0)
    exclusivity = float(positive and failure)
    threshold = float(positive != (law.invariant_residual <= value.tolerance))
    return QENNDualBranchCertificate(
        law_name=law.law_name,
        response=law.response,
        defect_field=law.residual_field,
        defect_norm=law.invariant_residual,
        positive_branch=positive,
        failure_dual_branch=failure,
        branch_name="positive" if positive else "failure_dual",
        failure_condition=law.failure_condition,
        exhaustiveness_residual=exhaustiveness,
        exclusivity_residual=exclusivity,
        threshold_classification_residual=threshold,
    )


def _source_residual(value: base.QENNContractInput, output: QENNDualBranchCertificate) -> ResidualResult:
    vector = (
        output.exhaustiveness_residual,
        output.exclusivity_residual,
        output.threshold_classification_residual,
    )
    passed = max(vector) <= value.tolerance
    return ResidualResult(
        f"{output.law_name} positive/failure-dual partition",
        vector,
        value.tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {
            "branch": output.branch_name,
            "defect_norm": output.defect_norm,
            "failure_condition": output.failure_condition,
        },
    )


def _array(tensor: torch.Tensor) -> np.ndarray:
    return tensor.detach().cpu().numpy().astype(float, copy=True).ravel()


def _branch_states(certificate: QENNDualBranchCertificate) -> tuple[np.ndarray, np.ndarray]:
    diagnostic = np.asarray((certificate.defect_norm,), dtype=float)
    positive = np.concatenate(
        (
            np.asarray((float(certificate.positive_branch),), dtype=float),
            diagnostic,
            _array(certificate.response),
        )
    )
    failure = np.concatenate(
        (
            np.asarray((float(certificate.failure_dual_branch),), dtype=float),
            diagnostic,
            _array(certificate.defect_field),
        )
    )
    return positive, failure


def _b_input(index: int, value: base.QENNContractInput | ExactProductInput) -> ExactProductInput:
    if isinstance(value, ExactProductInput):
        return value
    source_ids = B_SOURCE_PAIRS[index]
    certificates = tuple(source_operator(A_IDS.index(source_id), value) for source_id in source_ids)
    states = tuple(_branch_states(item) for item in certificates)
    residuals = tuple(
        max(
            item.exhaustiveness_residual,
            item.exclusivity_residual,
            item.threshold_classification_residual,
        )
        for item in certificates
    )
    return ExactProductInput(
        first_states={source_id: states[pos][0] for pos, source_id in enumerate(source_ids)},
        second_states={source_id: states[pos][1] for pos, source_id in enumerate(source_ids)},
        first_residuals={source_id: residuals[pos] for pos, source_id in enumerate(source_ids)},
        second_residuals={source_id: residuals[pos] for pos, source_id in enumerate(source_ids)},
        tolerance=value.tolerance,
    )


def b_operator(index: int, value: base.QENNContractInput | ExactProductInput) -> ExactProductResult:
    return evaluate_exact_product(_b_input(index, value), source_ids=B_SOURCE_PAIRS[index])


def _b_residual(index: int, value, output):
    return exact_product_residual(
        _b_input(index, value),
        output,
        name=f"QENN {B_IDS[index]} product projections and branch exchange",
    )


def _flatten_product(product: tuple[np.ndarray, ...]) -> np.ndarray:
    return np.concatenate(tuple(np.asarray(item, dtype=float).ravel() for item in product))


def _c_input(index: int, value: base.QENNContractInput | ExactProductInput) -> ExactProductInput:
    if isinstance(value, ExactProductInput):
        return value
    source_ids = C_SOURCE_PAIRS[index]
    b_indices = tuple(B_IDS.index(source_id) for source_id in source_ids)
    outputs = tuple(b_operator(b_index, value) for b_index in b_indices)
    return ExactProductInput(
        first_states={source_id: _flatten_product(outputs[pos].first_product) for pos, source_id in enumerate(source_ids)},
        second_states={source_id: _flatten_product(outputs[pos].second_product) for pos, source_id in enumerate(source_ids)},
        first_residuals={source_id: outputs[pos].first_product_residual for pos, source_id in enumerate(source_ids)},
        second_residuals={source_id: outputs[pos].second_product_residual for pos, source_id in enumerate(source_ids)},
        tolerance=value.tolerance,
    )


def c_operator(index: int, value: base.QENNContractInput | ExactProductInput) -> ExactProductResult:
    return evaluate_exact_product(_c_input(index, value), source_ids=C_SOURCE_PAIRS[index])


def _c_residual(index: int, value, output):
    return exact_product_residual(
        _c_input(index, value),
        output,
        name=f"QENN {C_IDS[index]} product-field projections and pointwise involution",
    )


def _removal(source_id: str, position: int, count: int):
    def check(_value) -> SourceRemovalResult:
        complete = np.ones(count, dtype=float)
        removed = complete.copy(); removed[position] = 0.0
        return source_removal_result(
            ComplexId(source_id), complete, removed, tolerance=1e-12
        )
    return check


def contracts() -> tuple[ComplexContract, ...]:
    domain_a = DomainSpec(
        "finite QENN theorem/failure-dual realization",
        "rank-two finite signal, nonnegative tolerance, and positive interaction/spatial weights",
        (base.QENNContractInput,),
    )
    artifact = ArtifactSpec(
        ("branch_classification_table", "projection_table", "source_removal_table"),
        "python -m the_nothingness_effect.artificial_intelligence.qenn.simulation.run_contract_suite",
    )
    result: list[ComplexContract] = []
    for index, identifier in enumerate(A_IDS):
        result.append(
            ComplexContract(
                ComplexId(identifier), APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (),
                domain_a,
                CodomainSpec(
                    f"{identifier} complete dual classification",
                    "concrete source response, defect field, positive/failure-dual partition, and threshold certificate",
                    (QENNDualBranchCertificate,),
                ),
                partial(source_operator, index),
                residual=_source_residual,
                exact_semantics=True,
                implementation_path=IMPLEMENTATION_PATH,
            )
        )
    for index, identifier in enumerate(B_IDS):
        sources = tuple(ComplexId(item) for item in B_SOURCE_PAIRS[index])
        result.append(
            ComplexContract(
                ComplexId(identifier), APPENDIX, APPENDIX_SHA256, ComplexLevel.B, sources,
                DomainSpec(
                    f"QENN {identifier} authoritative product carrier",
                    "paired complete source-branch states with exact coordinate projections",
                    (base.QENNContractInput, ExactProductInput),
                ),
                CodomainSpec(
                    f"QENN {identifier} product certificate",
                    "coordinate recovery, localized source residuals, and coordinatewise involution",
                    (ExactProductResult,),
                ),
                partial(b_operator, index),
                residual=partial(_b_residual, index),
                source_removal_checks=tuple(
                    _removal(source_id, pos, len(sources))
                    for pos, source_id in enumerate(B_SOURCE_PAIRS[index])
                ),
                artifact_spec=artifact,
                exact_semantics=True,
                implementation_path=IMPLEMENTATION_PATH,
            )
        )
    for index, identifier in enumerate(C_IDS):
        sources = tuple(ComplexId(item) for item in C_SOURCE_PAIRS[index])
        result.append(
            ComplexContract(
                ComplexId(identifier), APPENDIX, APPENDIX_SHA256, ComplexLevel.C, sources,
                DomainSpec(
                    f"QENN {identifier} authoritative product field",
                    "paired complete B-level product states on one joint domain",
                    (base.QENNContractInput, ExactProductInput),
                ),
                CodomainSpec(
                    f"QENN {identifier} exact product-field certificate",
                    "coordinate theorem recovery, residual equivalence, and pointwise product involution",
                    (ExactProductResult,),
                ),
                partial(c_operator, index),
                residual=partial(_c_residual, index),
                closure_predicate=exact_product_predicate,
                source_removal_checks=tuple(
                    _removal(source_id, pos, len(sources))
                    for pos, source_id in enumerate(C_SOURCE_PAIRS[index])
                ),
                artifact_spec=artifact,
                exact_semantics=True,
                implementation_path=IMPLEMENTATION_PATH,
            )
        )
    return tuple(result)
