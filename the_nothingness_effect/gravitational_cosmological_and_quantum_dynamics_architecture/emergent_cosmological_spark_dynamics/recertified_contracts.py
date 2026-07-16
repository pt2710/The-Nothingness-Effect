"""Recertified appendix-wide symmetric cosmology spatial closure."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from the_nothingness_effect._runtime.theorem_complex_runtime import ContractResult, ContractStatus, scale_aware_tolerance


@dataclass(frozen=True)
class SymmetricCosmologyInput:
    spatial_domain: np.ndarray
    source_fields: tuple[np.ndarray, ...]
    source_ids: tuple[str, ...]
    symmetry: np.ndarray
    boundary_mask: np.ndarray
    localization_radius: float


@dataclass(frozen=True)
class SymmetricCosmologyResult:
    local_operator: np.ndarray
    symmetric_operator: np.ndarray
    source_removal_residuals: tuple[float, ...]
    symmetry_residual: float
    boundary_residual: float
    localization_residual: float


def evaluate_symmetric_cosmology_cross_complex_closure(value: SymmetricCosmologyInput) -> ContractResult[SymmetricCosmologyResult]:
    domain = np.asarray(value.spatial_domain, dtype=float); fields = tuple(np.asarray(item, dtype=float) for item in value.source_fields); sigma = np.asarray(value.symmetry, dtype=float); boundary = np.asarray(value.boundary_mask, dtype=bool)
    if domain.ndim != 1 or len(fields) < 2 or len(value.source_ids) != len(fields) or any(field.shape != domain.shape for field in fields) or sigma.shape != (domain.size, domain.size) or boundary.shape != domain.shape or value.localization_radius <= 0.0 or not all(np.all(np.isfinite(item)) for item in (domain, sigma, *fields)):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_SPATIAL_SOURCE_RECORDS")
    local = np.sum(np.stack(fields), axis=0)
    for left in range(len(fields)):
        for right in range(left + 1, len(fields)):
            local = local + fields[left] * fields[right]
    symmetric = (local + sigma @ local) / 2.0
    tol = scale_aware_tolerance(*local); symmetry_residual = float(np.linalg.norm(sigma @ symmetric - symmetric)); boundary_residual = float(np.linalg.norm(symmetric[boundary])); coordinates = domain[:, None]
    far = np.abs(coordinates - coordinates.T) > value.localization_radius
    localization_residual = float(np.linalg.norm((sigma * far) @ local))
    removals = tuple(float(np.linalg.norm(symmetric - (np.sum(np.stack([field for j, field in enumerate(fields) if j != i]), axis=0)))) for i in range(len(fields)))
    residuals = {"symmetry": symmetry_residual, "boundary": boundary_residual, "localization": localization_residual}
    failed = symmetry_residual > tol or localization_residual > tol or any(item <= tol for item in removals)
    status = ContractStatus.FALSIFIED if failed else (ContractStatus.NUMERICAL_CANDIDATE if boundary_residual <= tol else ContractStatus.UNDECIDED)
    reason = "SOURCE_SYMMETRY_OR_LOCALIZATION_FAILURE" if failed else ("SPATIAL_CLOSURE_CANDIDATE" if boundary_residual <= tol else "BOUNDARY_CLOSURE_OPEN")
    return ContractResult(SymmetricCosmologyResult(local, symmetric, removals, symmetry_residual, boundary_residual, localization_residual), status, reason, residuals, {name: tol for name in residuals}, {"source_removal": dict(zip(value.source_ids, removals, strict=True))}, {"source_contract": "appendix_wide_symmetric_cosmology_cross_complex_closure_and_computational_falsification_interface", "spatial_domain_size": domain.size})

