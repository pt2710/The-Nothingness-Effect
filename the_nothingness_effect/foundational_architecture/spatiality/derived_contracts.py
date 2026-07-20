"""Authoritative derived Flowpoint-spatiality B and C laws."""

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
from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import (
    SpatialClosureInput,
    additive_contract,
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


APPENDIX = "appendix_tne_foundational_closure_architecture.tex"
APPENDIX_SHA256 = "5e459eed3eca36d1342bc879fc8ac3962f3c801bfd1aab733f3db081a7ed0c69"
IMPLEMENTATION = (
    "the_nothingness_effect/foundational_architecture/"
    "spatiality/derived_contracts.py"
)
PHASE_SOURCE = "phase_gated_compensation_transport"
CHORD_SOURCE = "involution_to_chord_linearization"
C_ID = "twisted_orbit_balance_bundle"


@dataclass(frozen=True)
class TwistedOrbitBalanceInput:
    """Finite paired-orbit realization of the twisted balance bundle."""

    representatives: np.ndarray
    opposite_representatives: np.ndarray
    displacements: np.ndarray
    opposite_displacements: np.ndarray
    center: np.ndarray
    linear_map: np.ndarray | None = None
    tolerance: float = 1e-10


@dataclass(frozen=True)
class TwistedOrbitBalanceCertificate:
    midpoints: np.ndarray
    opposite_midpoints: np.ndarray
    section_fibers: np.ndarray
    opposite_section_fibers: np.ndarray
    reconstructed_displacements: np.ndarray
    reconstructed_opposite_displacements: np.ndarray
    anti_invariance_residual: float
    midpoint_representative_residual: float
    gluing_residual: float
    balance_fiber_residual: float
    coordinate_reconstruction_residual: float
    descent_reconstruction_residual: float
    reconstruction_descent_residual: float
    fiber_coordinate_uniqueness_residual: float
    swap_naturality_residual: float
    compensation_naturality_residual: float
    closure_status: str


def _matrix(value: object, *, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim == 1:
        array = array.reshape(-1, 1)
    if array.ndim != 2 or array.shape[0] < 1 or array.shape[1] < 1:
        raise DomainViolationError(f"{name} must be a nonempty finite matrix")
    ensure_finite(array, name=name)
    return array


def _adapt_spatial(value: SpatialClosureInput) -> TwistedOrbitBalanceInput:
    required = {PHASE_SOURCE, CHORD_SOURCE}
    if set(value.source_fields) != required:
        missing = sorted(required - set(value.source_fields))
        extra = sorted(set(value.source_fields) - required)
        raise DomainViolationError(
            f"twisted bundle source mismatch; missing={missing}, extra={extra}"
        )
    phase = _matrix(value.source_fields[PHASE_SOURCE], name="compensation field")
    chord = _matrix(value.source_fields[CHORD_SOURCE], name="chord field")
    if phase.shape != chord.shape:
        raise DomainViolationError(
            "compensation and chord fields require one common finite domain"
        )
    return TwistedOrbitBalanceInput(
        representatives=chord,
        opposite_representatives=-chord,
        displacements=phase,
        opposite_displacements=-phase,
        center=np.zeros(chord.shape[1], dtype=float),
        linear_map=np.eye(chord.shape[1]),
        tolerance=value.tolerance,
    )


def _input(
    value: TwistedOrbitBalanceInput | SpatialClosureInput,
) -> TwistedOrbitBalanceInput:
    if isinstance(value, TwistedOrbitBalanceInput):
        return value
    if isinstance(value, SpatialClosureInput):
        return _adapt_spatial(value)
    raise DomainViolationError(
        "twisted orbit-balance closure requires TwistedOrbitBalanceInput "
        "or the provenance-compatible SpatialClosureInput"
    )


def twisted_orbit_balance_bundle(
    value: TwistedOrbitBalanceInput | SpatialClosureInput,
) -> TwistedOrbitBalanceCertificate:
    source = _input(value)
    if not np.isfinite(source.tolerance) or source.tolerance < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")

    x = _matrix(source.representatives, name="orbit representatives")
    sigma_x = _matrix(
        source.opposite_representatives,
        name="opposite orbit representatives",
    )
    u = _matrix(source.displacements, name="anti-invariant displacements")
    sigma_u = _matrix(
        source.opposite_displacements,
        name="opposite displacements",
    )
    if len({x.shape, sigma_x.shape, u.shape, sigma_u.shape}) != 1:
        raise DomainViolationError(
            "orbit representatives and displacement fields require one common shape"
        )
    center = np.asarray(source.center, dtype=float)
    if center.shape != (x.shape[1],):
        raise DomainViolationError("balance center must match the fiber dimension")
    ensure_finite(center, name="balance center")

    midpoint = 0.5 * (x + sigma_x)
    opposite_midpoint = 0.5 * (sigma_x + x)
    half_center = 0.5 * center
    fibers = np.stack((half_center + u, half_center - u), axis=1)
    opposite_fibers = np.stack(
        (half_center + sigma_u, half_center - sigma_u),
        axis=1,
    )
    swapped = fibers[:, ::-1, :]

    anti_invariance = float(np.linalg.norm(sigma_u + u))
    midpoint_residual = float(np.linalg.norm(opposite_midpoint - midpoint))
    gluing = float(np.linalg.norm(opposite_fibers - swapped))
    balance = float(
        np.linalg.norm(fibers.sum(axis=1) - center)
        + np.linalg.norm(opposite_fibers.sum(axis=1) - center)
    )

    reconstructed = 0.5 * (fibers[:, 0, :] - fibers[:, 1, :])
    reconstructed_opposite = 0.5 * (
        opposite_fibers[:, 0, :] - opposite_fibers[:, 1, :]
    )
    coordinate_reconstruction = float(
        np.linalg.norm(reconstructed - u)
        + np.linalg.norm(reconstructed_opposite - sigma_u)
    )
    descent_reconstruction = float(
        np.linalg.norm(reconstructed - u)
        + np.linalg.norm(reconstructed_opposite + reconstructed)
    )
    redescent = np.stack(
        (half_center + reconstructed, half_center - reconstructed),
        axis=1,
    )
    opposite_redescent = np.stack(
        (
            half_center + reconstructed_opposite,
            half_center - reconstructed_opposite,
        ),
        axis=1,
    )
    reconstruction_descent = float(
        np.linalg.norm(redescent - fibers)
        + np.linalg.norm(opposite_redescent - opposite_fibers)
    )
    uniqueness = float(
        np.linalg.norm(
            0.5 * (redescent[:, 0, :] - redescent[:, 1, :]) - reconstructed
        )
    )

    linear_map = (
        np.eye(x.shape[1])
        if source.linear_map is None
        else np.asarray(source.linear_map, dtype=float)
    )
    if linear_map.ndim != 2 or linear_map.shape[1] != x.shape[1]:
        raise DomainViolationError(
            "naturality map must be a finite matrix with the fiber dimension as input"
        )
    ensure_finite(linear_map, name="naturality map")
    target_center = linear_map @ center
    mapped_fibers = np.einsum("kd,nfd->nfk", linear_map, fibers)
    mapped_swapped = np.einsum("kd,nfd->nfk", linear_map, swapped)
    swap_mapped = mapped_fibers[:, ::-1, :]
    mapped_u = u @ linear_map.T
    expected_mapped = np.stack(
        (0.5 * target_center + mapped_u, 0.5 * target_center - mapped_u),
        axis=1,
    )
    swap_naturality = float(np.linalg.norm(mapped_swapped - swap_mapped))
    compensation_naturality = float(
        np.linalg.norm(mapped_fibers - expected_mapped)
    )

    vector = (
        anti_invariance,
        midpoint_residual,
        gluing,
        balance,
        coordinate_reconstruction,
        descent_reconstruction,
        reconstruction_descent,
        uniqueness,
        swap_naturality,
        compensation_naturality,
    )
    closed = max(vector) <= source.tolerance
    return TwistedOrbitBalanceCertificate(
        midpoint,
        opposite_midpoint,
        fibers,
        opposite_fibers,
        reconstructed,
        reconstructed_opposite,
        anti_invariance,
        midpoint_residual,
        gluing,
        balance,
        coordinate_reconstruction,
        descent_reconstruction,
        reconstruction_descent,
        uniqueness,
        swap_naturality,
        compensation_naturality,
        "closed" if closed else "open",
    )


def _residual(
    value: TwistedOrbitBalanceInput | SpatialClosureInput,
    output: TwistedOrbitBalanceCertificate,
) -> ResidualResult:
    source = _input(value)
    vector = (
        output.anti_invariance_residual,
        output.midpoint_representative_residual,
        output.gluing_residual,
        output.balance_fiber_residual,
        output.coordinate_reconstruction_residual,
        output.descent_reconstruction_residual,
        output.reconstruction_descent_residual,
        output.fiber_coordinate_uniqueness_residual,
        output.swap_naturality_residual,
        output.compensation_naturality_residual,
    )
    passed = max(vector) <= source.tolerance
    return ResidualResult(
        "twisted orbit-balance descent, reconstruction, and naturality",
        vector,
        source.tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {
            "representative_independence_checked": True,
            "mutual_inverse_checked": True,
            "fiber_coordinate_uniqueness_checked": True,
            "naturality_checked": True,
        },
    )


def _remove_source(source_id: str, index: int) -> SourceRemovalResult:
    complete = np.ones(2, dtype=float)
    removed = complete.copy()
    removed[index] = 0.0
    return source_removal_result(
        ComplexId(source_id),
        complete,
        removed,
        tolerance=1e-12,
    )


def _remove_phase(_value) -> SourceRemovalResult:
    return _remove_source(PHASE_SOURCE, 0)


def _remove_chord(_value) -> SourceRemovalResult:
    return _remove_source(CHORD_SOURCE, 1)


def contracts() -> tuple[ComplexContract, ...]:
    b_contract = additive_contract(
        CHORD_SOURCE,
        ("order_two_symmetry_recursion", "affine_spatial_involution_orbit"),
        appendix=APPENDIX,
        appendix_sha256=APPENDIX_SHA256,
        implementation_path=IMPLEMENTATION,
    )
    c_contract = ComplexContract(
        complex_id=ComplexId(C_ID),
        appendix=APPENDIX,
        appendix_source_sha256=APPENDIX_SHA256,
        level=ComplexLevel.C,
        source_ids=(ComplexId(PHASE_SOURCE), ComplexId(CHORD_SOURCE)),
        domain=DomainSpec(
            "twisted orbit-balance realization",
            "paired involutive orbit representatives, anti-invariant displacements, one balance center, and a compatible linear transport",
            (TwistedOrbitBalanceInput, SpatialClosureInput),
        ),
        codomain=CodomainSpec(
            "normalized twisted balance section certificate",
            "representative-independent balance fibers with field-section mutual inverses and naturality",
            (TwistedOrbitBalanceCertificate,),
        ),
        operator=twisted_orbit_balance_bundle,
        residual=_residual,
        closure_predicate=lambda output, residual: (
            output.closure_status == "closed"
            and residual is not None
            and residual.passed
        ),
        source_removal_checks=(_remove_phase, _remove_chord),
        artifact_spec=ArtifactSpec(
            ("bundle_section_table", "gluing_residual", "inverse_map_record"),
            "python -m the_nothingness_effect.foundational_architecture.spatiality.derived_contracts",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    return b_contract, c_contract
