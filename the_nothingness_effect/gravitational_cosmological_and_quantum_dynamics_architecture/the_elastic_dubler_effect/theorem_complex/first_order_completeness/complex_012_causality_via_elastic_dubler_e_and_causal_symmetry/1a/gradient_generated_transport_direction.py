'Authoritative theorem title: Gradient-Generated Transport Direction.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='causality_via_elastic_dubler_e_and_causal_symmetry',
    role=TheoremRole.LEFT,
    authoritative_title='Gradient-Generated Transport Direction',
    authoritative_title_tex='Gradient-Generated Transport Direction',
    equation_labels=('eq:ed12_direction_1a', 'eq:ed12_entropy_rate_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
