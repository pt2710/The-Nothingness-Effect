'Authoritative theorem title: Complex Phase--First-Harmonic Equivalence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='complex_phase_coordinates_and_fourier_reconstruction',
    role=TheoremRole.CROSS,
    authoritative_title='Complex Phase–First-Harmonic Equivalence',
    authoritative_title_tex='Complex Phase--First-Harmonic Equivalence',
    equation_labels=('eq:fm_trig_first_harmonic_embedding_joint', 'eq:fm_trig_first_harmonic_equivalence_joint', 'eq:fm_trig_amplitude_phase_separation_joint', 'eq:fm_trig_amplitude_recovery_joint', 'eq:fm_trig_joint_synthesis_1a2a', 'eq:fm_trig_joint_principle_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
