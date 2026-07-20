"""Canonical recertified DFI A05--A07 source-contract exports."""

from __future__ import annotations

from .extended_contracts import (
    DFIDecompositionCertificate,
    DFIDecompositionInput,
    DFIFlowpointInterfaceCertificate,
    DFIFlowpointInterfaceInput,
    DFISimulationCertificate,
    DFISimulationInput,
    contracts,
    decomposition_certificate,
    flowpoint_interface_certificate,
    simulation_certificate,
)


SOURCE_IDS = (
    "dfi_uniqueness_of_decomposition_and_mapping_ambiguity",
    "dfi_flowpoint_consistency_and_interface_inconsistency",
    "dfi_simulation_consistency_and_simulation_breakdown",
)


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
