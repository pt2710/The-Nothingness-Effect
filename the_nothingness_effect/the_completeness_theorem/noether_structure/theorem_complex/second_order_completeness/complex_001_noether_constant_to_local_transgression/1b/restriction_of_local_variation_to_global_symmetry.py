'Authoritative theorem title: Restriction of Local Variation to Global Symmetry.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='noether_constant_to_local_transgression',
    role=TheoremRole.LEFT,
    authoritative_title='Restriction of Local Variation to Global Symmetry',
    authoritative_title_tex='Restriction of Local Variation to Global Symmetry',
    equation_labels=(),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
