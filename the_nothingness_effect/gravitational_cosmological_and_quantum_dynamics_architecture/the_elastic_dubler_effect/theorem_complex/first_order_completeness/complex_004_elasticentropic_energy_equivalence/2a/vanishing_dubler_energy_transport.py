'Authoritative theorem title: Vanishing Dubler Energy Transport.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_dubler_effect::elastic_entropic_energy_equivalence',
    role=TheoremRole.RIGHT,
    authoritative_title='Vanishing Dubler Energy Transport',
    authoritative_title_tex='Vanishing Dubler Energy Transport',
    equation_labels=('eq:ed04_equilibrium_2a',),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
