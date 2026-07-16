'Authoritative theorem title: No-Shock Propagation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='shock_onset_self_steepening_threshold_no_shock_propagation',
    role=TheoremRole.RIGHT,
    authoritative_title='No-Shock Propagation',
    authoritative_title_tex='No-Shock Propagation',
    equation_labels=('eq:grw07_shock_threshold_order_parameter_2a', 'eq:grw07_shock_threshold_branch_condition_2a', 'eq:skew_width_bounds_2a', 'eq:g_bound_2a', 'eq:g_tanh_2a', 'eq:energy_decay_2a', 'eq:E_decay_integral_2a', 'eq:g_exact_2a', 'eq:gmax_ineq_raw_2a', 'eq:gmax_delta_beta_2a', 'eq:delta_beta_defs_2a', 'eq:logistic_comp_2a', 'eq:int_logistic_2a', 'eq:comparison_solution_2a', 'eq:W_bound_2a', 'eq:W_growth_bound_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
