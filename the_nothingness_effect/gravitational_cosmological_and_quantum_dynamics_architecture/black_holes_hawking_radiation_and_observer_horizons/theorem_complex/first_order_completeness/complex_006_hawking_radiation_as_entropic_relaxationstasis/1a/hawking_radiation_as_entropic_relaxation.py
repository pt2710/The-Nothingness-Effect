'Authoritative theorem title: Hawking Radiation as Entropic Relaxation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='hawking_radiation_as_entropic_relaxation_stasis',
    role=TheoremRole.LEFT,
    authoritative_title='Hawking Radiation as Entropic Relaxation',
    authoritative_title_tex='Hawking Radiation as Entropic Relaxation',
    equation_labels=('eq:bhhr06_hawking_relaxation_order_parameter_1a', 'eq:bhhr06_hawking_relaxation_branch_condition_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
