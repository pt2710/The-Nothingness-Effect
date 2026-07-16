'Authoritative theorem title: Fourier Isometry and Reconstruction.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='complex_phase_coordinates_and_fourier_reconstruction',
    role=TheoremRole.RIGHT,
    authoritative_title='Fourier Isometry and Reconstruction',
    authoritative_title_tex='Fourier Isometry and Reconstruction',
    equation_labels=('eq:fm_trig_harmonic_maps_2a', 'eq:fm_trig_fourier_isometry_2a', 'eq:fm_trig_harmonic_tail_2a', 'eq:fm_trig_harmonic_certificate_2a', 'eq:fm_trig_harmonic_synthesis_2a', 'eq:fm_trig_harmonic_principle_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
