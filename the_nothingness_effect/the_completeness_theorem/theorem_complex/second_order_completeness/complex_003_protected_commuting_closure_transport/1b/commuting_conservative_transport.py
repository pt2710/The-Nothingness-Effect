'Authoritative theorem title: Commuting Conservative Transport.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='protected_commuting_closure_transport',
    role=TheoremRole.LEFT,
    authoritative_title='Commuting Conservative Transport',
    authoritative_title_tex='Commuting Conservative Transport',
    equation_labels=(),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
