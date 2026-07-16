"""Three A-level foundational duality source laws."""

from __future__ import annotations

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ClosureStatus,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    ResidualResult,
)

from .duality import (
    C2ActionResult,
    FiniteInvolution,
    RelationGroupoid,
    TwoStateInput,
    TwoStateOrbit,
    involutive_c2_action,
    minimal_two_state_orbit,
    reciprocal_relation_action_groupoid,
)


APPENDIX = "appendix_tne_foundational_closure_architecture.tex"
APPENDIX_SHA256 = "2679b61a1d98100ed3a13669c16c299cd9b09807bc3847d383d559c9251189ea"


def _zero_residual(name: str, value: float) -> ResidualResult:
    return ResidualResult(
        name,
        (value,),
        0.0,
        value == 0.0,
        ClosureStatus.SATISFIED if value == 0.0 else ClosureStatus.OPEN,
    )


def contracts() -> tuple[ComplexContract, ...]:
    return (
        ComplexContract(
            ComplexId("reciprocal_relation_action_groupoid"),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            DomainSpec("finite involutive relation", "finite carrier and involutive permutation", (FiniteInvolution,)),
            CodomainSpec("reciprocal action groupoid", "graph, inverse graph, diagonal and composition", (RelationGroupoid,)),
            reciprocal_relation_action_groupoid,
            residual=lambda _source, output: _zero_residual(
                "relation composition", float(not output.composition_closed)
            ),
            implementation_path="the_nothingness_effect/foundational_architecture/duality/a_level.py",
        ),
        ComplexContract(
            ComplexId("minimal_two_state_involution_orbitwise_alternator"),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            DomainSpec("nonzero two-state generator", "nonzero complex source", (TwoStateInput,)),
            CodomainSpec("minimal two-state orbit", "fixed-point-free alternator", (TwoStateOrbit,)),
            minimal_two_state_orbit,
            residual=lambda _source, output: _zero_residual(
                "two-state fixed-point defect", float(not output.fixed_point_free)
            ),
            implementation_path="the_nothingness_effect/foundational_architecture/duality/a_level.py",
        ),
        ComplexContract(
            ComplexId("involutive_duality_c_2_action"),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            DomainSpec("finite involution", "finite C2 carrier", (FiniteInvolution,)),
            CodomainSpec("C2 action", "identity and nontrivial involution actions", (C2ActionResult,)),
            involutive_c2_action,
            residual=lambda _source, output: _zero_residual("C2 action", output.action_residual),
            implementation_path="the_nothingness_effect/foundational_architecture/duality/a_level.py",
        ),
    )
