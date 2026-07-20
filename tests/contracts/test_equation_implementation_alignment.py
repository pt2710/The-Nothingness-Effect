from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("torch")

from tools.build_equation_implementation_alignment import build


def test_all_351_theorem_complexes_have_equation_to_callable_bindings(tmp_path: Path):
    report = build(
        Path("docs/data/theorem_complex_implementation_matrix.csv"),
        tmp_path / "alignment.csv",
        tmp_path / "alignment.json",
    )
    assert report["passed"] is True
    assert report["rows"] == 351
    assert report["complete_mappings"] == 351
    assert report["source_faithful_corrections"] == 23
    assert report["first_labels"] == 351
    assert report["equation_labels"] > 351
    assert report["errors"] == []
