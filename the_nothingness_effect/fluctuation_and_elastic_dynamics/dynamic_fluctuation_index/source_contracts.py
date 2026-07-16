"""Compatibility shim for the recertified DFI A05--A07 source contracts.

The canonical registrations live in :mod:`extended_contracts` and are included
once through :mod:`derived_contracts`.  This module remains importable for
callers created during the recertification work but deliberately contributes no
second catalog registration.
"""

from __future__ import annotations

from .extended_contracts import (
    DFIDecompositionCertificate,
    DFIDecompositionInput,
    DFIFlowpointInterfaceCertificate,
    DFIFlowpointInterfaceInput,
    DFISimulationCertificate,
    DFISimulationInput,
    decomposition_certificate,
    flowpoint_interface_certificate,
    simulation_certificate,
)


SOURCE_IDS = (
    "dfi_uniqueness_of_decomposition_and_mapping_ambiguity",
    "dfi_flowpoint_consistency_and_interface_inconsistency",
    "dfi_simulation_consistency_and_simulation_breakdown",
)


def contracts() -> tuple[()]:
    """Return no duplicate registrations; use ``extended_contracts.contracts``."""

    return ()


__all__ = (
    "DFIDecompositionCertificate",
    "DFIDecompositionInput",
    "DFIFlowpointInterfaceCertificate",
    "DFIFlowpointInterfaceInput",
    "DFISimulationCertificate",
    "DFISimulationInput",
    "SOURCE_IDS",
    "contracts",
    "decomposition_certificate",
    "flowpoint_interface_certificate",
    "simulation_certificate",
)
