'Authoritative theorem title: Measure-Preserving Decomposition under SOI Normalization.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='measurable_decomposition_and_non_measurable_obstruction',
    role=TheoremRole.LEFT,
    authoritative_title='Measure-Preserving Decomposition under SOI Normalization',
    authoritative_title_tex='Measure-Preserving Decomposition under SOI Normalization',
    equation_labels=('eq:soi_measurable_absolute_decomposition_1a', 'eq:std_soi_measurable_conservation_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
