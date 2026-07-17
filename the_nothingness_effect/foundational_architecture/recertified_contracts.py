"""Validate the 79-contract Foundational slice and return its supplemental registry."""
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
    already_registered = (
        *(
            contract
            for contract in recertified_source_contracts()
            if contract.appendix == APPENDIX
        ),
        *duality_contracts(),
        *symmetry_derived_contracts(),
        *symmetry_canonical_contracts(),
        *spatiality_derived_contracts(),
        *spatiality_canonical_contracts(),
    )
    supplemental = (
        *countable_contracts(),
        *uncountable_contracts(),
        *observation_contracts(),
        *spectrum_contracts(),
    )

    registered_by_id = {
        str(contract.complex_id): contract for contract in already_registered
    }
    supplemental_by_id = {
        str(contract.complex_id): contract for contract in supplemental
    }
    overlap = sorted(registered_by_id.keys() & supplemental_by_id.keys())
    if overlap:
        raise RuntimeError(
            f"Foundational supplemental registry duplicates active contracts: {overlap}"
        )

    complete = {**registered_by_id, **supplemental_by_id}
    if len(complete) != 79:
        raise RuntimeError(
            f"Foundational recertification expected 79 unique contracts, found {len(complete)}"
        )
    if any(contract.appendix != APPENDIX for contract in complete.values()):
        raise RuntimeError("Foundational recertification encountered a foreign appendix")

    return tuple(
        replace(contract, appendix_source_sha256=APPENDIX_SHA256)
        for _, contract in sorted(supplemental_by_id.items())
    )
