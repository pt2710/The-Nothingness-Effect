'Authoritative theorem title: Finite Elasticity Gives Finite Sensitivity.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='universal_elasticity_constant_k_d',
    role=TheoremRole.LEFT,
    authoritative_title='Finite Elasticity Gives Finite Sensitivity',
    authoritative_title_tex='Finite Elasticity Gives Finite Sensitivity',
    equation_labels=('eq:ed07_response_family_1a', 'eq:ed07_sensitivity_1a', 'eq:ed07_nonzero_drive_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
