'Authoritative theorem title: Definite-State versus Ambiguous-Update Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='definite_state_projection_and_state_ambiguity',
    role=TheoremRole.CROSS,
    authoritative_title='Definite-State versus Ambiguous-Update Classification',
    authoritative_title_tex='Definite-State versus Ambiguous-Update Classification',
    equation_labels=('eq:obs13_canonical_observation_collapse_1a2a', 'eq:obs13_joint_tuple_1a2a', 'eq:obs13_instrument_consistency_1a2a', 'eq:obs13_general_conditional_state_1a2a', 'eq:obs13_luders_channel_1a2a', 'eq:obs13_joint_instrument_chain_1a2a', 'eq:std_obs13_principle_joint'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
