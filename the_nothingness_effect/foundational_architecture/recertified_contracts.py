"""Validate and register the 79-contract Foundational authority slice."""
from __future__ import annotations

from dataclasses import replace

from the_nothingness_effect._runtime.theorem_complex_runtime.recertified_catalog import (
    contracts as recertified_source_contracts,
)

from .duality.contracts import duality_contracts
from .symmetry.derived_contracts import contracts as symmetry_derived_contracts
from .symmetry.canonical_contracts import contracts as symmetry_canonical_contracts
from .spatiality.derived_contracts import contracts as spatiality_derived_contracts
from .spatiality.canonical_contracts import contracts as spatiality_canonical_contracts
from .countable_infinity.canonical_contracts import contracts as countable_contracts
from .uncountable_infinity.canonical_contracts import contracts as uncountable_contracts
from .observation_and_collapse.canonical_contracts import contracts as observation_contracts
from .the_spectrum_of_infinities.hardened_contracts import contracts as spectrum_contracts

APPENDIX = "appendix_tne_foundational_closure_architecture.tex"
APPENDIX_SHA256 = "2679b61a1d98100ed3a13669c16c299cd9b09807bc3847d383d559c9251189ea"


def contracts():
    externally_registered = {
        str(contract.complex_id): contract
        for contract in recertified_source_contracts()
        if contract.appendix == APPENDIX
    }
    local_source = (
        *duality_contracts(),
        *symmetry_derived_contracts(),
        *symmetry_canonical_contracts(),
        *spatiality_derived_contracts(),
        *spatiality_canonical_contracts(),
        *countable_contracts(),
        *uncountable_contracts(),
        *observation_contracts(),
        *spectrum_contracts(),
    )
    local_by_id = {str(contract.complex_id): contract for contract in local_source}

    overlap = sorted(externally_registered.keys() & local_by_id.keys())
    if overlap:
        raise RuntimeError(
            f"Foundational local registry duplicates recertified source adapters: {overlap}"
        )
    complete = {**externally_registered, **local_by_id}
    if len(externally_registered) != 5:
        raise RuntimeError(
            "Foundational recertification expected five external source adapters, "
            f"found {len(externally_registered)}"
        )
    if len(local_by_id) != 74 or len(complete) != 79:
        raise RuntimeError(
            "Foundational recertification expected 5 external + 74 local = 79 "
            f"unique contracts, found {len(externally_registered)} + "
            f"{len(local_by_id)} = {len(complete)}"
        )
    if any(contract.appendix != APPENDIX for contract in complete.values()):
        raise RuntimeError("Foundational recertification encountered a foreign appendix")

    return tuple(
        replace(contract, appendix_source_sha256=APPENDIX_SHA256)
        for _, contract in sorted(local_by_id.items())
    )
