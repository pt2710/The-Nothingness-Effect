'Authoritative theorem title: Environment-Dependent Group Velocity Mapping $\\leftrightarrow$ Uniform Propagation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='environment_dependent_group_velocity_mapping_uniform_propagation',
    role=TheoremRole.CROSS,
    authoritative_title='Environment-Dependent Group Velocity Mapping <-> Uniform Propagation',
    authoritative_title_tex='Environment-Dependent Group Velocity Mapping $\\leftrightarrow$ Uniform Propagation',
    equation_labels=('eq:grw09_group_velocity_status_1a2a', 'eq:group_delay_def_1a2a', 'eq:delta_tau_linear_1a2a', 'eq:spectral_corrugation_1a2a', 'eq:path_gradient_1a2a', 'eq:dual_representation_1a2a', 'eq:dual_representation_spectral_1a2a', 'eq:dual_core_identity_1a2a', 'eq:dual_core_spectral_1a2a', 'eq:inference_or_bound_1a2a', 'eq:inference_or_bound_spectral_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
