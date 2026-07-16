"""Recertified affine spatial involution orbit."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from the_nothingness_effect._runtime.theorem_complex_runtime import ContractResult, ContractStatus, scale_aware_tolerance


@dataclass(frozen=True)
class AffineSpatialOrbitResult:
    image: np.ndarray
    return_image: np.ndarray
    midpoint: np.ndarray
    invariant_part: np.ndarray
    anti_invariant_part: np.ndarray


def evaluate_affine_spatial_involution_orbit(point, center, linear_involution) -> ContractResult[AffineSpatialOrbitResult]:
    z = np.asarray(point, dtype=float); p = np.asarray(center, dtype=float); r = np.asarray(linear_involution, dtype=float)
    if z.ndim != 1 or p.shape != z.shape or r.shape != (z.size, z.size) or not all(np.all(np.isfinite(item)) for item in (z, p, r)):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_AFFINE_DOMAIN")
    identity = np.eye(z.size); image = p + r @ (z - p); returned = p + r @ (image - p)
    invariant = (identity + r) @ (z - p) / 2.0; anti = (identity - r) @ (z - p) / 2.0
    tol = scale_aware_tolerance(*z, *p, *r.ravel()); involution = float(np.linalg.norm(r @ r - identity)); orbit = float(np.linalg.norm(returned - z)); midpoint = (z + image) / 2.0
    fixed = float(np.linalg.norm(image - z)) <= tol; failed = max(involution, orbit) > tol
    return ContractResult(AffineSpatialOrbitResult(image, returned, midpoint, invariant, anti), ContractStatus.FALSIFIED if failed else ContractStatus.EXACT, "NONINVOLUTIVE_AFFINE_MAP" if failed else ("FIXED_POINT" if fixed else "AFFINE_ORBIT_CERTIFIED"), {"linear_involution": involution, "orbit_return": orbit}, {"linear_involution": tol, "orbit_return": tol}, {"fixed_point": fixed}, {"source_contract": "affine_spatial_involution_orbit"})
