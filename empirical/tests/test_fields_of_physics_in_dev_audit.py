from __future__ import annotations

import csv
import json
from pathlib import Path

from empirical.audit.run_fields_of_physics_in_dev_audit import RECOMMENDED_ACTIONS, run


def test_fields_of_physics_in_dev_audit_outputs_exist():
    result = run()
    assert result["csv"].exists()
    assert result["json"].exists()
    assert result["report"].exists()

    with result["csv"].open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    major_paths = {row["path"] for row in rows}
    assert "fields_of_physics_in_dev/general_relativity/gravitational_curvature" in major_paths
    assert "fields_of_physics_in_dev/quantum_mechanics/wave_functionality/fp_pi_wave" in major_paths
    assert {row["recommended_action"] for row in rows}.issubset(RECOMMENDED_ACTIONS)

    payload = json.loads(result["json"].read_text(encoding="utf-8"))
    assert payload["rows"]
