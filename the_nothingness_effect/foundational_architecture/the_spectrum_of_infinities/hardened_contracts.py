"""Authoritative registry and source-removal hardening for Spectrum contracts.

The canonical finite operators remain in ``canonical_contracts.py``. This
adapter replaces preliminary A2/A6 proxies with exact finite SOI laws and
recomputes every derived certificate after a source ablation instead of
setting the certificate to zero.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Callable

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    source_removal_result,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    ComplexContract,
    ComplexId,
    DomainSpec,
)

from . import canonical_contracts as _base
from .authoritative_dfi import spectrum_dfi_regularity_law
from .authoritative_finitization import (
    ScaledFinitizationInput,
    soi_finitization_l1_law,
)

DFI_IMPLEMENTATION = (
    "the_nothingness_effect/foundational_architecture/"
    "the_spectrum_of_infinities/authoritative_dfi.py"
)
FINITIZATION_IMPLEMENTATION = (
    "the_nothingness_effect/foundational_architecture/"
    "the_spectrum_of_infinities/authoritative_finitization.py"
)


def _recompute_certificate(
    complete_certificate: np.ndarray,
    source_blocks: tuple[np.ndarray, ...],
) -> np.ndarray:
    """Rebuild the derived certificate from the surviving typed source blocks."""

    certificate = np.asarray(complete_certificate, dtype=float).ravel()
    blocks = tuple(np.asarray(block, dtype=float).ravel() for block in source_blocks)
    concatenated_size = sum(block.size for block in blocks)
    if certificate.size == concatenated_size:
        return np.concatenate(blocks)
    if blocks and all(block.size == certificate.size for block in blocks):
        return sum(blocks, np.zeros_like(certificate))
    raise RuntimeError(
        "Spectrum source-removal certificate has no declared reconstruction law"
    )


def _source_removal_check(
    operator: Callable[[object], _base.LawCertificate],
    source_id: ComplexId,
    source_index: int,
) -> Callable[[object], object]:
    def check(value: object):
        output = operator(value)
        blocks = tuple(
            np.asarray(block, dtype=float).ravel()
            for block in output.source_blocks
        )
        if output.certificate is None:
            raise RuntimeError("derived Spectrum contract lacks a certificate")
        if source_index >= len(blocks):
            raise RuntimeError("source-removal index exceeds declared source blocks")

        complete_certificate = np.asarray(output.certificate, dtype=float).ravel()
        complete = np.concatenate((*blocks, complete_certificate))

        surviving = list(blocks)
        surviving[source_index] = np.zeros_like(surviving[source_index])
        surviving_tuple = tuple(surviving)
        removed_certificate = _recompute_certificate(
            complete_certificate,
            surviving_tuple,
        )
        removed = np.concatenate((*surviving_tuple, removed_certificate))
        return source_removal_result(
            source_id,
            complete,
            removed,
            tolerance=value.tolerance,
        )

    return check


def contracts() -> tuple[ComplexContract, ...]:
    result: list[ComplexContract] = []
    for contract in _base.contracts():
        if contract.complex_id == _base.A2:
            contract = replace(
                contract,
                operator=spectrum_dfi_regularity_law,
                implementation_path=DFI_IMPLEMENTATION,
            )
        elif contract.complex_id == _base.A6:
            contract = replace(
                contract,
                domain=DomainSpec(
                    str(contract.complex_id),
                    "finite SOI L1 approximation with explicit absolute scaling",
                    (_base.FinitizationInput, ScaledFinitizationInput),
                ),
                operator=soi_finitization_l1_law,
                implementation_path=FINITIZATION_IMPLEMENTATION,
            )
        if not contract.source_ids:
            result.append(contract)
            continue
        checks = tuple(
            _source_removal_check(contract.operator, source_id, index)
            for index, source_id in enumerate(contract.source_ids)
        )
        result.append(replace(contract, source_removal_checks=checks))
    return tuple(result)


__all__ = ["contracts"]
