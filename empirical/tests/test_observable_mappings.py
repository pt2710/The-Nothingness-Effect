from __future__ import annotations

import importlib
import inspect

import numpy as np
import pytest


MAPPING_CASES = [
    ("empirical.mappings.dubler_redshift_mapping", "observable_x"),
    ("empirical.mappings.spiral_galaxy_mapping", "radius"),
    ("empirical.mappings.horizon_eht_mapping", "source"),
    ("empirical.mappings.observer_memory_mapping", "time"),
    ("empirical.mappings.ripple_ringdown_mapping", "time"),
]


@pytest.mark.parametrize(("module_name", "observable_key"), MAPPING_CASES)
def test_mapping_pipeline_accepts_fixture_data(module_name: str, observable_key: str):
    mapping = importlib.import_module(module_name)

    empirical = mapping.prepare_empirical_observable()
    signature = inspect.signature(mapping.fit_parameters)
    fitted = (
        mapping.fit_parameters(empirical, parameter_sweep_level="quick")
        if "parameter_sweep_level" in signature.parameters
        else mapping.fit_parameters(empirical)
    )
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


def test_ringdown_mapping_emits_alignment_and_holdout_metadata():
    from empirical.mappings import ripple_ringdown_mapping as mapping

    empirical = mapping.prepare_empirical_observable()
    fitted = mapping.fit_parameters(empirical, parameter_sweep_level="quick")
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)

    assert "window_start_index" in empirical
    assert "train_RMSE" in metrics
    assert "test_RMSE" in metrics
    assert "tne_residual_envelope" in residuals


def test_galaxy_mapping_emits_baseline_family_and_profiles():
    from empirical.mappings import spiral_galaxy_mapping as mapping

    empirical = mapping.prepare_empirical_observable()
    fitted = mapping.fit_parameters(empirical, parameter_sweep_level="quick")
    prediction = mapping.prepare_model_prediction(empirical, fitted)

    assert "flat_baseline_prediction" in prediction
    assert "linear_baseline_prediction" in prediction
    assert "density_profile" in prediction
    assert "pitch_angle_proxy" in prediction


def test_eht_mapping_reports_source_specific_diagnostics():
    from empirical.mappings import horizon_eht_mapping as mapping

    empirical = mapping.prepare_empirical_observable()
    fitted = mapping.fit_parameters(empirical)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)

    assert "ring_prediction_source_specific" in prediction
    assert "source_specific_RMSE" in metrics
    assert "ring_normalized_residual" in residuals


def test_dubler_mapping_reports_formula_and_sign_metadata():
    from empirical.mappings import dubler_redshift_mapping as mapping

    empirical = mapping.prepare_empirical_observable()
    fitted = mapping.fit_parameters(empirical)
    assert "formula" in fitted
    assert "sign_convention" in empirical
