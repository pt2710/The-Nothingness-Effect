'Authoritative theorem title: Operational Transport Tilt (1A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='stochastic_background_tilt_n_e_standard_gr_tilt_n_t',
    role=TheoremRole.LEFT,
    authoritative_title='Operational Transport Tilt',
    authoritative_title_tex='Operational Transport Tilt (1A)',
    equation_labels=('eq:grw08_stochastic_tilt_order_parameter_1a', 'eq:grw08_stochastic_tilt_branch_condition_1a', 'eq:nonzero_delta_n_interval_1a', 'eq:transfer_reconstruct_1a', 'eq:tilt_running_1a', 'eq:series_running_1a', 'eq:tilt_diff_lemma_1a', 'eq:tilt_running_lemma_1a', 'eq:proof_nonzero_delta_n_1a', 'eq:calc_chain_rule_expansion_1a', 'eq:calc_delta_n_from_chain_1a', 'eq:cor_transfer_int_1a', 'eq:cor_transfer_solution_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
