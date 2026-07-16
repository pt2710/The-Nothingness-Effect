'Authoritative theorem title: Hawking Radiation Absence/Stasis.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_hawking_emission_radiative_stasis',
    role=TheoremRole.RIGHT,
    authoritative_title='Hawking Radiation Absence/Stasis',
    authoritative_title_tex='Hawking Radiation Absence/Stasis',
    equation_labels=('eq:bhhr05_elastic_pi_hawking_boundary_order_parameter_2a', 'eq:bhhr05_elastic_pi_hawking_boundary_branch_condition_2a', 'eq:hawking_no_emission_2a', 'eq:hawking_flux_zero_2a', 'eq:hawking_zero_flux_2a', 'eq:hawking_lemma_zero_emission_2a', 'eq:hawking_lemma_flux_zero_2a', 'eq:hawking_proof_algebraic_2a', 'eq:hawking_proof_flux_2a', 'eq:hawking_corollary_2a', 'eq:hawking_corollary_flux_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
