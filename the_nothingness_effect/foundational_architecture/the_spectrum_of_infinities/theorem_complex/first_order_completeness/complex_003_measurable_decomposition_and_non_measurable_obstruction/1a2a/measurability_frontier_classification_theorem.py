'Authoritative theorem title: Measurability Frontier Classification Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='measurable_decomposition_and_non_measurable_obstruction',
    role=TheoremRole.CROSS,
    authoritative_title='Measurability Frontier Classification Theorem',
    authoritative_title_tex='Measurability Frontier Classification Theorem',
    equation_labels=('eq:soi_measurable_original_soi_1a2a', 'eq:soi_measurable_measure_scaling_1a2a', 'eq:soi_measurable_pushforward_pair_1a2a', 'eq:std_soi_meas_frontier_joint', 'eq:soi_measurable_absolute_scale_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
