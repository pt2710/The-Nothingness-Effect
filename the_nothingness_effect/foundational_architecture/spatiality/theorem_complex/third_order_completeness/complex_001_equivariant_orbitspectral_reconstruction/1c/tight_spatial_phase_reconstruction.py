'Authoritative theorem title: Tight Spatial Phase Reconstruction.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='equivariant_orbit_spectral_reconstruction',
    role=TheoremRole.LEFT,
    authoritative_title='Tight Spatial Phase Reconstruction',
    authoritative_title_tex='Tight Spatial Phase Reconstruction',
    equation_labels=('eq:spatiality_phase_evaluation_kernel_1c', 'eq:spatiality_phase_frame_vectors_1c', 'eq:spatiality_phase_kernel_covariance_1c', 'eq:spatiality_phase_frame_bound_1c', 'eq:spatiality_phase_frame_reconstruction_1c', 'eq:spatiality_phase_kernel_iterated_covariance_1c', 'eq:spatiality_phase_analysis_map_1c', 'eq:spatiality_phase_field_synthesis_1c', 'eq:spatiality_reconstruction_principle_1c'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
