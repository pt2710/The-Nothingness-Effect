'Authoritative theorem title: Shock-Onset Self-Steepening Threshold $\\leftrightarrow$ No-Shock Propagation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='shock_onset_self_steepening_threshold_no_shock_propagation',
    role=TheoremRole.CROSS,
    authoritative_title='Shock-Onset Self-Steepening Threshold <-> No-Shock Propagation',
    authoritative_title_tex='Shock-Onset Self-Steepening Threshold $\\leftrightarrow$ No-Shock Propagation',
    equation_labels=('eq:grw07_shock_threshold_status_1a2a', 'eq:governing_shock_1a2a', 'eq:rates_shock_1a2a', 'eq:threshold_shock_1a2a', 'eq:threshold_freq_shock_1a2a', 'eq:char_X_1a2a', 'eq:char_pi_1a2a', 'eq:gradient_blowup_1a2a', 'eq:shock_time_1a2a', 'eq:I_II_equiv_1a2a', 'eq:sign_partition_1a2a', 'eq:ts_partition_1a2a', 'eq:template_switch_1a2a', 'eq:mismatch_rate_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
