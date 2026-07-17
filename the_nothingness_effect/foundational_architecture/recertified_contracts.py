"""Explicit 79-contract Foundational recertification against authority bytes."""
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
    source = (
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
        *countable_contracts(),
        *uncountable_contracts(),
        *observation_contracts(),
        *spectrum_contracts(),
    )
    by_id = {str(contract.complex_id): contract for contract in source}
    if len(by_id) != 79:
        raise RuntimeError(f"Foundational recertification expected 79 unique contracts, found {len(by_id)}")
    if any(contract.appendix != APPENDIX for contract in by_id.values()):
        raise RuntimeError("Foundational recertification encountered a foreign appendix")
    return tuple(replace(contract, appendix_source_sha256=APPENDIX_SHA256) for _, contract in sorted(by_id.items()))
