'Authoritative theorem title: Uniform Propagation (2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='environment_dependent_group_velocity_mapping_uniform_propagation',
    role=TheoremRole.RIGHT,
    authoritative_title='Uniform Propagation',
    authoritative_title_tex='Uniform Propagation (2A)',
    equation_labels=('eq:grw09_group_velocity_order_parameter_2a', 'eq:grw09_group_velocity_branch_condition_2a', 'eq:delta_tau_zero_2a', 'eq:delta_tau_zero_derivatives_2a', 'eq:uniform_zero_residual_2a', 'eq:uniform_zero_derivatives_2a', 'eq:proof_uniform_2a', 'eq:proof_uniform_derivatives_2a', 'eq:bound_integral_2a', 'eq:bound_spectral_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
