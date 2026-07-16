'Authoritative theorem title: Universal Dual-State Observation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='two_state_free_cofree_duality',
    role=TheoremRole.RIGHT,
    authoritative_title='Universal Dual-State Observation',
    authoritative_title_tex='Universal Dual-State Observation',
    equation_labels=('eq:drv_duality_b02_2b', 'eq:drv_duality_b02_theorem_2b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
