from __future__ import annotations

import numpy as np

from tools.run_source_faithful_convergence_benchmark import resample_input
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_elastic_dubler import elastic_dubler_sample
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_elastic_pi_ripples import elastic_pi_ripple_sample


def test_resample_preserves_uniform_grid_and_binary_parity():
    sample=resample_input(elastic_dubler_sample(),17)
    assert sample.coordinates.shape==(17,)
    assert np.allclose(np.diff(sample.coordinates),np.diff(sample.coordinates)[0])
    assert set(np.unique(sample.parity))<={0.0,1.0}
    assert sample.domain_elasticity.shape==(17,)


def test_resample_preserves_square_transport_shape():
    sample=resample_input(elastic_pi_ripple_sample(),17)
    assert sample.coordinate.shape==(17,)
    assert sample.transport_matrix.shape==(17,17)
    assert sample.source.shape==(17,)
    assert sample.detected.shape==(17,)
    assert set(np.unique(sample.flowpoint_parity))<={0.0,1.0}
    assert np.isfinite(sample.transport_matrix).all()
