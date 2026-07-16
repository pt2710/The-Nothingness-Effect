'Authoritative theorem title: Projection Breakdown and State Ambiguity.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='definite_state_projection_and_state_ambiguity',
    role=TheoremRole.RIGHT,
    authoritative_title='Projection Breakdown and State Ambiguity',
    authoritative_title_tex='Projection Breakdown and State Ambiguity',
    equation_labels=('eq:obs13_povm_conditions_2a', 'eq:obs13_povm_probabilities_2a', 'eq:obs13_coin_povm_2a', 'eq:obs13_prepare_instrument_2a', 'eq:obs13_same_probabilities_2a', 'eq:obs13_synthesis_2a', 'eq:std_obs13_principle_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
