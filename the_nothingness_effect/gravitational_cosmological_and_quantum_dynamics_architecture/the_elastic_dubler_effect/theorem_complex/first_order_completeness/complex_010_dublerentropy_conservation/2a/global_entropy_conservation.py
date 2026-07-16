'Authoritative theorem title: Global Entropy Conservation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dubler_entropy_conservation',
    role=TheoremRole.RIGHT,
    authoritative_title='Global Entropy Conservation',
    authoritative_title_tex='Global Entropy Conservation',
    equation_labels=('eq:ed10_closed_boundary_2a', 'eq:ed10_global_conservation_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
