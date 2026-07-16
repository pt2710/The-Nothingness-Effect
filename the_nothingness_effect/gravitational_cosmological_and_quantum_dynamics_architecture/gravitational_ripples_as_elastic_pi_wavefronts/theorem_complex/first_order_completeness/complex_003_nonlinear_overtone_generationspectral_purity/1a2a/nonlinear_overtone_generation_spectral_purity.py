'Authoritative theorem title: Nonlinear Overtone Generation $\\leftrightarrow$ Spectral Purity.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='nonlinear_overtone_generation_spectral_purity',
    role=TheoremRole.CROSS,
    authoritative_title='Nonlinear Overtone Generation <-> Spectral Purity',
    authoritative_title_tex='Nonlinear Overtone Generation $\\leftrightarrow$ Spectral Purity',
    equation_labels=('eq:grw03_overtone_purity_status_1a2a', 'eq:overtone_power_2f_1a2a', 'eq:overtone_power_3f_1a2a', 'eq:phase_locking_1a2a', 'eq:fourier_split_1a2a', 'eq:nonlinear_terms_1a2a', 'eq:indicator_equiv_1a2a', 'eq:deriv_equiv_1a2a-appendix_gravitational_ripples_as_entropic_wavefronts', 'eq:case_split_1a2a', 'eq:dP_dXi_1a2a', 'eq:xi_estimator_1a2a', 'eq:xi_closed_form_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
