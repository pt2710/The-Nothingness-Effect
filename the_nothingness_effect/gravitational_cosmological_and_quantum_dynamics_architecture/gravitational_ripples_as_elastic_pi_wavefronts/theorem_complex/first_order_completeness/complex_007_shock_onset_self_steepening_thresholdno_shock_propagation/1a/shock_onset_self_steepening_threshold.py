'Authoritative theorem title: Shock-Onset Self-Steepening Threshold.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='shock_onset_self_steepening_threshold_no_shock_propagation',
    role=TheoremRole.LEFT,
    authoritative_title='Shock-Onset Self-Steepening Threshold',
    authoritative_title_tex='Shock-Onset Self-Steepening Threshold',
    equation_labels=('eq:grw07_shock_threshold_order_parameter_1a', 'eq:grw07_shock_threshold_branch_condition_1a', 'eq:skew_growth_1a', 'eq:width_growth_1a', 'eq:bispectrum_scaling_1a', 'eq:g_eqn_1a', 'eq:gmax_ineq_1a', 'eq:ts_bound_1a', 'eq:superlinear_S_1a', 'eq:Skew_integral_1a', 'eq:finite_ts_1a', 'eq:sep_ode_1a', 'eq:sep_integrated_1a', 'eq:sep_ts_bound_1a', 'eq:leakage_1a', 'eq:leakage_integral_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
