from __future__ import annotations

import importlib


def test_fetch_modules_import_without_network_execution():
    modules = [
        "empirical.data_acquisition.fetch_all_empirical_data",
        "empirical.data_acquisition.fetch_redshift_clock_data",
        "empirical.data_acquisition.fetch_galaxy_rotation_data",
        "empirical.data_acquisition.fetch_eht_observables",
        "empirical.data_acquisition.fetch_hawking_analogue_or_limits",
        "empirical.data_acquisition.fetch_ligo_waveforms",
    ]
    for module_name in modules:
        importlib.import_module(module_name)
