'Authoritative theorem title: Nonlocal Rotation Ambiguity Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='locality_driven_rotation_curve_duality',
    role=TheoremRole.RIGHT,
    authoritative_title='Nonlocal Rotation Ambiguity Theorem',
    authoritative_title_tex='Nonlocal Rotation Ambiguity Theorem',
    equation_labels=('eq:ldg05_rotation_curve_order_parameter_2a', 'eq:ldg05_rotation_curve_branch_condition_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
