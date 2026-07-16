'Authoritative theorem title: Local Dubler Redistribution.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dubler_entropy_conservation',
    role=TheoremRole.LEFT,
    authoritative_title='Local Dubler Redistribution',
    authoritative_title_tex='Local Dubler Redistribution',
    equation_labels=('eq:ed10_continuity_1a', 'eq:ed10_local_balance_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
