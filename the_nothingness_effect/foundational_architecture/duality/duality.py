"""Canonical finite involutive duality primitives.

The compatibility ``duality_equation`` wrapper is retained, while theorem
contracts use explicit involutions, relations, actions, fields, and residuals.
"""

from __future__ import annotations

from dataclasses import dataclass
import warnings

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime.types import DomainViolationError
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import ensure_finite


_COMPATIBILITY_WARNING_EMITTED = False


@dataclass(frozen=True)
class FiniteInvolution:
    points: tuple[complex, ...]
    image: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.points or len(self.points) != len(self.image):
            raise DomainViolationError("finite involution requires equally sized nonempty points and image")
        if sorted(self.image) != list(range(len(self.points))):
            raise DomainViolationError("involution image must be a permutation")
        if any(self.image[self.image[index]] != index for index in range(len(self.image))):
            raise DomainViolationError("declared map does not square to the identity")
        ensure_finite(self.points, name="duality points")

    def apply_index(self, index: int) -> int:
        if index < 0 or index >= len(self.points):
            raise DomainViolationError("point index lies outside the involution carrier")
        return self.image[index]

    @property
    def fixed_points(self) -> tuple[int, ...]:
        return tuple(index for index, target in enumerate(self.image) if index == target)

    @property
    def orbits(self) -> tuple[tuple[int, ...], ...]:
        unseen = set(range(len(self.points)))
        result: list[tuple[int, ...]] = []
        while unseen:
            index = min(unseen)
            target = self.image[index]
            orbit = (index,) if target == index else tuple(sorted((index, target)))
            result.append(orbit)
            unseen.difference_update(orbit)
        return tuple(result)


@dataclass(frozen=True)
class RelationGroupoid:
    graph: tuple[tuple[int, int], ...]
    inverse_graph: tuple[tuple[int, int], ...]
    diagonal: tuple[tuple[int, int], ...]
    composition_closed: bool


def reciprocal_relation_action_groupoid(value: FiniteInvolution) -> RelationGroupoid:
    graph = tuple((index, target) for index, target in enumerate(value.image))
    inverse = tuple((target, index) for index, target in graph)
    diagonal = tuple((index, index) for index in value.fixed_points)
    composition_closed = all(value.image[value.image[index]] == index for index in range(len(value.image)))
    return RelationGroupoid(graph, inverse, diagonal, composition_closed)


@dataclass(frozen=True)
class TwoStateInput:
    positive: complex


@dataclass(frozen=True)
class TwoStateOrbit:
    states: tuple[complex, complex]
    alternator: tuple[int, int]
    fixed_point_free: bool


def minimal_two_state_orbit(value: TwoStateInput) -> TwoStateOrbit:
    ensure_finite(value.positive, name="two-state source")
    if value.positive == 0:
        raise DomainViolationError("minimal two-state duality requires a nonzero source")
    return TwoStateOrbit((complex(value.positive), complex(-value.positive)), (1, 0), True)


@dataclass(frozen=True)
class C2ActionResult:
    identity_action: tuple[int, ...]
    involution_action: tuple[int, ...]
    action_residual: float


def involutive_c2_action(value: FiniteInvolution) -> C2ActionResult:
    identity = tuple(range(len(value.points)))
    residual = float(sum(value.image[value.image[index]] != index for index in identity))
    return C2ActionResult(identity, value.image, residual)


@dataclass(frozen=True)
class ReciprocalDoubleCover:
    base_orbits: tuple[tuple[int, ...], ...]
    sheets: tuple[tuple[int, int], ...]
    projection: tuple[int, ...]
    deck_transformation: tuple[int, ...]
    fiber_residual: float


def reciprocal_orbit_double_cover(value: FiniteInvolution) -> ReciprocalDoubleCover:
    if value.fixed_points:
        raise DomainViolationError("the minimal reciprocal double cover requires a free involution")
    orbits = value.orbits
    sheets = tuple((orbit[0], orbit[1]) for orbit in orbits)
    projection = tuple(orbit_index for orbit_index in range(len(orbits)) for _ in (0, 1))
    deck = tuple(index ^ 1 for index in range(2 * len(orbits)))
    residual = float(sum(projection[index] != projection[deck[index]] for index in range(len(deck))))
    return ReciprocalDoubleCover(orbits, sheets, projection, deck, residual)


@dataclass(frozen=True)
class FreeCofreeInput:
    values: tuple[complex, ...]


@dataclass(frozen=True)
class FreeCofreeDuality:
    free_pairs: tuple[tuple[complex, complex], ...]
    evaluation: tuple[complex, ...]
    equivariance_residual: float


def two_state_free_cofree_duality(value: FreeCofreeInput) -> FreeCofreeDuality:
    if not value.values:
        raise DomainViolationError("free-cofree duality requires at least one generator")
    ensure_finite(value.values, name="free-cofree generators")
    pairs = tuple((complex(item), complex(-item)) for item in value.values)
    evaluation = tuple(first + second for first, second in pairs)
    residual = float(np.linalg.norm(np.asarray(evaluation)))
    return FreeCofreeDuality(pairs, evaluation, residual)


@dataclass(frozen=True)
class OrbitField:
    spatial_domain: tuple[int, ...]
    invariant_field: tuple[complex, ...]
    anti_invariant_field: tuple[complex, ...]
    reconstruction: tuple[complex, ...]
    reconstruction_residual: float
    boundary_trace_residual: float
    closure_status: str


def invariant_anti_invariant_orbit_field(value: FiniteInvolution) -> OrbitField:
    values = np.asarray(value.points, dtype=complex)
    transformed = values[np.asarray(value.image)]
    invariant = 0.5 * (values + transformed)
    anti = 0.5 * (values - transformed)
    reconstruction = invariant + anti
    residual = float(np.linalg.norm(reconstruction - values))
    boundary = float(abs(reconstruction[0] - values[0]) + abs(reconstruction[-1] - values[-1]))
    closed = residual <= 1e-10 and boundary <= 1e-10
    return OrbitField(
        tuple(range(len(values))),
        tuple(complex(item) for item in invariant),
        tuple(complex(item) for item in anti),
        tuple(complex(item) for item in reconstruction),
        residual,
        boundary,
        "closed" if closed else "open",
    )


def duality_equation(y):
    """Compatibility wrapper returning the source and its reciprocal partner."""

    global _COMPATIBILITY_WARNING_EMITTED
    if not _COMPATIBILITY_WARNING_EMITTED:
        warnings.warn(
            "duality_equation is a compatibility wrapper; use typed duality contracts",
            DeprecationWarning,
            stacklevel=2,
        )
        _COMPATIBILITY_WARNING_EMITTED = True
    if isinstance(y, bool):
        return y, not y
    if not isinstance(y, (int, float, complex)):
        raise TypeError(f"Unsupported duality value: {type(y)}")
    ensure_finite(y, name="duality value")
    return y, -y
