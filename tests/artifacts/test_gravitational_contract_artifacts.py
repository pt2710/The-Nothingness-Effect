from __future__ import annotations

import json

import pytest

from equations.gravitational_contract_artifacts import run_suite
from equations.gravitational_contract_runtime import APPENDIX_SHA256, SPECS


@pytest.mark.parametrize("module", sorted(SPECS))
def test_each_physical_module_emits_seven_manifests(tmp_path, module):
    outputs = run_suite(module, tmp_path / module, seed=0)

    assert outputs["metrics"].is_file()
    assert outputs["figure"].is_file()
    assert len(outputs["manifests"]) == 7
    for path in outputs["manifests"]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["appendix_source_sha256"] == APPENDIX_SHA256
        assert payload["claim_boundary"] == "finite computational support; not a formal proof substitute"
        assert payload["seed"] == 0
