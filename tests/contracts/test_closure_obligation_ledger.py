from __future__ import annotations

import json
from pathlib import Path

from tools.build_closure_obligation_ledger import build


def _write(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_closure_ledger_represents_every_open_and_candidate_state(tmp_path: Path):
    status = _write(
        tmp_path / "status.json",
        {
            "open_and_numerical_candidate_preserved": 2,
            "records": [
                {
                    "complex_id": "open-law",
                    "appendix_file": "a.tex",
                    "level": "B",
                    "runtime_status": "implemented",
                    "source_exactness": "exact",
                    "closure_status": "open",
                    "validation_status": "synthetic",
                    "artifact_status": "complete_core_bundle",
                    "implementation_path": "open.py",
                },
                {
                    "complex_id": "candidate-law",
                    "appendix_file": "a.tex",
                    "level": "C",
                    "runtime_status": "implemented",
                    "source_exactness": "exact",
                    "closure_status": "numerical_candidate",
                    "validation_status": "synthetic",
                    "artifact_status": "complete_core_bundle",
                    "implementation_path": "candidate.py",
                },
                {
                    "complex_id": "closed-law",
                    "appendix_file": "a.tex",
                    "level": "A",
                    "runtime_status": "implemented",
                    "source_exactness": "exact",
                    "closure_status": "satisfied",
                    "validation_status": "synthetic",
                    "artifact_status": "complete_core_bundle",
                    "implementation_path": "closed.py",
                },
            ],
        },
    )
    provenance = _write(
        tmp_path / "provenance.json",
        {
            "manifests": [
                {
                    "theorem_complex_id": "open-law",
                    "closure_status": "open",
                    "residual_vector": [1.0, 2.0],
                    "numeric_tolerances": {"residual": 1e-6},
                    "approximation_metadata": {"exact_semantics": False},
                },
                {
                    "theorem_complex_id": "candidate-law",
                    "closure_status": "numerical_candidate",
                    "residual_vector": [1e-8],
                    "numeric_tolerances": {"residual": 1e-6},
                    "approximation_metadata": {"exact_semantics": False},
                },
                {
                    "theorem_complex_id": "closed-law",
                    "closure_status": "satisfied",
                    "residual_vector": [0.0],
                    "numeric_tolerances": {"residual": 1e-6},
                    "approximation_metadata": {"exact_semantics": True},
                },
            ]
        },
    )
    csv_output = tmp_path / "ledger.csv"
    json_output = tmp_path / "ledger.json"
    report = build(status, provenance, csv_output, json_output)

    assert report["all_open_states_represented"] is True
    assert report["open_or_numerical_candidate_count"] == 2
    assert report["counts"] == {"numerical_candidate": 1, "open": 1}
    assert {item["complex_id"] for item in report["records"]} == {
        "open-law",
        "candidate-law",
    }
    candidate = next(
        item for item in report["records"] if item["complex_id"] == "candidate-law"
    )
    assert "attainment" in candidate["required_evidence"]
    assert csv_output.is_file()
    assert json_output.is_file()
