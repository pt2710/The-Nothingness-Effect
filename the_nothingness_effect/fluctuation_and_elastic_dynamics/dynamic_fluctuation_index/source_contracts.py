"""Executable DFI A05--A07 source contracts.

The operators expose fixed-map decomposition, DFI--Flowpoint interface, and
simulation consistency as separate typed laws.  Componentwise defects are
retained so equal totals cannot conceal a failed interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import (
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
    NonFiniteValueError,
)

from .contracts import APPENDIX, APPENDIX_SHA256
from .dfi import normalized_dfi, require_finite_dfi


SOURCE_IDS = tuple(
    ComplexId(identifier)
    for identifier in (
        "dfi_uniqueness_of_decomposition_and_mapping_ambiguity",
        "dfi_flowpoint_consistency_and_interface_inconsistency",
        "dfi_simulation_consistency_and_simulation_breakdown",
    )
)
IMPLEMENTATION = (
    "the_nothingness_effect/fluctuation_and_elastic_dynamics/"
    "dynamic_fluctuation_index/source_contracts.py"
)


@dataclass(frozen=True)
class DFICertificationInput:
    data: np.ndarray
    spectrum_scale: float
    mapped_data: np.ndarray | None = None
    flowpoint_components: np.ndarray | None = None
    simulated_components: np.ndarray | None = None
    tolerance: float = 1e-10


@dataclass(frozen=True)
class DFISourceCertificate:
    law_name: str
    components: np.ndarray
    total: float
    comparison_components: np.ndarray
    component_residual: np.ndarray
    total_residual: float
    invariant_residual: float
    failure_condition: str


def _array(value: object, *, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 2 or array.shape[0] < 1 or array.shape[1] < 2:
        raise DomainViolationError(f"{name} must be a finite rank-two array with at least two features")
    if not np.isfinite(array).all():
        raise NonFiniteValueError(f"{name} contains NaN or infinity")
    return array


def _validate(value: DFICertificationInput) -> np.ndarray:
    data = _array(value.data, name="DFI certification data")
    if not np.isfinite(value.spectrum_scale) or value.spectrum_scale <= 0.0:
        raise DomainViolationError("DFI certification spectrum_scale must be strictly positive")
    if not np.isfinite(value.tolerance) or value.tolerance < 0.0:
        raise DomainViolationError("DFI certification tolerance must be finite and non-negative")
    return data


def _components(data: np.ndarray, scale: float) -> np.ndarray:
    result = require_finite_dfi(normalized_dfi(data, spectrum_scale=scale))
    components = np.asarray(result.normalized_entropy, dtype=float)
    if not np.isfinite(components).all():
        raise NonFiniteValueError("DFI components contain NaN or infinity")
    return components


def source_operator(index: int, value: DFICertificationInput) -> DFISourceCertificate:
    data = _validate(value)
    components = _components(data, value.spectrum_scale)
    total = float(np.sum(components))

    if index == 0:
        comparison = (
            components.copy()
            if value.mapped_data is None
            else _components(
                _array(value.mapped_data, name="alternative DFI mapping"),
                value.spectrum_scale,
            )
        )
        if comparison.shape != components.shape:
            raise DomainViolationError("alternative DFI mapping must preserve component shape")
        failure = "mapping-dependent component assignment or ambiguous DFI decomposition"
    elif index == 1:
        comparison = (
            components.copy()
            if value.flowpoint_components is None
            else _array(value.flowpoint_components, name="Flowpoint interface components")
        )
        if comparison.shape != components.shape:
            raise DomainViolationError("Flowpoint interface must preserve DFI component indexing")
        failure = "non-commuting DFI--Flowpoint interface or componentwise entropy mismatch"
    elif index == 2:
        comparison = (
            components.copy()
            if value.simulated_components is None
            else _array(value.simulated_components, name="simulated DFI components")
        )
        if comparison.shape != components.shape:
            raise DomainViolationError("DFI simulation output must preserve component shape")
        failure = "formula-inconsistent DFI simulation, residual overflow, or simulation breakdown"
    else:
        raise IndexError(index)

    component_residual = components - comparison
    total_residual = abs(total - float(np.sum(comparison)))
    invariant_residual = float(
        np.sqrt(np.linalg.norm(component_residual) ** 2 + total_residual**2)
    )
    return DFISourceCertificate(
        str(SOURCE_IDS[index]),
        components,
        total,
        comparison,
        component_residual,
        total_residual,
        invariant_residual,
        failure,
    )


def _residual(
    source: DFICertificationInput,
    output: DFISourceCertificate,
) -> ResidualResult:
    passed = output.invariant_residual <= source.tolerance
    return ResidualResult(
        output.law_name,
        tuple(float(item) for item in output.component_residual.ravel())
        + (output.total_residual,),
        source.tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {
            "component_residual_norm": float(np.linalg.norm(output.component_residual)),
            "failure_condition": output.failure_condition,
        },
    )


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec(
        "DFI certification pullback",
        "finite fixed-map data plus optional Flowpoint, alternate-map, or simulation comparison",
        (DFICertificationInput,),
    )
    return tuple(
        ComplexContract(
            complex_id,
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            domain,
            CodomainSpec(
                str(complex_id),
                "componentwise DFI certificate with total and non-cancelling interface residuals",
                (DFISourceCertificate,),
            ),
            partial(source_operator, index),
            residual=_residual,
            exact_semantics=False,
            implementation_path=IMPLEMENTATION,
        )
        for index, complex_id in enumerate(SOURCE_IDS)
    )
