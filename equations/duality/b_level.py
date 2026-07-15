"""Two genuine B-level duality derivations."""

from __future__ import annotations

import numpy as np

from tne_runtime.theorem_complex_runtime import (
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
from tne_runtime.theorem_complex_runtime.invariants import source_removal_result

from .a_level import APPENDIX, APPENDIX_SHA256
from .duality import (
    FiniteInvolution,
    FreeCofreeDuality,
    FreeCofreeInput,
    ReciprocalDoubleCover,
    reciprocal_orbit_double_cover,
    two_state_free_cofree_duality,
)


def _residual(name: str, value: float) -> ResidualResult:
    return ResidualResult(
        name,
        (value,),
        1e-12,
        value <= 1e-12,
        ClosureStatus.SATISFIED if value <= 1e-12 else ClosureStatus.OPEN,
    )


def remove_relation_source(value: FiniteInvolution) -> SourceRemovalResult:
    complete = np.asarray(reciprocal_orbit_double_cover(value).deck_transformation, dtype=float)
    removed = np.arange(len(complete), dtype=float)
    return source_removal_result(
        ComplexId("reciprocal_relation_action_groupoid"), complete, removed, tolerance=1e-12
    )


def remove_alternator_source(value: FiniteInvolution) -> SourceRemovalResult:
    complete = np.asarray(reciprocal_orbit_double_cover(value).sheets, dtype=float)
    removed = np.asarray([(orbit[0], orbit[0]) for orbit in value.orbits], dtype=float)
    return source_removal_result(
        ComplexId("minimal_two_state_involution_orbitwise_alternator"),
        complete,
        removed,
        tolerance=1e-12,
    )


def _pairs(result: FreeCofreeDuality) -> np.ndarray:
    return np.asarray(result.free_pairs, dtype=complex)


def remove_two_state_source(value: FreeCofreeInput) -> SourceRemovalResult:
    complete = _pairs(two_state_free_cofree_duality(value))
    removed = np.asarray([(item, item) for item in value.values], dtype=complex)
    return source_removal_result(
        ComplexId("minimal_two_state_involution_orbitwise_alternator"),
        complete,
        removed,
        tolerance=1e-12,
    )


def remove_c2_action_source(value: FreeCofreeInput) -> SourceRemovalResult:
    complete = _pairs(two_state_free_cofree_duality(value))
    removed = np.asarray([(item, 0.0) for item in value.values], dtype=complex)
    return source_removal_result(
        ComplexId("involutive_duality_c_2_action"), complete, removed, tolerance=1e-12
    )


def contracts() -> tuple[ComplexContract, ...]:
    return (
        ComplexContract(
            ComplexId("reciprocal_orbit_double_cover"),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.B,
            (
                ComplexId("reciprocal_relation_action_groupoid"),
                ComplexId("minimal_two_state_involution_orbitwise_alternator"),
            ),
            DomainSpec("free finite involution", "fixed-point-free reciprocal carrier", (FiniteInvolution,)),
            CodomainSpec("two-sheeted orbit cover", "projection and unique deck action", (ReciprocalDoubleCover,)),
            reciprocal_orbit_double_cover,
            residual=lambda _source, output: _residual("double-cover fiber", output.fiber_residual),
            source_removal_checks=(remove_relation_source, remove_alternator_source),
            artifact_spec=ArtifactSpec(("cover_table", "source_ablation", "operator_diagram"), "python -m equations.duality.simulation"),
            implementation_path="equations/duality/b_level.py",
        ),
        ComplexContract(
            ComplexId("two_state_free_cofree_duality"),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.B,
            (
                ComplexId("minimal_two_state_involution_orbitwise_alternator"),
                ComplexId("involutive_duality_c_2_action"),
            ),
            DomainSpec("finite generators", "nonempty tuple of finite complex generators", (FreeCofreeInput,)),
            CodomainSpec("free-cofree duality", "signed pairs and evaluation", (FreeCofreeDuality,)),
            two_state_free_cofree_duality,
            residual=lambda _source, output: _residual("free-cofree equivariance", output.equivariance_residual),
            source_removal_checks=(remove_two_state_source, remove_c2_action_source),
            artifact_spec=ArtifactSpec(("pair_table", "source_ablation", "operator_diagram"), "python -m equations.duality.simulation"),
            implementation_path="equations/duality/b_level.py",
        ),
    )
