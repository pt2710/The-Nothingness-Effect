'Authoritative theorem title: Environment-Dependent Group Velocity Mapping (1A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='environment_dependent_group_velocity_mapping_uniform_propagation',
    role=TheoremRole.LEFT,
    authoritative_title='Environment-Dependent Group Velocity Mapping',
    authoritative_title_tex='Environment-Dependent Group Velocity Mapping (1A)',
    equation_labels=('eq:grw09_group_velocity_order_parameter_1a', 'eq:grw09_group_velocity_branch_condition_1a', 'eq:delta_tau_linear_1a', 'eq:spectral_slope_1a', 'eq:spectral_curvature_1a', 'eq:lemma_linearization_1a', 'eq:lemma_spectral_derivative_1a', 'eq:proof_tau_expansion_1a', 'eq:proof_delta_tau_1a', 'eq:proof_spectral_derivative_1a', 'eq:path_diff_1a', 'eq:path_diff_spectral_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
