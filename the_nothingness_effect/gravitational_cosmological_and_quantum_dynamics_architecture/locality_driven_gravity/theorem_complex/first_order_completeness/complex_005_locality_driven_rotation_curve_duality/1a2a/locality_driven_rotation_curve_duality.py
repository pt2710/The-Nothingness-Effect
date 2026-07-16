'Authoritative theorem title: Locality-Driven Rotation Curve Duality.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='locality_driven_rotation_curve_duality',
    role=TheoremRole.CROSS,
    authoritative_title='Locality-Driven Rotation Curve Duality',
    authoritative_title_tex='Locality-Driven Rotation Curve Duality',
    equation_labels=('eq:ldg05_rotation_curve_status_1a2a', 'eq:local_potential_1a2a', 'eq:nonlocal_potential_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
