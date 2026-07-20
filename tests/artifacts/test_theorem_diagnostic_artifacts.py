"""Artifact-bundle tests for machine-readable and visual diagnostics."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from tools.theorem_diagnostic_artifacts import (
    _jsonable,
    materialize_contract_diagnostics,
)
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_elastic_dubler import elastic_dubler_sample
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.source_faithful_contracts import contracts


def _fixture():
    sample=elastic_dubler_sample()
    contract=next(
        item for item in contracts()
        if str(item.complex_id)=="parity_localized_pdfi_response_operator"
    )
    return sample,contract,evaluate_contract(contract,sample)


def test_complex_scalars_are_explicitly_json_serializable():
    payload={
        "numpy":_jsonable(np.complex128(1.25-2.5j)),
        "python":_jsonable(3.0+4.0j),
    }
    assert payload=={
        "numpy":{"real":1.25,"imag":-2.5},
        "python":{"real":3.0,"imag":4.0},
    }
    assert json.loads(json.dumps(payload))==payload


def test_diagnostic_bundle_contains_machine_readable_and_visual_evidence(tmp_path: Path):
    sample,contract,evaluation=_fixture()
    removals=[check(sample) for check in contract.source_removal_checks]
    names=set(materialize_contract_diagnostics(tmp_path,contract,sample,evaluation,removals))

    assert any(name.endswith("_status.json") for name in names)
    assert any(name.endswith("_metrics.csv") for name in names)
    assert any(name.endswith("_source_removal.csv") for name in names)
    assert any(name.endswith("_trace.npz") for name in names)
    assert any(name.endswith("_diagnostic_2d.png") for name in names)
    assert any(name.endswith("_diagnostic_3d.png") for name in names)
    assert any(name.endswith("_diagnostic_5d_parallel.png") for name in names)
    assert any(name.endswith("_checksums.json") for name in names)

    status_path=next(tmp_path/name for name in names if name.endswith("_status.json"))
    status=json.loads(status_path.read_text(encoding="utf-8"))
    assert status["theorem_complex_id"]=="parity_localized_pdfi_response_operator"
    assert status["source_removal_diagnostics_materialized"] is True
    assert "not a proof" in status["claim_boundary"]

    trace_path=next(tmp_path/name for name in names if name.endswith("_trace.npz"))
    with np.load(trace_path) as trace:
        assert "output_vector" in trace
        assert "residual_vector" in trace
        assert trace["source_removal_residuals"].shape==(2,)

    checksum_path=next(tmp_path/name for name in names if name.endswith("_checksums.json"))
    checksums=json.loads(checksum_path.read_text(encoding="utf-8"))
    assert len(checksums["files"])==len(names)-1


def test_replay_without_typed_ablation_does_not_claim_source_necessity(tmp_path: Path):
    sample,contract,evaluation=_fixture()
    destination=tmp_path/"replay"
    names=set(
        materialize_contract_diagnostics(
            destination,
            contract,
            {"source":"executed_domain_suite_manifest","replay_only":True},
            evaluation,
            [],
        )
    )
    removal_path=next(
        destination/name for name in names if name.endswith("_source_removal.csv")
    )
    with removal_path.open(newline="",encoding="utf-8") as handle:
        rows=list(csv.DictReader(handle))
    assert rows==[
        {
            "theorem_complex_id":"parity_localized_pdfi_response_operator",
            "source_id":"",
            "applicable":"False",
            "baseline_response":"0.0",
            "removed_response":"0.0",
            "necessity_residual":"0.0",
            "necessary":"False",
            "evidence_source":"not_replayed_in_diagnostic_wrapper",
            "closure_status":evaluation.status.value,
        }
    ]
    status_path=next(destination/name for name in names if name.endswith("_status.json"))
    status=json.loads(status_path.read_text(encoding="utf-8"))
    assert status["source_removal_diagnostics_materialized"] is False
    assert not any(name.endswith("_diagnostic_5d_parallel.png") for name in names)
