"""Explicit 7-contract recertification against the immutable authority ZIP."""
from __future__ import annotations
from dataclasses import replace
from .contracts import mathematical_closure_contracts as _legacy_contracts

APPENDIX = "appendix_tne_mathematical_closure_architecture.tex"
APPENDIX_SHA256 = "3f428e24ed9518655f94145dcd8667f979aa03c74f75695d8273da273e2538d0"


def mathematical_closure_contracts():
    source = _legacy_contracts()
    if len(source) != 7 or any(contract.appendix != APPENDIX for contract in source):
        raise RuntimeError("Mathematical Closure recertification expected exactly 7 contracts")
    return tuple(replace(contract, appendix_source_sha256=APPENDIX_SHA256) for contract in source)
