'Authoritative theorem title: Entropic Instability (2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_entropic_stability_entropic_instability',
    role=TheoremRole.RIGHT,
    authoritative_title='Entropic Instability',
    authoritative_title_tex='Entropic Instability (2A)',
    equation_labels=('eq:edi07_entropic_stability_order_parameter_2a', 'eq:edi07_entropic_stability_branch_condition_2a', 'eq:ees_error_floor_2a', 'eq:ees_unbounded_variation_2a', 'eq:ees_growth_2a', 'eq:ees_linear_growth_2a', 'eq:ees_exponential_growth_2a', 'eq:ees_noncoercive_2a', 'eq:ees_noise_amplification_2a', 'eq:ees_linear_amplification_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
