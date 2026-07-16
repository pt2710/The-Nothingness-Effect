'Authoritative theorem title: Flowpoint Boundary Mode Conversion $\\leftrightarrow$ Pure-Mode Propagation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='flowpoint_boundary_mode_conversion_pure_mode_propagation',
    role=TheoremRole.CROSS,
    authoritative_title='Flowpoint Boundary Mode Conversion <-> Pure-Mode Propagation',
    authoritative_title_tex='Flowpoint Boundary Mode Conversion $\\leftrightarrow$ Pure-Mode Propagation',
    equation_labels=('eq:grw06_mode_conversion_status_1a2a', 'eq:flowpoint_evolution_1a2a', 'eq:flowpoint_conversion_operator_1a2a', 'eq:pure_mode_limit_1a2a', 'eq:born_amplitude_1a2a', 'eq:conversion_probability_1a2a', 'eq:dual_diagnostic_1a2a', 'eq:angular_integral_1a2a', 'eq:switching_kernel_1a2a', 'eq:gate_derivative_1a2a', 'eq:global_discriminant_1a2a', 'eq:disc_derivative_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
