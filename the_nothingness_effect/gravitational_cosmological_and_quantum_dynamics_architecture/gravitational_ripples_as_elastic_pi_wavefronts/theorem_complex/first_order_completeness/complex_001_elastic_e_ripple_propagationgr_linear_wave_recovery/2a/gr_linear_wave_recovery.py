'Authoritative theorem title: GR Linear-Wave Recovery.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_e_ripple_propagation_gr_linear_wave_recovery',
    role=TheoremRole.RIGHT,
    authoritative_title='GR Linear-Wave Recovery',
    authoritative_title_tex='GR Linear-Wave Recovery',
    equation_labels=('eq:grw01_ripple_propagation_order_parameter_2a', 'eq:grw01_ripple_propagation_branch_condition_2a', 'eq:def_state_2a', 'eq:pde_2a', 'eq:dispersion_2a', 'eq:energy_2a', 'eq:energy_const_2a', 'eq:gr_bounds_2a', 'eq:eps_vec_2a', 'eq:pde_eps_2a', 'eq:uniform_bounds_2a', 'eq:weak_limit_2a', 'eq:residual_2a', 'eq:residual_to_zero_2a', 'eq:weak_limit_eq_2a', 'eq:proof_energy_gr_2a', 'eq:bounds_2a', 'eq:gr_obs_relations_2a', 'eq:post_concentration_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
