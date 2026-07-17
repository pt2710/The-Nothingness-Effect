"""Artifact-bundle tests for JSON/CSV/NPZ and diagnostic projections."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from tools.theorem_diagnostic_artifacts import materialize_contract_diagnostics
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_elastic_dubler import elastic_dubler_sample
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.source_faithful_contracts import contracts


def test_diagnostic_bundle_contains_machine_readable_and_visual_evidence(tmp_path: Path):
    sample=elastic_dubler_sample()
    contract=next(item for item in contracts() if str(item.complex_id)=="parity_localized_pdfi_response_operator")
    evaluation=evaluate_contract(contract,sample)
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
    assert "not a proof" in status["claim_boundary"]

    trace_path=next(tmp_path/name for name in names if name.endswith("_trace.npz"))
    with np.load(trace_path) as trace:
        assert "output_vector" in trace
        assert "residual_vector" in trace
        assert trace["source_removal_residuals"].shape==(2,)

    checksum_path=next(tmp_path/name for name in names if name.endswith("_checksums.json"))
    checksums=json.loads(checksum_path.read_text(encoding="utf-8"))
    assert len(checksums["files"])==len(names)-1
