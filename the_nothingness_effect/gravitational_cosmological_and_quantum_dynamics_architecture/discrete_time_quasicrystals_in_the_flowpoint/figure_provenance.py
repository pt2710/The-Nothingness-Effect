"""Byte-verifying adapter for the recertified figure-backed closure contract."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ContractResult,
    ContractStatus,
)

from .recertified_contracts import (
    FigureClosureInput,
    FigureClosureResult,
    evaluate_figure_backed_closure as _evaluate_metadata_closure,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def _declared_paths(value: FigureClosureInput) -> tuple[str, ...]:
    raw = value.parameters.get("generated_files", ())
    if isinstance(raw, str):
        return (raw,)
    if not isinstance(raw, Iterable):
        return ()
    return tuple(str(item) for item in raw)


def _verified_hashes(
    relative_paths: tuple[str, ...],
    expected_hashes: tuple[str, ...],
) -> tuple[bool, tuple[str, ...], tuple[str, ...]]:
    if not relative_paths or len(relative_paths) != len(expected_hashes):
        return False, (), ("missing_or_misaligned_generated_files",)

    actual: list[str] = []
    failures: list[str] = []
    root = REPOSITORY_ROOT.resolve()
    for relative, expected in zip(relative_paths, expected_hashes, strict=True):
        candidate = Path(relative)
        if candidate.is_absolute():
            failures.append(f"absolute_path:{relative}")
            continue
        resolved = (root / candidate).resolve()
        if resolved != root and root not in resolved.parents:
            failures.append(f"path_escape:{relative}")
            continue
        if not resolved.is_file():
            failures.append(f"missing_file:{relative}")
            continue
        digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
        actual.append(digest)
        if digest.lower() != expected.lower():
            failures.append(f"hash_mismatch:{relative}")
    return not failures, tuple(actual), tuple(failures)


def evaluate_figure_backed_closure(
    value: FigureClosureInput,
) -> ContractResult[FigureClosureResult]:
    """Verify tracked artifact bytes before accepting figure-backed evidence."""

    result = _evaluate_metadata_closure(value)
    relative_paths = _declared_paths(value)
    verified, actual_hashes, failures = _verified_hashes(
        relative_paths,
        tuple(value.generated_file_hashes),
    )
    provenance = dict(result.provenance)
    provenance.update(
        {
            "generated_files": relative_paths,
            "verified_file_hashes": actual_hashes,
            "byte_verification_failures": failures,
            "artifact_bytes_verified": verified,
        }
    )
    if not verified:
        residuals = dict(result.residuals)
        residuals["artifact_byte_verification"] = 1.0
        tolerances = dict(result.tolerances)
        tolerances["artifact_byte_verification"] = 0.0
        return ContractResult(
            result.value,
            ContractStatus.FALSIFIED,
            "FIGURE_BYTES_OR_HASH_MISMATCH",
            residuals,
            tolerances,
            dict(result.witnesses),
            provenance,
        )
    return ContractResult(
        result.value,
        result.status,
        result.reason_code,
        dict(result.residuals),
        dict(result.tolerances),
        dict(result.witnesses),
        provenance,
    )


# Ensure direct imports from recertified_contracts receive the hardened evaluator
# after the package initializer loads this adapter.
from . import recertified_contracts as _recertified_contracts

_recertified_contracts.evaluate_figure_backed_closure = evaluate_figure_backed_closure
