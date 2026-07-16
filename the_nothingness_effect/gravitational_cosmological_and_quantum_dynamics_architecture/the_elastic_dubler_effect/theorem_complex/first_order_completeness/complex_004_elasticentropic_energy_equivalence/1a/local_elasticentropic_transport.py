'Authoritative theorem title: Local Elastic--Entropic Transport.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_dubler_effect::elastic_entropic_energy_equivalence',
    role=TheoremRole.LEFT,
    authoritative_title='Local Elastic–Entropic Transport',
    authoritative_title_tex='Local Elastic--Entropic Transport',
    equation_labels=('eq:ed04_control_volume_1a', 'eq:ed04_current_gradient_equiv_1a', 'eq:ed04_dissipation_pairing_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
