'Authoritative theorem title: Conserved GR Tilt (2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='stochastic_background_tilt_n_e_standard_gr_tilt_n_t',
    role=TheoremRole.RIGHT,
    authoritative_title='Conserved GR Tilt',
    authoritative_title_tex='Conserved GR Tilt (2A)',
    equation_labels=('eq:grw08_stochastic_tilt_order_parameter_2a', 'eq:grw08_stochastic_tilt_branch_condition_2a', 'eq:transfer_identity_2a', 'eq:delta_n_zero_2a', 'eq:tilt_running_zero_2a', 'eq:gr_limit_transfer_2a', 'eq:gr_limit_slope_2a', 'eq:proof_tilt_equal_2a', 'eq:calc_running_zero_from_T_one_2a', 'eq:calc_constant_diff_zero_2a', 'eq:null_offset_direct_2a', 'eq:null_offset_running_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
