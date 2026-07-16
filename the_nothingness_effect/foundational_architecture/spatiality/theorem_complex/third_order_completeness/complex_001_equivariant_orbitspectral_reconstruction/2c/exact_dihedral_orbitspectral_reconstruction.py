'Authoritative theorem title: Exact Dihedral Orbit--Spectral Reconstruction.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='equivariant_orbit_spectral_reconstruction',
    role=TheoremRole.RIGHT,
    authoritative_title='Exact Dihedral Orbit–Spectral Reconstruction',
    authoritative_title_tex='Exact Dihedral Orbit--Spectral Reconstruction',
    equation_labels=('eq:spatiality_orbit_fourier_kernel_2c', 'eq:spatiality_kernel_rotation_covariance_2c', 'eq:spatiality_kernel_reflection_covariance_2c', 'eq:spatiality_kernel_fourier_reconstruction_2c', 'eq:spatiality_kernel_orthogonality_2c', 'eq:spatiality_kernel_completeness_2c', 'eq:spatiality_dihedral_kernel_synthesis_2c', 'eq:spatiality_reconstruction_principle_2c'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
