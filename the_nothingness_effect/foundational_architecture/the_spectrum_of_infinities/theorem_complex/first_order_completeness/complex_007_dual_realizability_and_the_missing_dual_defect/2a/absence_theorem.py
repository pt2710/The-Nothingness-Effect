'Authoritative theorem title: Absence Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dual_realizability_and_the_missing_dual_defect',
    role=TheoremRole.RIGHT,
    authoritative_title='Absence Theorem',
    authoritative_title_tex='Absence Theorem',
    equation_labels=('eq:std_soi_missing_coordinate_2a',),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
