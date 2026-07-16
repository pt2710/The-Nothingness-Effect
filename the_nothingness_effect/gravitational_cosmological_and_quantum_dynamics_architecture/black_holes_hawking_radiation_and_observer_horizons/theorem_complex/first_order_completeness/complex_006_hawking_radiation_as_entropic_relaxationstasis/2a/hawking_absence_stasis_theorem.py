'Authoritative theorem title: Hawking Absence/Stasis Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='hawking_radiation_as_entropic_relaxation_stasis',
    role=TheoremRole.RIGHT,
    authoritative_title='Hawking Absence/Stasis Theorem',
    authoritative_title_tex='Hawking Absence/Stasis Theorem',
    equation_labels=('eq:bhhr06_hawking_relaxation_order_parameter_2a', 'eq:bhhr06_hawking_relaxation_branch_condition_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
