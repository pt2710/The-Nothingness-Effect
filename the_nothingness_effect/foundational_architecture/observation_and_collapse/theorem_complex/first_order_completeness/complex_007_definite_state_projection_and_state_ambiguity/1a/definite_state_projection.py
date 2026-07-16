'Authoritative theorem title: Definite-State Projection.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='definite_state_projection_and_state_ambiguity',
    role=TheoremRole.LEFT,
    authoritative_title='Definite-State Projection',
    authoritative_title_tex='Definite-State Projection',
    equation_labels=('eq:obs13_pvm_conditions_1a', 'eq:obs13_born_probabilities_1a', 'eq:obs13_luders_update_1a', 'eq:obs13_probability_normalization_1a', 'eq:obs13_conditional_state_properties_1a', 'eq:obs13_repeatability_1a', 'eq:obs13_parseval_pvm_1a', 'eq:obs13_synthesis_1a', 'eq:std_obs13_principle_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
