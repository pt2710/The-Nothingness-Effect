'Authoritative theorem title: Vanishing Preferred Transport Direction.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='causality_via_elastic_dubler_e_and_causal_symmetry',
    role=TheoremRole.RIGHT,
    authoritative_title='Vanishing Preferred Transport Direction',
    authoritative_title_tex='Vanishing Preferred Transport Direction',
    equation_labels=('eq:ed12_zero_current_2a',),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
