'Authoritative theorem title: Pure-Mode Propagation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='flowpoint_boundary_mode_conversion_pure_mode_propagation',
    role=TheoremRole.RIGHT,
    authoritative_title='Pure-Mode Propagation',
    authoritative_title_tex='Pure-Mode Propagation',
    equation_labels=('eq:grw06_mode_conversion_order_parameter_2a', 'eq:grw06_mode_conversion_branch_condition_2a', 'eq:pure_mode_power_constancy_2a', 'eq:diagonal_S_2a', 'eq:two_mode_constancy_2a', 'eq:proof_diagonal_2a', 'eq:zero_amplitude_2a', 'eq:discriminant_2a', 'eq:disc_constancy_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
