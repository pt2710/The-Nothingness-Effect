'Authoritative theorem title: Global Entropic Flowpoint-Phase Symmetry.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='global_symmetry_and_kd_charge_conservation',
    role=TheoremRole.LEFT,
    authoritative_title='Global Entropic Flowpoint-Phase Symmetry',
    authoritative_title_tex='Global Entropic Flowpoint-Phase Symmetry',
    equation_labels=('eq:noether_global_predicate_1a', 'eq:noether_global_symmetry_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
