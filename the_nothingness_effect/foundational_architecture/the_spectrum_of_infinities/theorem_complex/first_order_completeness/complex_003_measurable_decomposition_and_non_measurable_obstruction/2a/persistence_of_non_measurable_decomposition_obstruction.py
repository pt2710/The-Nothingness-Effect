'Authoritative theorem title: Persistence of Non-Measurable Decomposition Obstruction.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='measurable_decomposition_and_non_measurable_obstruction',
    role=TheoremRole.RIGHT,
    authoritative_title='Persistence of Non-Measurable Decomposition Obstruction',
    authoritative_title_tex='Persistence of Non-Measurable Decomposition Obstruction',
    equation_labels=('eq:std_soi_measure_domain_2a',),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
