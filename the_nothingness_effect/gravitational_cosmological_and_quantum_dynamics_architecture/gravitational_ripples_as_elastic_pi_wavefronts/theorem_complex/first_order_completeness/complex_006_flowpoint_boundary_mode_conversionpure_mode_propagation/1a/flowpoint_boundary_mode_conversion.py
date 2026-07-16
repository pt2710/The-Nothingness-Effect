'Authoritative theorem title: Flowpoint Boundary Mode Conversion.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='flowpoint_boundary_mode_conversion_pure_mode_propagation',
    role=TheoremRole.LEFT,
    authoritative_title='Flowpoint Boundary Mode Conversion',
    authoritative_title_tex='Flowpoint Boundary Mode Conversion',
    equation_labels=('eq:grw06_mode_conversion_order_parameter_1a', 'eq:grw06_mode_conversion_branch_condition_1a', 'eq:scattering_matrix_1a', 'eq:conversion_coefficients_1a', 'eq:power_balance_1a', 'eq:mode_power_rate_1a', 'eq:monotonicity_probability_1a', 'eq:monotonicity_derivative_1a', 'eq:dyson_series_1a', 'eq:nonzero_Sji_1a', 'eq:two_mode_system_1a', 'eq:polarization_arcs_1a', 'eq:arc_derivative_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
