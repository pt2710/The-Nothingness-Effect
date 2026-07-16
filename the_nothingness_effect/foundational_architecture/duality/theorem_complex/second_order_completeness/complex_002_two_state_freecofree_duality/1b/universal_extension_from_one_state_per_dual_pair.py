'Authoritative theorem title: Universal Extension from One State per Dual Pair.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='two_state_free_cofree_duality',
    role=TheoremRole.LEFT,
    authoritative_title='Universal Extension from One State per Dual Pair',
    authoritative_title_tex='Universal Extension from One State per Dual Pair',
    equation_labels=('eq:drv_duality_b02_1b', 'eq:drv_duality_b02_theorem_1b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
