"""Regression tests: source ablations must rerun the declared operator."""
from __future__ import annotations

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_black_hole import black_hole_sample
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_elastic_dubler import elastic_dubler_sample
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_elastic_pi_ripples import elastic_pi_ripple_sample
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_locality_gravity import locality_gravity_sample
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons import source_faithful_contracts as black_hole
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts import source_faithful_contracts as ripples
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity import source_faithful_contracts as locality
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect import source_faithful_contracts as dubler


def _norm(value) -> float:
    return float(np.linalg.norm(np.asarray(value).ravel()))


def test_elastic_dubler_b_ablation_matches_recomputed_operator():
    sample=elastic_dubler_sample()
    for identifier,source_a,source_b in dubler.legacy.B_SPECS:
        for index,source_id in enumerate((source_a,source_b)):
            active=[True,True]; active[index]=False
            expected=dubler._b_operator(identifier,sample,tuple(active))
            observed=dubler._remove_a(identifier,index,sample)
            assert str(observed.source_id)==source_id
            assert np.isclose(observed.removed_response,_norm(expected.combined_operator))
            assert observed.necessary


def test_locality_b_ablation_uses_every_declared_source():
    sample=locality_gravity_sample()
    for identifier,source_ids in locality.legacy.B_SPECS:
        for index,source_id in enumerate(source_ids):
            active=[True]*len(source_ids); active[index]=False
            expected=locality._b_operator(identifier,sample,tuple(active))
            observed=locality._remove_a(identifier,index,sample)
            assert str(observed.source_id)==source_id
            assert np.isclose(observed.removed_response,_norm(expected.combined_operator))
            assert observed.necessary
    cluster_contract=locality._b_operator(locality.B_IDS[3],sample)
    assert len(cluster_contract.source_responses)==3


def test_black_hole_b_and_c_ablation_are_recomputed():
    sample=black_hole_sample()
    for identifier,source_ids in black_hole.legacy.B_SPECS:
        for index,source_id in enumerate(source_ids):
            active=[True]*len(source_ids); active[index]=False
            expected=black_hole._b_operator(identifier,sample,tuple(active))
            observed=black_hole._remove_a(identifier,index,sample)
            assert str(observed.source_id)==source_id
            assert np.isclose(observed.removed_response,_norm(expected.combined_operator))
            assert observed.necessary
    for index,identifier in enumerate(black_hole.B_IDS):
        active=[True,True,True]; active[index]=False
        expected=black_hole._c_operator(sample,tuple(active))
        observed=black_hole._remove_b(index,sample)
        assert str(observed.source_id)==identifier
        assert np.isclose(observed.removed_response,_norm(expected.local_field))
        assert observed.necessary


def test_ripple_b_ablation_matches_recomputed_operator():
    sample=elastic_pi_ripple_sample()
    for identifier,source_ids in ripples.legacy.B_SPECS:
        for index,source_id in enumerate(source_ids):
            active=[True]*len(source_ids); active[index]=False
            expected=ripples._b_operator(identifier,sample,tuple(active))
            observed=ripples._remove_a(identifier,index,sample)
            assert str(observed.source_id)==source_id
            assert np.isclose(observed.removed_response,_norm(expected.combined_operator))
            assert observed.necessary
