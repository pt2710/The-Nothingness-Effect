from __future__ import annotations

import importlib

import numpy as np
import pytest


MAPPING_CASES = [
    ("empirical.mappings.dubler_redshift_mapping", "observable_x"),
    ("empirical.mappings.spiral_galaxy_mapping", "radius"),
    ("empirical.mappings.horizon_eht_mapping", "source"),
    ("empirical.mappings.hawking_flux_mapping", "x"),
    ("empirical.mappings.observer_memory_mapping", "time"),
    ("empirical.mappings.ripple_ringdown_mapping", "time"),
]


@pytest.mark.parametrize(("module_name", "observable_key"), MAPPING_CASES)
def test_mapping_pipeline_accepts_fixture_data(module_name: str, observable_key: str):
    mapping = importlib.import_module(module_name)

    empirical = mapping.prepare_empirical_observable()
    fitted = mapping.fit_parameters(empirical)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)

    assert len(empirical[observable_key]) > 0
    assert set(empirical["source_status"]) == {"fixture_only"}
    assert metrics["data_status"] == "fixture_only"
    assert metrics["passed_validation"] is True

    for values in residuals.values():
        array = np.asarray(values, dtype=float)
        assert array.shape[0] == len(empirical[observable_key])
        assert np.isfinite(array).all()

    for key, value in metrics.items():
        if isinstance(value, (bool, int, float, np.integer, np.floating)):
            assert np.isfinite(float(value)), key
