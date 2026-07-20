"""Explicit 15-contract recertification against the immutable authority ZIP."""
from __future__ import annotations
from dataclasses import replace
from .contracts import contracts as _legacy_contracts

APPENDIX = "appendix_the_completeness_theorem.tex"
APPENDIX_SHA256 = "d711e5c4260fb61bff1ef3e7ea3be14ef093370a9ff22607d2a54e74ba8b166b"


def contracts():
    source = _legacy_contracts()
    if len(source) != 15 or any(contract.appendix != APPENDIX for contract in source):
        raise RuntimeError("Completeness recertification expected exactly 15 contracts")
    return tuple(replace(contract, appendix_source_sha256=APPENDIX_SHA256) for contract in source)
