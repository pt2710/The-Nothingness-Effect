'Authoritative theorem title: Locality-Driven Rotation Curve Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='locality_driven_rotation_curve_duality',
    role=TheoremRole.LEFT,
    authoritative_title='Locality-Driven Rotation Curve Theorem',
    authoritative_title_tex='Locality-Driven Rotation Curve Theorem',
    equation_labels=('eq:ldg05_rotation_curve_order_parameter_1a', 'eq:ldg05_rotation_curve_branch_condition_1a', 'eq:rotation_local_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
