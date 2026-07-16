'Authoritative theorem title: Elastic $\\pi$ Hawking Radiation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_hawking_emission_radiative_stasis',
    role=TheoremRole.LEFT,
    authoritative_title='Elastic pi Hawking Radiation',
    authoritative_title_tex='Elastic $\\pi$ Hawking Radiation',
    equation_labels=('eq:bhhr05_elastic_pi_hawking_boundary_order_parameter_1a', 'eq:bhhr05_elastic_pi_hawking_boundary_branch_condition_1a', 'eq:hawking_emission_1a', 'eq:hawking_flux_gradient_1a', 'eq:hawking_positive_flux_1a', 'eq:hawking_lemma_emission_1a', 'eq:hawking_lemma_flux_1a', 'eq:hawking_proof_algebraic_1a', 'eq:hawking_proof_flux_1a', 'eq:hawking_corollary_1a', 'eq:hawking_corollary_flux_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
