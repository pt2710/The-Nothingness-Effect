"""Spatially closed C-level affine history field."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from equations.theorem_complex_runtime import (
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
from equations.theorem_complex_runtime.invariants import source_removal_result

from .a_level import APPENDIX, APPENDIX_SHA256
from .flowpoint import AffineHistoryField, affine_history_field


@dataclass(frozen=True)
class AffineHistoryInput:
    bits: tuple[int, ...]
    balance: float
    kernel_offset: float
    history_amplitude: float
    tolerance: float = 1e-10


def affine_history_operator(value: AffineHistoryInput) -> AffineHistoryField:
    return affine_history_field(
        value.bits,
        balance=value.balance,
        kernel_offset=value.kernel_offset,
        history_amplitude=value.history_amplitude,
        tolerance=value.tolerance,
    )


def affine_history_residual(_source, output: AffineHistoryField) -> ResidualResult:
    vector = (
        output.balance_residual,
        output.boundary_trace_residual,
        output.reconstruction_residual,
    )
    norm = float(np.linalg.norm(vector))
    tolerance = 1e-10
    return ResidualResult(
        "affine history spatial closure",
        vector,
        tolerance,
        norm <= tolerance,
        ClosureStatus.CLOSED if norm <= tolerance else ClosureStatus.OPEN,
        metadata={"spatial_domain": list(output.spatial_points)},
    )


def affine_closure_predicate(output: AffineHistoryField, residual: ResidualResult | None) -> bool:
    return output.closure_status == "closed" and residual is not None and residual.passed


def _field_array(field: AffineHistoryField) -> np.ndarray:
    return np.asarray([(state.first, state.second) for state in field.states], dtype=float)


def remove_scheduled_history_source(value: AffineHistoryInput) -> SourceRemovalResult:
    complete = affine_history_operator(value)
    removed = affine_history_field(
        (0,) * len(value.bits),
        balance=value.balance,
        kernel_offset=value.kernel_offset,
        history_amplitude=value.history_amplitude,
        tolerance=value.tolerance,
    )
    return source_removal_result(
        ComplexId("scheduled_spectral_history"),
        _field_array(complete),
        _field_array(removed),
        tolerance=value.tolerance,
    )


def remove_phase_transport_source(value: AffineHistoryInput) -> SourceRemovalResult:
    complete = affine_history_operator(value)
    removed = affine_history_field(
        value.bits,
        balance=value.balance,
        kernel_offset=-value.history_amplitude,
        history_amplitude=value.history_amplitude,
        tolerance=value.tolerance,
    )
    return source_removal_result(
        ComplexId("phase_indexed_kernel_transport"),
        _field_array(complete),
        _field_array(removed),
        tolerance=value.tolerance,
    )


def contracts() -> tuple[ComplexContract, ...]:
    return (
        ComplexContract(
            complex_id=ComplexId("affine_history_field"),
            appendix=APPENDIX,
            appendix_source_sha256=APPENDIX_SHA256,
            level=ComplexLevel.C,
            source_ids=(
                ComplexId("scheduled_spectral_history"),
                ComplexId("phase_indexed_kernel_transport"),
            ),
            domain=DomainSpec(
                "finite discrete spatial history",
                "binary field on a nonempty discrete spatial domain",
                (AffineHistoryInput,),
            ),
            codomain=CodomainSpec(
                "closed affine balance field",
                "history-indexed states with local gradients and boundary traces",
                (AffineHistoryField,),
            ),
            operator=affine_history_operator,
            residual=affine_history_residual,
            closure_predicate=affine_closure_predicate,
            source_removal_checks=(remove_scheduled_history_source, remove_phase_transport_source),
            artifact_spec=ArtifactSpec(
                ("field_csv", "boundary_residual_map", "closure_animation_generator", "spatial_diagram"),
                "python -m equations.flowpoint.simulation",
            ),
            implementation_path="equations/flowpoint/c_level.py",
        ),
    )
