from __future__ import annotations

import pytest

from equations.theorem_complex_runtime import (
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
)


SHA = "0" * 64


def test_complex_id_rejects_unstable_text():
    with pytest.raises(ValueError):
        ComplexId("Contains spaces")


def test_b_contract_requires_complete_sources():
    with pytest.raises(ValueError, match="at least two sources"):
        ComplexContract(
            complex_id=ComplexId("bad_b"),
            appendix="appendix.tex",
            appendix_source_sha256=SHA,
            level=ComplexLevel.B,
            source_ids=(ComplexId("source_a"),),
            domain=DomainSpec("R", "real scalar", (float,)),
            codomain=CodomainSpec("R", "real scalar", (float,)),
            operator=lambda value: value,
        )


def test_c_contract_requires_explicit_closure_predicate():
    with pytest.raises(ValueError, match="closure predicate"):
        ComplexContract(
            complex_id=ComplexId("bad_c"),
            appendix="appendix.tex",
            appendix_source_sha256=SHA,
            level=ComplexLevel.C,
            source_ids=(ComplexId("source_b1"), ComplexId("source_b2")),
            domain=DomainSpec("R", "real scalar", (float,)),
            codomain=CodomainSpec("R", "real scalar", (float,)),
            operator=lambda value: value,
        )
