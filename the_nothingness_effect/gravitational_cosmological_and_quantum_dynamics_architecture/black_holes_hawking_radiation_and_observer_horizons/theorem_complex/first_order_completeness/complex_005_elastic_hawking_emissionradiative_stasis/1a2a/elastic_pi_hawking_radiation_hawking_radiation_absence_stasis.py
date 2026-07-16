'Authoritative theorem title: Elastic $\\pi$ Hawking Radiation $\\leftrightarrow$ Hawking Radiation Absence/Stasis.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_hawking_emission_radiative_stasis',
    role=TheoremRole.CROSS,
    authoritative_title='Elastic pi Hawking Radiation <-> Hawking Radiation Absence/Stasis',
    authoritative_title_tex='Elastic $\\pi$ Hawking Radiation $\\leftrightarrow$ Hawking Radiation Absence/Stasis',
    equation_labels=('eq:bhhr05_elastic_pi_hawking_boundary_status_1a2a', 'eq:hawking_emission_1a2a', 'eq:hawking_no_emission_1a2a', 'eq:hawking_flux_integral_1a2a', 'eq:hawking_flux_zero_integral_1a2a', 'eq:hawking_lemma_dual_emission_1a2a', 'eq:hawking_lemma_dual_stasis_1a2a', 'eq:hawking_lemma_dual_integral_1a2a', 'eq:hawking_proof_dual_emission_1a2a', 'eq:hawking_proof_dual_stasis_1a2a', 'eq:hawking_proof_dual_integral_1a2a', 'eq:hawking_corollary_dual_1a2a', 'eq:hawking_corollary_dual_integral_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
