"""C-level invariant/anti-invariant orbit field."""

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
from .duality import FiniteInvolution, OrbitField, invariant_anti_invariant_orbit_field


def field_residual(_source, output: OrbitField) -> ResidualResult:
    vector = (output.reconstruction_residual, output.boundary_trace_residual)
    norm = float(np.linalg.norm(vector))
    return ResidualResult(
        "invariant/anti-invariant spatial reconstruction",
        vector,
        1e-10,
        norm <= 1e-10,
        ClosureStatus.CLOSED if norm <= 1e-10 else ClosureStatus.OPEN,
        metadata={"spatial_domain": list(output.spatial_domain)},
    )


def remove_double_cover_source(value: FiniteInvolution) -> SourceRemovalResult:
    complete = invariant_anti_invariant_orbit_field(value)
    return source_removal_result(
        ComplexId("reciprocal_orbit_double_cover"),
        np.asarray(complete.reconstruction),
        np.asarray(complete.anti_invariant_field),
        tolerance=1e-12,
    )


def remove_free_cofree_source(value: FiniteInvolution) -> SourceRemovalResult:
    complete = invariant_anti_invariant_orbit_field(value)
    return source_removal_result(
        ComplexId("two_state_free_cofree_duality"),
        np.asarray(complete.reconstruction),
        np.asarray(complete.invariant_field),
        tolerance=1e-12,
    )


def contracts() -> tuple[ComplexContract, ...]:
    return (
        ComplexContract(
            ComplexId("invariant_anti_invariant_orbit_fields"),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.C,
            (ComplexId("reciprocal_orbit_double_cover"), ComplexId("two_state_free_cofree_duality")),
            DomainSpec("finite orbit field", "finite involution with spatial orbit index", (FiniteInvolution,)),
            CodomainSpec("closed orbit field", "invariant and anti-invariant sections with reconstruction", (OrbitField,)),
            invariant_anti_invariant_orbit_field,
            residual=field_residual,
            closure_predicate=lambda output, residual: output.closure_status == "closed" and residual is not None and residual.passed,
            source_removal_checks=(remove_double_cover_source, remove_free_cofree_source),
            artifact_spec=ArtifactSpec(("field_csv", "boundary_plot", "animation_generator", "bundle_diagram"), "python -m equations.duality.simulation"),
            implementation_path="equations/duality/c_level.py",
        ),
    )
